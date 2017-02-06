# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta

class hr_promotion(models.Model):
    _name = 'hr.promotion'
    _inherit = ['ir.needaction_mixin']
    _description = 'Promotion Decision'
    
    
    

    name = fields.Char(string=u'رقم محضر الترقيات', advanced_search=True)
    date = fields.Date(string=u'تاريخ ', default=fields.Datetime.now())
    letter_sender = fields.Char(string=u'جهة الخطاب', advanced_search=True)
    letter_number = fields.Char(string=u'رقم الخطاب', advanced_search=True)
    letter_date = fields.Date(string=u'تاريخ الخطاب')
    employee_promotion_line_ids = fields.One2many('hr.promotion.employee', 'promotion_id', string=' قائمة الموظفين',)

    state = fields.Selection([
                              ('draft', u'طلب'),
                              ('done', u'مفعل'),
                              ('refuse', u'رفض'),
                              ('cancel', u'ملغاة'),
                              ], string=u'حالة', default='draft', advanced_search=True)
    etape = fields.Selection([
                              ('draft', u'طلب'),
                              ('employee_done', u'موافقة صاحب الترقية'),
                              ('manager', u'صاحب صلاحية التعين'),
                              ('minister', u'وزارة الخدمة المدنية'),
                              ('hrm', u'شؤون الموظفين'),
                              ('done', u'اعتمدت'),
                              ('refuse', u'رفض'),
                              ('cancel', u'ملغاة'),
                              ], string=u'حالة', default='draft', advanced_search=True)
 
    @api.model
    def create(self, vals):
        ret = super(hr_promotion, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.promotion.seq')
        ret.write(vals)
        return ret
    @api.model
    def default_get(self,fields):
        res = super(hr_promotion, self).default_get(fields)
        employee_promotion=[]
        employee_promotion_job=[]
        employees=self.env['hr.employee'].search([])
        for emp in employees:
            print emp.job_id
            if emp.job_id.grade_id: 
                if  emp.promotion_duration/365 >  emp.job_id.grade_id.years_job  :
                    if  emp.sanction_ids:
                        for saction in sanction_ids:
                            if sanction.date_sanction_start > (date.today().year -1):
                                if not sanction.nb_days >  15  and  not sanction.type_sanction.code == "4" and not self.env['hr.suspension'].search([('employee_id', '=', emp.id), ('suspension_date', '<=', fields.Datetime.now()),('suspension_end_id.release_date', '=>', fields.Datetime.now())]):
                                    employee_promotion.append(emp)
        for emp_promotion in employee_promotion :
            id_emp= self.env['hr.promotion.employee'].create({'employee_id': emp_promotion.id,
                                                           'old_job_id': emp_promotion.job_id.id,
                                                           'old_number_job': emp_promotion.job_id.number ,
                                                           'emp_department_old_id':emp_promotion.department_id.id,
                                                           'emp_grade_id_old':emp_promotion.job_id.grade_id.id
                                                           }) 
            employee_promotion_job.append(id_emp.id)
        res['employee_promotion_line_ids'] = [(6, 0, employee_promotion_job)]
        return res
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft' and self._uid != SUPERUSER_ID:
                raise ValidationError(u'لا يمكن حذف قرار الترقية في هذه المرحلة يرجى مراجعة مدير النظام')
        return super(hr_promotion, self).unlink()
    
    

  


class hr_promotion_type(models.Model):
    _name = 'hr.promotion.type'
     
    name = fields.Char(string=u'نوع الترقية', advanced_search=True)
    
class hr_promotion_ligne(models.Model):
    _name = 'hr.promotion.employee'
    
    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    promotion_id = fields.Many2one('hr.promotion', string=u'الترقية ')
    old_job_id = fields.Many2one('hr.job', string=u'الوظيفة الحالية')
    new_job_id = fields.Many2one('hr.job', string=u'الوظيفة المرقى عليها')
    old_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1) 
    new_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1) 
    emp_department_old_id = fields.Many2one('hr.department', string='الادارة', store=True, readonly=1)
    emp_grade_id_old = fields.Many2one('salary.grid.grade', string='المرتبةالحالية ', store=True, readonly=1)
    emp_grade_id_new = fields.Many2one('salary.grid.grade', string='المرتبة الجديدة', store=True, readonly=1)



class hr_promotion_demande(models.Model):
    _name = 'hr.promotion.employee.demande'
    
    employee_id = fields.Many2one('hr.employee', string=u'الموظف',default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1))
    name = fields.Char(string=u'رقم الطلب', advanced_search=True)
    description1 = fields.Text(string='رغبات الموظف', ) 
    description2 = fields.Text(string='رغبات الموظف', ) 
    description3 = fields.Text(string='رغبات الموظف', ) 
    description4 = fields.Text(string='رغبات الموظف', ) 
    description5 = fields.Text(string='رغبات الموظف', ) 
    city_fovorite = fields.Char(string='المدينة المفضلة',) 
    hr_allowance_type_id = fields.Many2one('hr.allowance.type', string='أنواع البدلات(بدل طبيعة عمل )',)


