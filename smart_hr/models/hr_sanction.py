# -*- coding: utf-8 -*-



from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta




class HrTypeSanction(models.Model):
    _name = 'hr.type.sanction'  
    _description = u'أنواع العقوبات'
    
    
    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    min_grade_id = fields.Many2one('salary.grid.grade', string='المرتبة من ')
    max_grade_id = fields.Many2one('salary.grid.grade', string='إلى')
    
    sanction_manager = fields.Boolean(string=u' صاحب صلاحية العقوبات ', default=True)
    sanction_responsable = fields.Boolean(string=u' مسؤول على العقوبات ', default=True)
    sanction_decider = fields.Boolean(string=u' موافقة المقام السامي  ', default=False)
    
class hrSanction(models.Model):
    _name = 'hr.sanction'
    _description = u'إجراء العقوبات'
    
    name = fields.Char(string='رقم القرار', required=1 )
    order_date = fields.Date(string='تاريخ الطلب',default=fields.Datetime.now(),readonly=1) 
    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', required=1)
    type_sanction = fields.Many2one('hr.type.sanction',string='العقوبة',required=1)
    sanction_text = fields.Text(string=u'محتوى العقوبة' )
    date_sanction_start = fields.Date(string='تاريخ بدأ العقوبة') 
    date_sanction_end = fields.Date(string='تاريخ الإلغاء') 
    active = fields.Boolean(string=u'سارية', default=True)
    date_sanction = fields.Date(string='تاريخ العقوبة', default=fields.Datetime.now(),)
    financial_impact = fields.Float(string='  الأثر المالي  %من الراتب') 
    financial_amount = fields.Float(string='  المبلغ') 
    sanction_id = fields.Many2one('hr.remove.sanction',string='العقوبة')
    note = fields.Text(string = u'الملاحظات', required = True)
    state = fields.Selection([('draft', '  طلب'),
                             ('waiting', '  صاحب صلاحية العقوبات'),
                             ('extern', 'جهة خارجية'),
                             ('done', 'اعتمدت')], string='الحالة', readonly=1, default='draft')
 
    
    @api.onchange('date_sanction_end')
    def _onchange_date_sanction_end(self):
         if self.date_sanction_end and self.date_sanction_start :
             if self.date_sanction_end > self.date_sanction_start:
                 raise ValidationError(u"تاريخ إلغاء العقوبة يجب ان يكون أكبر من تاريخ البدأ")
        
  
    @api.multi
    def action_draft(self):
        self.ensure_one()
        self.state = 'waiting'
  
    @api.multi
    def action_refuse(self):
        self.ensure_one()
        self.state = 'draft'
    
    
    @api.multi
    def action_waiting(self):
        self.ensure_one()
        self.state = 'extern'

    @api.multi
    def action_extern(self):
        self.ensure_one()
        direct_appoint_obj = self.env['hr.employee.sanction']
        self.env['hr.employee.sanction'].create({ 'employee_id': self.employee_id.id,
                                                  'type_sanction' : self.type_sanction.id,
                                                  'date_sanction_start' : self.date_sanction_start,
                                                  'date_sanction_end' : self.date_sanction_end,
                                                 
                                                           })
        type=''
        if self.type_appointment.id == self.env.ref('smart_hr.data_hr_sanction_type_alert').id:
            type = '40'
        elif self.type_appointment.id == self.env.ref('smart_hr.data_hr_sanction_type_blame').id:
            type = '89'
        elif self.type_appointment.id == self.env.ref('smart_hr.data_hr_sanction_type_displine').id:
            type = '90'
        elif self.type_appointment.id == self.env.ref('smart_hr.data_hr_sanction_type_grade').id:
            type = '91'
        elif self.type_appointment.id == self.env.ref('smart_hr.data_hr_sanction_type_separation').id:
            type = '92'
       
        if type:
            self.env['hr.employee.history'].sudo().add_action_line(self.employee_id, self.name, self.date, type)
        self.state = 'done'
        
        
class HrRemoveSanction(models.Model):
    _name = 'hr.remove.sanction'  
    _description = u'فسخ عقوبة'
    
    name = fields.Char(string='رقم القرار', required=1 )
    order_date = fields.Date(string='تاريخ الطلب',default=fields.Datetime.now(),readonly=1)
    employee_id = fields.Many2one('hr.employee',  string=u'الموظف', domain=[('employee_state','=','employee')], advanced_search=True)
    type_sanction = fields.Many2one('hr.type.sanction',string=u'العقوبة')
    sanction_ids = fields.One2many('hr.sanction', 'sanction_id', string=u'العقوبات')
    note = fields.Text(string = u'الملاحظات')
    state = fields.Selection([
                              ('draft', u'طلب'),
                              ('waiting', u'  صاحب صلاحية العقوبات'),
                              ('done', u'اعتمدت'),
                              ('refuse', u'رفض'),
                             
                              ], string=u'حالة', default='draft', advanced_search=True)
    
    
    
   
    
    @api.multi
    def action_draft(self):
        self.ensure_one()
        
        self.state = 'waiting'
  
    @api.multi
    def action_refuse(self):
        self.ensure_one()
        self.state = 'draft'
    
    
    @api.multi
    def action_waiting(self):
        self.ensure_one()
        
        
        type=''
        if self.type_appointment.id == self.env.ref('smart_hr.data_hr_sanction_type_alert').id:
            type = '40'
        elif self.type_appointment.id == self.env.ref('smart_hr.data_hr_sanction_type_blame').id:
            type = '89'
        elif self.type_appointment.id == self.env.ref('smart_hr.data_hr_sanction_type_displine').id:
            type = '90'
        elif self.type_appointment.id == self.env.ref('smart_hr.data_hr_sanction_type_grade').id:
            type = '91'
        elif self.type_appointment.id == self.env.ref('smart_hr.data_hr_sanction_type_separation').id:
            type = '92'
       
        if type:
            self.env['hr.employee.history'].sudo().add_action_line(self.employee_id, self.name, self.date, type)
            
            
        remove_sanction = self.env['hr.employee.sanction'].search([('employee_id', '=', self.employee_id.id),
                                                           ('type_sanction', '=', self.type_sanction.id,),
                                                           ('date_sanction_start', '=', self.date_sanction_start),
                                                           ('date_sanction_end', '=', self.date_sanction_end)
                                                           ])
        if remove_sanction :
            remove_sanction.unlink()
        self.state = 'done'

   
   