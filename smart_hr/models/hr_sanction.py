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
    
    
class hrSanctionHistory(models.Model):
    _name = 'hr.sanction.history'
  
   
    name = fields.Char(string='رقم القرار' )
    sanction_id = fields.Many2one('hr.sanction', string=' العقوبات', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string=' الموظف', required=1)
    action = fields.Char(string='الإجراء')
    reason = fields.Char(string='السبب', required=1,)
    order_date = fields.Date(string='تاريخ القرار')
    


    
class HrSanctionLigne(models.Model):
    _name = 'hr.sanction.ligne'  
    _description = u' العقوبات'
    
    
    employee_id = fields.Many2one('hr.employee', string=u' إسم الموظف', required=1)
    type_sanction = fields.Many2one('hr.type.sanction',string=u'العقوبة')
    active = fields.Boolean(string=u'سارية', default=True)
    nb_days_old = fields.Integer(string=u'عدد أيام ')
    nb_days_new = fields.Integer(string=u'عدد الايام بعد التعديل ')
    sanction_id = fields.Many2one('hr.sanction', string=' العقوبات', ondelete='cascade')
    sanction_update_id = fields.Many2one('hr.sanction', string=' العقوبات', ondelete='cascade')
    #option_update_line = fields.Boolean(related='sanction_id.option_update', store=True, readonly=True, string=u'الرقم الوظيفي') 
    option_update_line = fields.Boolean(string='تعديل')
   # wizard_sanction_id = fields.Many2one('wizard.sanction.update', string=' العقوبات', ondelete='cascade')
#     sanction_state = fields.Selection(related='sanction_id.state', store=True, string='الحالة')
    state = fields.Selection([('waiting', 'في إنتظار العقوبة'),
                               ('excluded', 'مستبعد'),
                               ('done', 'تم العقوبة'),
                               ('cancel', 'ملغى')], string='الحالة', readonly=1, default='waiting')

    
class hrSanction(models.Model):
    _name = 'hr.sanction'
    _order = 'id desc'
    _description = u'إجراء العقوبات'
    
    name = fields.Char(string='رقم القرار', required=1 )
    order_date = fields.Date(string='تاريخ العقوبة',default=fields.Datetime.now(),readonly=1) 
    sanction_text = fields.Text(string=u'محتوى العقوبة' )
    order_picture = fields.Binary(string='صورة القرار', required=1) 
    order_picture_name = fields.Char(string='صورة القرار') 
    sanction_id = fields.Many2one('hr.difference.sanction',string='العقوبة')
    type_sanction = fields.Many2one('hr.type.sanction',string=u'نوع العقوبة',required=1)
    date_sanction_start = fields.Date(string='تاريخ بدأ العقوبة') 
    date_sanction_end = fields.Date(string='تاريخ الإلغاء') 
    line_ids = fields.One2many('hr.sanction.ligne', 'sanction_id', string=u'العقوبات')
    note = fields.Text(string = u'الملاحظات')
    nb_days_old = fields.Integer(string=u'عدد أيام ')
    history_ids = fields.One2many('hr.sanction.history', 'sanction_id', string='سجل التغييرات', readonly=1)
    option_update = fields.Boolean(string='تعديل')
    #update sanction
    number_order = fields.Char(string='رقم القرار')
    order_date_up = fields.Date(string='تاريخ العقوبة',default=fields.Datetime.now()) 
    order_picture_up = fields.Binary(string='صورة القرار') 
    order_picture_up_name = fields.Char(string='صورة القرار') 
    type_sanction_up = fields.Many2one('hr.type.sanction',string=u'نوع العقوبة',)
    date_sanction_start_up = fields.Date(string='تاريخ بدأ العقوبة') 
    date_sanction_end_up = fields.Date(string='تاريخ الإلغاء') 
    line_ids_up = fields.One2many('hr.sanction.ligne', 'sanction_update_id', string=u'العقوبات')
    
    
    state = fields.Selection([('draft', '  طلب'),
                             ('waiting', '  صاحب صلاحية العقوبات'),
                             ('extern', 'جهة خارجية'),
                             ('done', 'اعتمدت'),
                              ('update', 'تعديل'),
                            ('cancel','مرفوض')], string='الحالة', readonly=1, default='draft')
 
    
    
            
    
    @api.multi
    def button_cancel_sanction(self):
        self.ensure_one() 
        #TODO  
        sanction=self.search([('state','=','done')])
        
    @api.multi
    def button_update_sanction(self):
        self.ensure_one()
        self.option_update = True
        for rec in self.line_ids:
             self.option_update_line = True
        self.state = 'update'
