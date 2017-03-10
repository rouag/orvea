# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class hrDirectAppoint(models.Model):
    _name = 'hr.direct.appoint'
    _order = 'id desc'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', required=1)
    number=fields.Char(string='الرقم الوظيفي',readonly=1) 
    code = fields.Char(string=u'رمز الوظيفة ',readonly=1) 
    country_id=fields.Many2one(related='employee_id.country_id', store=True, readonly=True, string='الجنسية')
    job_id  = fields.Many2one('hr.job', string='الوظيفة',store=True,readonly=1) 
    number_job=fields.Char(string='رقم الوظيفة',store=True,readonly=1) 
    type_id=fields.Many2one('salary.grid.type',string='الصنف',store=True,readonly=1) 
    department_id=fields.Many2one('hr.department',string='الادارة',store=True,readonly=1)
    grade_id=fields.Many2one('salary.grid.grade',string='المرتبة',store=True,readonly=1)
    far_age = fields.Float(string=' السن الاقصى',store=True,readonly=1) 
    basic_salary = fields.Float(string='الراتب الأساسي',store=True, readonly=1)   
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة',store=True, readonly=1)
    date_direct_action = fields.Date(string='تاريخ المباشرة المنصوص في التعين ') 
    type_appointment = fields.Many2one('hr.type.appoint',string=u'نوع التعيين' )
    decision_appoint_ids = fields.One2many('hr.decision.appoint', 'employee_id', string=u'تعيينات الموظف')

    date = fields.Date(string=u'تاريخ المباشرة الفعلي', default=fields.Datetime.now())
    state = fields.Selection([('new', '  طلب'),
                             ('waiting', u'في إنتظار المباشرة'),
                             ('done',u'مباشرة'),
                              ('cancel', u'ملغاة')], string='الحالة', readonly=1, default='waiting')

    state_direct = fields.Selection([
                             ('waiting', u'في إنتظار المباشرة'),
                             ('confirm',u'لتأكيد المباشرة '),
                              ('done',u'تم الاجراء'),
                              ('cancel', u'للإلغاء ')], string='الحالة', readonly=1, default='waiting')


    @api.multi
    def action_waiting(self):

        self.state = 'waiting'

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_refuse(self):
        self.state = 'cancel'





    @api.multi
    def button_cancel_appoint(self):
        self.ensure_one() 
        
        appoint_line = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id),('state','=','done'),('is_started','=',False),('state_appoint','=','active')], limit=1)
        print"cancel",appoint_line
        for line in  appoint_line :
            line.write({'is_started': False ,'state_appoint' : 'refuse'})
            title= u"' إشعار بعدم مباشرة التعين'"
            msg= u"' إشعار بعدم مباشرة التعين'"  + unicode(line.employee_id.name) + u"'"
            group_id = self.env.ref('smart_hr.group_department_employee')
            self.send_appoint_group(group_id,title,msg)
        self.state = 'cancel'
        self.state_direct = 'done'  
        
    @api.multi
    def button_direct_appoint(self):
        self.ensure_one()
        #TODO   

        appoint_line = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id),('state','=','done'),('is_started','=',False),('state_appoint','=','active')], limit=1)
        print"appoint_line",appoint_line
        for line in  appoint_line :
            if line.first_appoint == True :
                line.employee_id.write({'begin_work_date': line.date_direct_action, 'recruiter_date': line.date_direct_action})
                line.write({'is_started': True ,'state_appoint' : 'active'})
            else :
                line.write({'is_started': True ,'state_appoint' : 'active'})

            title= u"' إشعار بمباشرة التعين'"
            msg= u"' إشعار بمباشرة التعين'"  + unicode(line.employee_id.display_name) + u"'"
            group_id = self.env.ref('smart_hr.group_department_employee')
            self.send_appoint_group(group_id,title,msg)
        self.state = 'done'
        self.state_direct = 'done'
   
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id :
            self.number = self.employee_id.number
            self.country_id = self.employee_id.country_id
            appoint_line = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id),('state','=','done')],limit=1 )
            if appoint_line :
                self.job_id = appoint_line.job_id.id
                self.code = appoint_line.job_id.name.number
                self.number_job =appoint_line.number
                self.type_id = appoint_line.type_id.id
                self.far_age = appoint_line.type_id.far_age
                self.grade_id = appoint_line.grade_id.id
                self.department_id = appoint_line.department_id.id
                self.date_direct_action = appoint_line. date_direct_action
      
    def send_appoint_group(self, group_id, title, msg):
        '''
        @param group_id: res.groups
        '''
        for recipient in group_id.users:
            self.env['base.notification'].create({'title': title,
                                                  'message': msg,
                                                  'user_id': recipient.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_direct_appoint',
                                                  'notif': True
                                                  })
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'new'  :
                raise UserError(_(u'لا يمكن حذف قرار مباشرة التعين  إلا في حالة طلب !'))
        return super(hrDirectAppoint, self).unlink()
   