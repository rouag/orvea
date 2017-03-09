# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class HrImproveSituatim(models.Model):
    _name = 'hr.improve.situation'  
    _inherit = ['mail.thread'] 
    _description=u'تحسين وضع' 
    _rec_name = 'employee_id'

    employee_id=fields.Many2one('hr.employee',string=' إسم الموظف',required=1,)
    number=fields.Char(string='الرقم الموظف',readonly=1)
    state= fields.Selection([('new','طلب'),('waiting','في إنتظار الإعتماد'),('done','اعتمدت')], readonly=1, default='new')
    order_picture=fields.Binary(string='صورة القرار',required=1, attachment=True) 
    order_date=fields.Date(string='تاريخ القرار',required=1) 
    date_hiring=fields.Date(string='تاريخ التعيين',required=1)
    job_id = fields.Many2one('hr.job', string='الوظيفة',readonly=1) 
    number_job=fields.Char(string='الرقم الوظيفي',readonly=1) 
    type_id=fields.Many2one('salary.grid.type',string='الصنف',readonly=1) 
    department_id=fields.Many2one('hr.department',string='الادارة',readonly=1)
    grade_id=fields.Many2one('salary.grid.grade',string='المرتبة',readonly=1)
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', readonly=1)
    far_age = fields.Float(string=' السن الاقصى',readonly=1) 
    basic_salary = fields.Float(string='الراتب الأساسي',readonly=1)   
    transport_allow = fields.Float(string='بدل النقل',readonly=1) 
    retirement = fields.Float(string='المحسوم للتقاعد',readonly=1) 
    net_salary = fields.Float(string='صافي الراتب',readonly=1)
    salary_recent = fields.Float(string=' أخر راتب شهري ',readonly=1)
    transport_alocation = fields.Boolean(string='بدل نقل',readonly=1)
    type_improve=fields.Many2one('hr.type.improve.situation',string='نوع التتحسين',required=1,states={'new': [('readonly', 0)]})
    order_picture1=fields.Binary(string='صورة القرار',required=1, attachment=True) 
    job_id1 = fields.Many2one('hr.job', string='الوظيفة') 
    number_job1=fields.Char(string='الرقم الوظيفي') 
    order_date1=fields.Date(string='تاريخ القرار',required=1) 
    date_hiring1=fields.Date(string='تاريخ التعيين',required=1)
    type_id1=fields.Many2one('salary.grid.type',string='الصنف') 
    department_id1=fields.Many2one('hr.department',string='الادارة')
    grade_id1=fields.Many2one('salary.grid.grade',string='المرتبة')
    degree_id1 = fields.Many2one('salary.grid.degree', string='الدرجة')
    basic_salary1 = fields.Float(string='الراتب الأساسي')   
    net_salary1 = fields.Float(string='صافي الراتب')
    
    @api.one
    def action_waiting(self):
        self.state = 'waiting' 

    @api.multi
    def action_done(self):
        self.ensure_one()
        for line in self:
            improve_val = {

                    'degree_id': line.degree_id1.id,
                    'job_id': line.job_id1.id,
                    'number_job': line.number_job1,
                    'type_id': line.type_id1.id,
                     'basic_salary': line.basic_salary1,
                    'type_improve': line.type_improve.id,
                    'grade_id': line.grade_id1.id,
                    'department_id': line.department_id1.id,
                     }
            self.env['hr.decision.appoint'].search([('employee_id', '=', line.employee_id.id)], limit=1).write  ({
                                    'job_id':line.job_id1.id,
                                     'degree_id': line.degree_id1.id,
                                    'number_job': line.number_job1,
                                    'type_id': line.type_id1.id,
                                    'basic_salary': line.basic_salary1,
                                    'grade_id': line.grade_id1.id,
                                    'department_id': line.department_id1.id,})
        self.state = 'done'
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت إحداث تحسين الوضع جديد '" + unicode(user.name) + u"'")

    @api.one
    def action_refuse(self):
        self.state = 'new'   

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
            if self.employee_id:

                employee_id_line = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id)
                                                ])
                print"employee_id_line",employee_id_line
                if employee_id_line:
                    self.number = employee_id_line.number
                    self.number_job = employee_id_line.number_job
                    self.job_id = employee_id_line.job_id
                    self.order_picture = employee_id_line.order_picture
                    self.type_id = employee_id_line.type_id
                    self.grade_id = employee_id_line.grade_id
                    self.degree_id = employee_id_line.degree_id
                    self.department_id = employee_id_line.department_id
                    self.basic_salary = employee_id_line.basic_salary

    @api.onchange('job_id1')
    def _onchange_job_id1(self):
        if self.job_id1 :
            self.number_job1 = self.job_id1.number
            self.type_id1 = self.job_id1.type_id.id
            self.grade_id1 = self.job_id1.grade_id.id
            self.department_id1 = self.job_id1.department_id.id

class HrTypeImproveSituation(models.Model):
    _name = 'hr.type.improve.situation'
    _description=u'أنواع تحسين الوضع'

    name=fields.Char(string='النوع',required=1 )
    code=fields.Char(string='الرمز')