#  action_update
    @api.multi
    def action_update(self):
        self.ensure_one()
        
        for rec in self.line_ids:
            self.env['hr.difference.sanction'].create({
                                                        'name': self.name ,
                                                        'order_new': self.number_order,
                                                       'date_sanction_start_old' : self.date_sanction_start,
                                                      'date_sanction_end_old' : self.date_sanction_end,
                                                       'type_sanction_new' : self.type_sanction_up.id,
                                                      #  'type_sanction_old'  :  type_sanction,
                                                        'date_sanction_start_new' : self.date_sanction_start_up,
                                                        'date_sanction_end_new' : self.date_sanction_end_up,
                                                        'order_update' : self.order_date_up,
                                                        'employee_id' :rec.employee_id.id,
                                                        'nb_days_old' : rec.nb_days_old,
                                                        'nb_days_new' : rec.nb_days_new,
                                                        # 'state' :state,
                                                         'order_picture' : self.order_picture,
                                                        'order_picture_name' : self.order_picture_name,
                                                  
                                                           })
            self.option_update_line = False
        self.option_update = False
        self.state = 'done'
        
    @api.multi
    def action_draft(self):
        self.ensure_one()
        self.state = 'waiting'
  
    @api.multi
    def action_refuse(self):
        self.ensure_one()
        self.state = 'draft'
    
    @api.multi
    def action_refuse_update(self):
        self.ensure_one()
        self.state = 'done'
        self.option_update = False
    
    
    @api.multi
    def action_waiting(self):
        self.ensure_one()
        self.state = 'extern'

    @api.multi
    def action_extern(self):
        self.ensure_one()
        direct_appoint_obj = self.env['hr.employee.sanction']
        if self.type_sanction_up.id == self.env.ref('smart_hr.data_hr_sanction_type_separation').id or self.type_sanction_up.id != self.env.ref('smart_hr.data_hr_sanction_type_grade').id :
            for rec in self.line_ids:
                self.env['hr.employee.sanction'].create({ 'employee_id': rec.employee_id.id,
                                                  'type_sanction' : rec.type_sanction.id,
                                                  'date_sanction_start' : self.date_sanction_start,
                                                  'date_sanction_end' : self.date_sanction_end,
                                                          })
          
        if rec.type_sanction.id == self.env.ref('smart_hr.data_hr_sanction_type_grade').id:
            type = '91'
        elif rec.type_sanction.id == self.env.ref('smart_hr.data_hr_sanction_type_separation').id:
            type = '92'
        
        if type:
            self.env['hr.employee.history'].sudo().add_action_line(rec.employee_id.id, rec.type_sanction.id, self.date_sanction_start, type)
           
        self.state = 'done'
            
    @api.multi
    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancel'
        for line in self.line_ids:
            
            line.state = 'cancel'
class HrUpadateSanction(models.Model):
    _name = 'hr.update.sanction'  
    _rec_name = 'number_order' 
    
    number_order = fields.Char(string='رقم القرار', required=1 )
    order_date_up = fields.Date(string='تاريخ العقوبة',default=fields.Datetime.now()) 
    
    order_picture_up = fields.Binary(string='صورة القرار') 
    order_picture_up_name = fields.Char(string='صورة القرار') 
 
    type_sanction_up = fields.Many2one('hr.type.sanction',string=u'نوع العقوبة',)
    date_sanction_start_up = fields.Date(string='تاريخ بدأ العقوبة') 
    date_sanction_end_up = fields.Date(string='تاريخ الإلغاء') 
    line_ids_up = fields.One2many('hr.sanction.ligne', 'sanction_update_id', string=u'العقوبات')
     
        
class HrDifferenceSanction(models.Model):
    _name = 'hr.difference.sanction'  
    _order = 'id desc'
    _description = u'فروقات العقوبات'
    
    name = fields.Char(string='رقم القرار' )
    order_new = fields.Char(string=u'قرار العقوبة الجديد')
    order_update = fields.Char(string=u'خطاب تعديل الجزاء')
    date_sanction_start_old = fields.Date(string='تاريخ بدأ العقوبةالقديم') 
    date_sanction_end_old = fields.Date(string='تاريخ الإلغاءالقديم') 
    date_sanction_start_new = fields.Date(string='تاريخ بدأ العقوبةالجديد') 
    date_sanction_end_new = fields.Date(string='تاريخ الإلغاءالجديد') 
    order_date = fields.Date(string='تاريخ القرار',readonly=1)
    employee_id = fields.Many2one('hr.employee',  string=u'الموظف', domain=[('employee_state','=','employee')], advanced_search=True)
    type_sanction_old = fields.Many2one('hr.type.sanction',string=u'العقوبة')
    type_sanction_new = fields.Many2one('hr.type.sanction',string=u'العقوبةالجديدة')
    sanction_ids = fields.One2many('hr.sanction', 'sanction_id', string=u'العقوبات')
    nb_days_old = fields.Float(string=u'   القديم') 
    nb_days_new = fields.Float(string=u'   الجديد') 
    diff_days = fields.Float(string=u' الفرق',compute="_compute_diff_days")
    deduction = fields.Boolean(string=u'حسم')
    state = fields.Selection([('waiting', 'في إنتظار العقوبة'),
                               ('excluded', 'مستبعد'),
                               ('done', 'تم العقوبة'),
                               ('cancel', 'ملغى')], string='الحالة', readonly=1, default='waiting')
    
    
    @api.multi
    @api.depends('nb_days_old', 'nb_days_new')
    def _compute_diff_days(self):
       for rec in self :
           if rec.nb_days_old and rec.nb_days_new :
               rec.diff_days = (rec.nb_days_old - rec.nb_days_new)
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
   