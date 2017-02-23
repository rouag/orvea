# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from mmap import mmap,ACCESS_READ
from xlrd import open_workbook
import os


class HrEmployeeCommissioning(models.Model):
    _name = 'hr.employee.commissioning'
    _description = u'طلب تكليف موظف'
    _rec_name = 'employee_id'

    @api.multi
    def _get_default_company(self):
        return self.env['res.company']._company_default_get('smart_hr').id

    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now(), readonly=1)
    demand_owner_id = fields.Many2one('hr.employee', string='صاحب الطلب', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), required=1, readonly=1)
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1, readonly=1, states={'new': [('readonly', 0)]})
    comm_type = fields.Many2one('hr.employee.commissioning.type', string=u'نوع التكليف', required=1, readonly=1, states={'new': [('readonly', 0)]})
    date_from = fields.Date(string=u'التاريخ من ', default=fields.Datetime.now(), readonly=1, states={'new': [('readonly', 0)]})
    date_to = fields.Date(string=u'التاريخ الى', compute='_compute_date_to', store=True)
    duration = fields.Integer(string=u'الأيام', required=1, readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', u'طلب'),
                              ('pm', u'شؤون الموظفين'),
                              ('accept', u'المكلف'),
                              ('done', u'اعتمدت'),
                              ('refused', u'رفض'),
                              ], readonly=1, default='new', string=u'الحالة')
    governmental_entity = fields.Many2one('res.partner', string=u'الجهة الحكومية', domain=[('company_type', '=', 'governmental_entity')], default=_get_default_company)
    task_ids = fields.One2many('hr.employee.task', 'comm_id', string=u'المهام')
    note = fields.Text(string=u'ملاحظات')
    current_city = fields.Many2one('res.city', string=u'مقر الموظف', related='employee_id.dep_city', required=1)
    city = fields.Many2one('res.city', string=u'مقر التكليف', required=1, readonly=1, states={'new': [('readonly', 0)]})
    decision_number = fields.Char(string=u"رقم القرار", required=1, readonly=1, states={'new': [('readonly', 0)]})
    decision_date = fields.Date(string=u'تاريخ القرار', required=1, readonly=1, states={'new': [('readonly', 0)]})
    decision_file = fields.Binary(string=u'نسخة القرار', required=1, readonly=1, states={'new': [('readonly', 0)]}, attachment=True)
    give_allowance_transport = fields.Boolean(string=u'بدل النقل', default=False)
    give_allow = fields.Boolean(string=u'بدلات، مكافأة أو تعويضات', default=False)
    give_salary = fields.Boolean(string=u'راتب', default=False)

    @api.multi
    @api.depends('date_from', 'duration')
    def _compute_date_to(self):
        self.ensure_one()
        if self.date_from and self.duration:
            new_date_to = self.env['hr.smart.utils'].compute_date_to(self.date_from, self.duration)
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
            comm_count = self.env['hr.employee.commissioning'].search_count([('state', '=', 'done'), ('employee_id', '=', self.employee_id.id), ('date_to', '>=', self.date_from)])
            if comm_count > 0:
                raise ValidationError(u"لا يمكن إنشاء إعارة قبل إتمام مدة أخر إعارة للموظف.")
            # check assignment periode
            if self.duration <= 0:
                raise ValidationError(u"الرجاء التثبت من المدة.")
            if self.duration > hr_config.assign_duration:
                raise ValidationError(u"لا يمكن تجاوز الهاد الاقصى للتكليف.")
            if hr_deputation_setting:
                # check distance
                deputation_distance = hr_deputation_setting.deputation_distance
                if self.employee_id.promotion_duration < 1:
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
    def action_refused(self):
        self.ensure_one()
        self.state = 'pm'

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.state = 'done'
        # create history_line
        self.env['hr.employee.history'].sudo().add_action_line(self.employee_id, False, False, self._description)


class HrEmployeeCommissioningType(models.Model):
    _name = 'hr.employee.commissioning.type'
    _description = u'نوع التكليف'

    name = fields.Char(string=u'نوع التكليف')
