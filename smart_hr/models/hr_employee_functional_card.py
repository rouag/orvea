# -*- coding: utf-8 -*-


from openerp import models, fields, api, _



class HrEmployeeFunctionnalCard(models.Model):
    _name = 'hr.employee.functionnal.card'
    _description = u'بطاقة موظف' 
    
    name=fields.Char(string='رقم بطاقة')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1)
    number = fields.Char(string=u'الرقم الوظيفي', related="employee_id.number")
    employee_state = fields.Selection(string=u'الحالة', related="employee_id.employee_state")
    last_salary = fields.Float(string='  الراتب الأخير ', store=True,compute='_compute_last_degree_salary') 
    birthday_location = fields.Char(string=u'مكان الميلاد', related="employee_id.birthday_location")
    birthday = fields.Date(string=u'تاريخ الميلاد',related="employee_id.birthday")
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة',compute='_compute_last_degree_salary')
    identification_id  =fields.Char(string=u'رقم الهوية',related="employee_id.identification_id")
    passport_id = fields.Char(string=u'رقم جواز السفر',related="employee_id.passport_id")
    join_date = fields.Date(string=u'تاريخ الالتحاق بالجهة', related="employee_id.join_date")
    begin_work_date = fields.Date(string=u' تاريخ بداية العمل الحكومي' , related="employee_id.begin_work_date")
    specialization_ids = fields.Many2many('hr.employee.specialization', string=u'الاختصاص',related="employee_id.specialization_ids")
    education_level = fields.Many2one('hr.employee.education.level', string=u'المستوى التعليمي', related="employee_id.education_level")
    history_ids = fields.One2many('hr.employee.history', 'employee_id', string=u'سجل الاجراءات',related="employee_id.history_ids")
    emp_name = fields.Char(string=u'إسم الموظف', relates="employee_id.name")
    emp_age = fields.Char(string=u'السن', relates="employee_id.age")
    department_id = fields.Many2one('hr.department', string=u'مكان العمل', related="employee_id.department_id")
    passport_date = fields.Date(string=u'تاريخ إصدار جواز السفر ',related='employee_id.passport_date')
    passport_place = fields.Char(string=u'مكان إصدار بجواز السفر', related='employee_id.passport_place')
    @api.one
    @api.depends('employee_id')
    def _compute_last_degree_salary(self):
        last_decision_appoint =self.env['hr.decision.appoint'].search([('employee_id','=',self.employee_id.id),('state_appoint','=','active')],limit=1)
        if last_decision_appoint:
            self.last_salary = last_decision_appoint.basic_salary
            self.degree_id = last_decision_appoint.degree_id.id

    @api.model
    def create(self, vals):
        res = super(HrEmployeeFunctionnalCard, self).create(vals)
        vals['name'] = self.env['ir.sequence'].get('hr.employye.card.seq')
        res.write(vals)
        return res
    
    
class HrEmployeeIssuingFunctionnalCard(models.Model):
    _name = 'hr.employee.issuing.functionnal.card'
    _description = u'اصدار بطاقة موظف' 

    employee_ids = fields.Many2many('hr.employee', string=u'الموظف', required=1)    
    date = fields.Date(string=u'التاريخ ', default=fields.Datetime.now(), readonly=1)
    expiration_date = fields.Date(string=u'تاريخ إنتهاء الصلاحية  ')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('hrm', u'مدير شؤون الموظفين'),
       ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
 ], string=u'حالة', default='draft', advanced_search=True)


    @api.multi
    def button_accept_hrm(self):
        self.ensure_one()
        for emp in self.employee_ids:
            self.env['hr.employee.functionnal.card'].create({'employee_id': emp.id,})
        self.state = 'done'

    @api.multi
    def button_send_request(self):
        self.ensure_one()
        self.state = 'hrm'

    @api.multi
    def button_refuse_hrm(self):
        self.ensure_one()
        self.state = 'refuse'

