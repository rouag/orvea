# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
from openerp.exceptions import UserError
from datetime import date, datetime, timedelta

class HrMandateTask(models.Model):
    _name = 'hr.mandate.task'
    _order = 'id desc'
    _description = 'mandate task'

    number_order = fields.Char(string='رقم القرار', required=1)
    order_date = fields.Date(string='تاريخ القرار', default=fields.Datetime.now(), readonly=1)
    order_picture = fields.Binary(string='صورة القرار', required=1, readonly=1, states={'draft': [('readonly', 0)]})
    order_picture_name = fields.Char(string='صورة القرار', readonly=1, states={'draft': [('readonly', 0)]})
    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', required=1)
    number=fields.Char(string='الرقم الوظيفي',readonly=1) 
    code = fields.Char(string=u'رمز الوظيفة ',readonly=1) 
    country_id=fields.Many2one(related='employee_id.country_id', store=True, readonly=True, string='الجنسية')
    job_id  = fields.Many2one('hr.job', string='الوظيفة',store=True,readonly=1) 
    number_job=fields.Char(string='رقم الوظيفة',store=True,readonly=1) 
    type_id=fields.Many2one('salary.grid.type',string='الصنف',store=True,readonly=1) 
    department_id=fields.Many2one('hr.department',string='الادارة',store=True,readonly=1)
    grade_id=fields.Many2one('salary.grid.grade',string='المرتبة',store=True,readonly=1)
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة',store=True, readonly=1)
    
    
    
    date_mandate_start = fields.Date(string='تاريخ بدأ', readonly=1, states={'draft': [('readonly', 0)]})
    date_mandate_end = fields.Date(string='تاريخ الإلغاء', readonly=1, states={'draft': [('readonly', 0)]})
    note = fields.Text(string=u'الملاحظات', readonly=1, states={'draft': [('readonly', 0)]})
    date_mandate_out = fields.Date(string='تاريخ قرار ')
    file_mandate = fields.Binary(string='صورة قرار ')
    mandate_type = fields.Selection([
        ('internal', u'داخلى'),
        ('external', u'خارجى'),
    ], string=u'نوع الأنتداب', default='internal', advanced_search=True)
    city_id = fields.Many2one('res.city', string=u'المدينة')
    mandate_category_id = fields.Many2one('hr.mandate.category', string=u'فئة التصنيف')
    state = fields.Selection([('draft', '  طلب'),
                             ('waiting', '  المعالي أو اللجنة'),
                             ('extern', 'جهة خارجية'),
                             ('done', 'اعتمدت'),
                             ('cancel', 'ملغاة')], string='الحالة')
    task_name = fields.Char(string=u'وصف المهمة')
    date_from = fields.Date(string=u'من')
    date_to = fields.Date(string=u'الى')
    duration = fields.Integer(string=u'المدة', compute='_compute_duration')

    @api.multi
    def action_draft(self):
        for time_out in self:
            time_out.state = 'waiting'
            
    @api.multi
    def action_waiting(self):
        for time_out in self:
            time_out.state = 'extern'

    @api.multi
    def action_refuse(self):
        for time_out in self:
            time_out.state = 'draft'
    
    @api.multi
    def action_extern(self):
        for time_out in self:
            time_out.state = 'extern'


  


    @api.depends('date_from', 'date_to')
    def _compute_duration(self):
        for rec in self:
            start_date = fields.Date.from_string(rec.date_from)
            end_date = fields.Date.from_string(rec.date_to)
            diff = end_date - start_date
            rec.duration = diff.days + 1
            
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
                self.grade_id = appoint_line.grade_id.id
                self.department_id = appoint_line.department_id.id
      
    
class HrMandateCategory(models.Model):
    _name = 'hr.mandate.category'
    _description = 'mandate Countries Categories'

    category = fields.Selection([
        ('high', u'مرتفعة'),
        ('a', u'أ'),
        ('b', u'ب'),
        ('c', u'ج'),
    ], string=u'الفئات', default='c')
    country_ids = fields.Many2many('res.country', 'mandate_country_rel', 'count_id', 'dep_id', string=u'البلاد')

   