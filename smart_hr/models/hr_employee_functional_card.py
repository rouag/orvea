# -*- coding: utf-8 -*-


from openerp import models, fields, api, _



class HrEmployeeFunctionnalCard(models.Model):
    _name = 'hr.employee.functionnal.card'
    _description = u'بطاقة موظف' 

    name=fields.Char(string='رقم بطاقة')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1, readonly=1)
    number = fields.Char(string=u'الرقم الوظيفي', related="employee_id.number", readonly=1)
    employee_state = fields.Selection(string=u'الحالة', related="employee_id.employee_state", readonly=1)
    last_salary = fields.Float(string='  الراتب الأخير ', store=True,compute='_compute_last_degree_salary', readonly=1) 
    birthday_location = fields.Char(string=u'مكان الميلاد', related="employee_id.birthday_location", readonly=1)
    birthday = fields.Date(string=u'تاريخ الميلاد',related="employee_id.birthday", readonly=1)
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة',compute='_compute_last_degree_salary', readonly=1)
    identification_id  =fields.Char(string=u'رقم الهوية',related="employee_id.identification_id", readonly=1)
    passport_id = fields.Char(string=u'رقم جواز السفر',related="employee_id.passport_id", readonly=1)
    join_date = fields.Date(string=u'تاريخ الالتحاق بالجهة', related="employee_id.join_date", readonly=1)
    begin_work_date = fields.Date(string=u' تاريخ بداية العمل الحكومي' , related="employee_id.begin_work_date", readonly=1)
    specialization_ids = fields.Many2many('hr.employee.specialization', string=u'التخصص',related="employee_id.specialization_ids", readonly=1)
    education_level = fields.Many2one('hr.employee.education.level', string=u'المستوى التعليمي', readonly=1)
    history_ids = fields.One2many('hr.employee.history', 'employee_id', string=u'سجل الاجراءات',related="employee_id.history_ids", readonly=1)
    emp_name = fields.Char(string=u'إسم الموظف', related="employee_id.display_name", readonly=1)
    emp_age = fields.Integer(string=u'السن', related="employee_id.age", readonly=1)
    department_id = fields.Many2one('hr.department', string=u'مكان العمل', related="employee_id.department_id", readonly=1)
    passport_date = fields.Date(string=u'تاريخ إصدار جواز السفر ',related='employee_id.passport_date', readonly=1)
    passport_place = fields.Char(string=u'مكان إصدار جواز السفر', related='employee_id.passport_place', readonly=1)
    date = fields.Date(string=u'التاريخ ', default=fields.Datetime.now(), readonly=1)
    expiration_date = fields.Date(string=u'تاريخ إنتهاء الصلاحية  ')
    state = fields.Selection([('draft', u'طلب'),
                              ('hrm', u'مدير شؤون الموظفين'),
                              ('done', u'اعتمدت'),
                              ('refuse', u'رفض'),
                              ], string=u'الحالة', default='draft', advanced_search=True)
    training_ids = fields.One2many('hr.candidates', 'employee_id', string=u'التدريب', readonly=1)

    @api.one
    @api.depends('employee_id')
    def _compute_last_degree_salary(self):
        last_decision_appoint = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id), ('state_appoint','=', 'active')], limit=1)
        if last_decision_appoint:
            self.last_salary = last_decision_appoint.basic_salary
            self.degree_id = last_decision_appoint.degree_id.id

    @api.model
    def create(self, vals):
        res = super(HrEmployeeFunctionnalCard, self).create(vals)
        vals['name'] = self.env['ir.sequence'].get('hr.employye.card.seq')
        res.write(vals)
        return res

    @api.multi
    def button_accept_hrm(self):
        self.ensure_one()
        self.state = 'done'

    @api.multi
    def button_send_request(self):
        self.ensure_one()
        self.state = 'hrm'

    @api.multi
    def button_refuse_hrm(self):
        self.ensure_one()
        self.state = 'refuse'
