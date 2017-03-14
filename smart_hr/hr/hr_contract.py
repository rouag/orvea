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
    country_id = fields.Many2one(related='employee_id.country_id', store=True, readonly=True, string='الجنسية')
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

    assurance = fields.Char(string='التامين')
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

    @api.onchange('state')
    def _onchange_state(self):
        if self.state == 'open':
            self.date_contract_to = fields.Datetime.now()

    @api.onchange('employee_id')
    def _onchange_employe(self):
        if self.employee_id:
            employee_line = self.env['hr.decision.appoint'].search(
                [('employee_id', '=', self.employee_id.id), ('is_started', '=', True)], limit=1)
            if employee_line:
                self.job_id = employee_line.job_id.id
                self.type_job_id = employee_line.type_id.id
                self.grade_id = employee_line.grade_id.id
                self.degree_id = employee_line.degree_id.id
                self.transport_allow = employee_line.transport_allow
                self.retirement = employee_line.retirement
                self.net_salary = employee_line.net_salary
                if self.employee_id.basic_salary == 0:
                    self.basic_salary = employee_line.basic_salary
            if self.employee_id.basic_salary > 0:
                self.basic_salary = self.employee_id.basic_salary

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
                                                  'notif': True
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
