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
    state = fields.Selection([('draft', '  طلب'),
                             ('waiting', '  صاحب صلاحية العقوبات'),
                             ('extern', 'جهة خارجية'),
                             ('done', 'اعتمدت')], string='الحالة', readonly=1, default='draft')
 
    
    @api.onchange('date_sanction_start')
    def _onchange_date_sanction_start(self):
         if self.date_direct_action :
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
        self.state = 'done'
        
   