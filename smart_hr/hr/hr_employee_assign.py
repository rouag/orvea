# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from mmap import mmap, ACCESS_READ
from xlrd import open_workbook
import os


class HrEmployeeCommissioning(models.Model):
    _name = 'hr.employee.commissioning'
    _inherit = ['mail.thread']
    _description = u'طلب تكليف موظف'
    _rec_name = 'employee_id'

    @api.multi
    def _get_default_company(self):
        return self.env['res.company']._company_default_get('smart_hr').id

    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now(), readonly=1)
    demand_owner_id = fields.Many2one('hr.employee', string='صاحب الطلب',
                                      domain=[('emp_state', 'not in', ['suspended', 'terminated']),
                                              ('employee_state', '=', 'employee')],
                                      default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid),
                                                                                           ('emp_state', 'not in',
                                                                                            ['suspended',
                                                                                             'terminated'])],
                                                                                          limit=1), )
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1, readonly=1,
                                  states={'new': [('readonly', 0)]})
    comm_type = fields.Many2one('hr.employee.commissioning.type', string=u'نوع التكليف', required=1, readonly=1,
                                states={'new': [('readonly', 0)]})
    date_from = fields.Date(string=u'التاريخ من ', default=fields.Datetime.now(), readonly=1,
                            states={'new': [('readonly', 0)]})
    date_to = fields.Date(string=u'التاريخ الى', compute='_compute_date_to', store=True)
    duration = fields.Integer(string=u'الأيام', required=1, readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', u'طلب'),
                              ('pm', u'شؤون الموظفين'),
                              ('accept', u'المكلف'),
                              ('done', u'اعتمدت'),
                              ('refused', u'رفض'),
                              ], readonly=1, default='new', string=u'الحالة')
    governmental_entity = fields.Many2one('res.partner', string=u'الجهة الحكومية',
                                          domain=[('company_type', '=', 'governmental_entity')],
                                          default=_get_default_company, readonly=1, states={'new': [('readonly', 0)]})
    task_ids = fields.One2many('hr.employee.task', 'comm_id', string=u'المهام')
    note = fields.Text(string=u'ملاحظات')
    current_city = fields.Many2one('res.city', string=u'مقر الموظف', related='employee_id.dep_city', required=0)
    city = fields.Many2one('res.city', string=u'مقر التكليف', required=1, readonly=1, states={'new': [('readonly', 0)]})

    decision_number = fields.Char(string=u"رقم القرار", readonly=1)
    decision_date = fields.Date(string=u'تاريخ القرار', readonly=1)

    allowance_transport_rate = fields.Float(string=u'نسبة بدل النقل التي توفرها الجهة')
    salary_rate = fields.Float(string=u'نسبة  الراتب التي توفرها الجهة ')
    give_allow = fields.Boolean(string=u'الجهة توفر بدلات، مكافأة أو تعويضات')

    done_date = fields.Date(string='تاريخ التفعيل')
    commissioning_job_id = fields.Many2one('hr.job', string='الوظيفة المكلف عليها', required=1,
                                           domain=[('state', '=', 'unoccupied')])
    type_id = fields.Many2one('salary.grid.type', string='نوع السلم', related='commissioning_job_id.type_id',
                              readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', related='commissioning_job_id.grade_id',
                               readonly=1)
    decission_id = fields.Many2one('hr.decision', string=u'القرارات')
    commissioning_department_id = fields.Many2one('hr.department', string='الفرع')

    @api.multi
    @api.onchange('comm_type')
    def _onchange_comm_type(self):
        # get list of employee depend on comm_typet
        res = {}
        if self.comm_type:
            grade_ids = self.comm_type.grade_ids.ids
            employee_ids = self.env['hr.employee'].search([('grade_id', 'in', grade_ids)])
            res['domain'] = {'employee_id': [('id', 'in', employee_ids.ids)]}
            return res

    @api.multi
    def open_decission_commissioning(self):
        decision_obj = self.env['hr.decision']
        if self.decission_id:
            decission_id = self.decission_id.id
        else :
            decision_type_id = 1
            decision_date = fields.Date.today() # new date
            if self.employee_id :
                decision_type_id = self.env.ref('smart_hr.data_employee_commissioning').id
            # create decission
            decission_val={
                'name': self.env['ir.sequence'].get('hr.commissioning.seq'),
                'decision_type_id':decision_type_id,
                'date':decision_date,
                'employee_id' :self.employee_id.id }
            decision = decision_obj.create(decission_val)
            decision.text = decision.replace_text(self.employee_id,decision_date,decision_type_id,'commissioning')
            decission_id = decision.id
            self.decission_id =  decission_id
        return {
            'name': _(u'قرار تكليف موظف'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.decision',
            'view_id': self.env.ref('smart_hr.hr_decision_wizard_form').id,
            'type': 'ir.actions.act_window',
            'res_id': decission_id,
            'target': 'new'
            }




    @api.multi
    @api.depends('date_from', 'duration')
    def _compute_date_to(self):
        self.ensure_one()
        if self.date_from and self.duration:
            new_date_to = self.env['hr.smart.utils'].compute_date_to(self.date_from, self.duration - 1)
            self.date_to = new_date_to
        elif self.date_from:
            self.date_to = self.date_from

    @api.multi
    def _get_distance(self, city_code_from, city_code_to):
        self.ensure_one()
        try:
            distances_file = (os.path.dirname(os.path.realpath(__file__)) + '/data/city_distances.xlsx')
            wb = open_workbook(distances_file)
            sheet = wb.sheet_by_name("cities")
            cell = sheet.cell(city_code_from, city_code_to)
            if cell:
                return cell.value
            else:
                raise ValidationError(u"لا يمكن إيجاد المسافة بين المدن.")
        except:
            raise ValidationError(u"لا يمكن إيجاد المسافة بين المدن.")

    @api.multi
    @api.constrains('employee_id')
    def check_constrains(self):
        self.ensure_one()
        hr_config = self.env['hr.setting'].search([], limit=1)
        hr_deputation_setting = self.env['hr.deputation.setting'].search([], limit=1)
        if hr_config:
            # check if there is another commissiong for the employee
            comm_count = self.env['hr.employee.commissioning'].search_count(
                [('state', '=', 'done'), ('employee_id', '=', self.employee_id.id), ('date_to', '>=', self.date_from)])
            if comm_count > 0:
                raise ValidationError(u"لا يمكن إنشاء تكليف قبل إتمام مدة أخر تكليف للموظف.")
            # check assignment periode
            if self.duration <= 0:
                raise ValidationError(u"الرجاء التثبت من المدة.")
            if self.duration > self.comm_type.assign_duration:
                raise ValidationError(u"لا يمكن تجاوز الحد الاقصى للتكليف.")
            if hr_deputation_setting:
                # check distance
                deputation_distance = hr_deputation_setting.deputation_distance
                if self.employee_id.promotion_duration/354 < 1:
                    distance = self._get_distance(int(self.city.code), int(self.employee_id.dep_city.code))
                    if distance >= deputation_distance:
                        raise ValidationError(u"المسافة بين مقر التكليف ومقر الموظف أكبر من مسافة الانتدابات.")

    @api.multi
    def action_new(self):
        self.ensure_one()
        self.state = 'new'

    @api.multi
    def action_pm(self):
        self.ensure_one()
        self.state = 'pm'

    @api.multi
    def action_accept(self):
        self.ensure_one()
        self.state = 'accept'

    @api.multi
    def button_refuse(self):
        self.ensure_one()
        self.state = 'pm'
    
        

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.done_date = fields.Date.today()
        self.employee_id.commissioning_job_id = self.commissioning_job_id
        self.commissioning_job_id.state = 'occupied'
        self.state = 'done'
        # create history_line
    
    @api.multi
    def unlink(self):
        # Validation
        for rec in self:
            if rec.state == 'done':
                raise ValidationError(u'لا يمكن حذف التكليف فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(HrEmployeeCommissioning, self).unlink()

    @api.model
    def control_commissioning_end(self):
        today_date = fields.Date.today()
        commissionings = self.env['hr.employee.commissioning'].search([('state', '=', 'done'), ('date_to', '=', today_date)])
        for line in commissionings:
            title = u"إشعار نهاية تكليف موظف'"
            msg = u"' إشعار نهاية تكليف الموظف'" + unicode(line.employee_id.display_name) + u"'"
            self.env['base.notification'].create({'title': title,
                                                  'message': msg,
                                                  'user_id': line.employee_id.user_id.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_employee_commissioning',
                                                  'notif': True
                                                  })
            self.env['base.notification'].create({'title': title,
                                                  'message': msg,
                                                  'user_id': line.demand_owner_id.user_id.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_employee_commissioning',
                                                  'notif': True
                                                  })

class HrEmployeeCommissioningType(models.Model):
    _name = 'hr.employee.commissioning.type'
    _description = u'نوع التكليف'

    name = fields.Char(string=u'نوع التكليف')
    assign_duration = fields.Integer(string=u'مدة التكليف‬‬ (باليوم)', default=354)
    grade_ids = fields.Many2many('salary.grid.grade', string='المراتب')
