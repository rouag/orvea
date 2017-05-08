# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrContract(models.Model):
    _inherit = 'hr.contract'

    employee_id = fields.Many2one('hr.employee', string=' الموظف ', required=1)
    country_id = fields.Char(readonly=True,string="الجنسية")
    identification_id = fields.Char(related='employee_id.identification_id', store=True, readonly=True,
                                    string=u'رقم الهوية')
    identification_date = fields.Date(related='employee_id.identification_date', store=True, readonly=True,
                                      string=u'تاريخ إصدار بطاقة الهوية')
    identification_place = fields.Many2one(related='employee_id.identification_place', store=True, readonly=True,
                                           string=u'مكان إصدار بطاقة الهوية')
    calendar_id = fields.Many2one(related='employee_id.calendar_id', store=True, readonly=True, string=u'وردية العمل')
    passport_id = fields.Char(related='employee_id.passport_id', store=True, readonly=True, string=u'رقم الحفيظة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True, string='الادارة', )
    job_id = fields.Many2one('hr.job', string='المسمى الوظيفي', store=True, readonly=1)

    assurance = fields.Char(string='التامين',readonly=True)
    type_job_id = fields.Many2one('salary.grid.type', string='الصنف', store=True, readonly=1)
    # type_id=fields.Many2one('salary.grid.type',string='الصنف',store=True,  readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', store=True, readonly=1)
    struct_id = fields.Many2one('hr.payroll.structure', 'Salary Structure', required=False)
    # struct_id= fields.Char(string="struct",required=0,),
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', store=True, readonly=True)
    payement_emploi = fields.Many2one('hr.contract.payement', string='الدفع المجدول')
    date_to = fields.Date(string=u' من', )
    date_endd = fields.Date(string=u'إلى', )
    date_contract_to = fields.Date(string=u'من', )
    date_contract_end = fields.Date(string=u'إلى', )
    basic_salary = fields.Float(string='الراتب الأساسي', store=True, readonly=True)
    transport_allow = fields.Float(string='بدل النقل', store=True, readonly=True)
    retirement = fields.Float(string='المحسوم للتقاعد', store=True, readonly=True)
    net_salary = fields.Float(string='صافي الراتب', store=True, readonly=True)
    contract_item_ids = fields.Many2many('hr.contract.item', string=u'بند العقد')

    employee_id1 = fields.Many2one('hr.employee', string='المسؤول على العقد', required=1)
    job_id1 = fields.Many2one(related='employee_id1.job_id', store=True, readonly=True)
    employee_id2 = fields.Many2one('hr.employee', string='مراجع البيانات', required=1)
    job_id2 = fields.Many2one(related='employee_id2.job_id', store=True, readonly=True, )
    department_id1 = fields.Many2one(related='employee_id1.department_id', store=True, readonly=True, string='الادارة')
    department_id2 = fields.Many2one(related='employee_id2.department_id', store=True, readonly=True, string='الادارة')
    renewable = fields.Boolean(string='قابل للتجديد')
    ticket_travel = fields.Boolean(string='تذاكر السفر')
    ticket_famely = fields.Boolean(string='تذكرة سفر عائلية')
   # is_saudian = fields.Boolean(string='is saudian', compute='_compute_is_saudian')
    

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft' :
                raise ValidationError(u'لا يمكن حذف العقد فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(HrContract, self).unlink()



    @api.onchange('state')
    def _onchange_state(self):
        if self.state == 'open':
            self.date_contract_to = fields.Datetime.now()

    @api.onchange('employee_id')
    def _onchange_employe(self):
        if self.employee_id:
            employee_line = self.env['hr.employee'].search(
                [('id', '=', self.employee_id.id)], limit=1)
            if employee_line:
                self.job_id = employee_line.job_id.id
                self.type_job_id = employee_line.type_id.id
                self.grade_id = employee_line.grade_id.id
                self.country_id = employee_line.country_id.national
                self.degree_id = employee_line.degree_id.id
                basic_salary = 0.0
                grid_domain= [('grid_id.state', '=','done'),
                         ('grid_id.enabled', '=', True),
                         ('type_id', '=', employee_line.type_id.id),
                         ('grade_id', '=', employee_line.grade_id.id),
                         ('degree_id', '=', employee_line.degree_id.id)]
                salary_grid_detail_id = self.env['salary.grid.detail'].search(grid_domain, order='date desc', limit=1)
                if salary_grid_detail_id:
                    basic_salary = salary_grid_detail_id.basic_salary
                    insurance = salary_grid_detail_id.insurance
                    net_salary = salary_grid_detail_id.net_salary
                    transport_allowance_amout = salary_grid_detail_id.transport_allowance_amout
                    retirement_amount = salary_grid_detail_id.retirement_amount
                    self.basic_salary = basic_salary
                    self.assurance = insurance
                    self.net_salary = net_salary
                    self.transport_allowance_amout = transport_allowance_amout
                    self.retirement = retirement_amount
                
                
                
    @api.multi
    @api.depends('country_id')
    def _compute_is_saudian(self):
        for rec in self:
            if rec.country_id:
                rec.is_saudian = (rec.country_id.code_nat == 'SA')
    @api.model
    def control_contract_employee(self):
        today_date = fields.Date.from_string(fields.Date.today())
        contracts = self.env['hr.contract'].search([('date_contract_end', '=', today_date)])
        for contrat in contracts:
            appoints = self.env['hr.decision.appoint'].search(
                [('employee_id', '=', contrat.employee_id.id), ('state', '=', 'done'), ('is_started', '=', True)],
                limit=1)
            if appoints:
                title = u"' إشعار نهاية العقد'"
                msg = u"' إشعار نهاية العقد'" + unicode(contrat.employee_id.name) + u"'"
                group_id = self.env.ref('smart_hr.group_department_employee')
                self.send_end_contract_group(group_id, title, msg)

    def send_end_contract_group(self, group_id, title, msg):
        '''
        @param group_id: res.groups
        '''
        for recipient in group_id.users:
            self.env['base.notification'].create({'title': title,
                                                  'message': msg,
                                                  'user_id': recipient.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_contract_view',
                                                    'type': 'hr_employee_contract_type',
                                                  })


class HrContractPayement(models.Model):
    _name = 'hr.contract.payement'

    name = fields.Char(string=u'المسمّى')
    periode = fields.Char(string=u'المدة')


class HrContractItem(models.Model):
    _name = 'hr.contract.item'

    name = fields.Char(string=u'مسمى المادة', required=1)
    code = fields.Char(string=u'رقم المادة', required=1)
    text = fields.Html(string=u' محتوى المادة', required=1)
    #   contract_item=fields.Many2one('hr.contract.item',string='بند العقد')
