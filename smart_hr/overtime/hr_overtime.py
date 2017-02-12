# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
from openerp.exceptions import UserError
from datetime import date, datetime, timedelta


class HrOvertime(models.Model):
    _name = 'hr.overtime'
    _order = 'id desc'
    _rec_name = 'number_time_out'
    _description = u'إجراء خارج دوام'

    number_time_out = fields.Char(string='رقم القرار', required=1)
    order_date = fields.Date(string='تاريخ القرار', default=fields.Datetime.now(), readonly=1)
    order_picture = fields.Binary(string='صورة القرار', required=1, readonly=1, states={'draft': [('readonly', 0)]})
    order_picture_name = fields.Char(string='صورة القرار', readonly=1, states={'draft': [('readonly', 0)]})
    date_time_out_start = fields.Date(string='تاريخ بدأ خارج دوام', readonly=1, states={'draft': [('readonly', 0)]})
    date_time_out_end = fields.Date(string='تاريخ الإلغاء', readonly=1, states={'draft': [('readonly', 0)]})
    note = fields.Text(string=u'الملاحظات', readonly=1, states={'draft': [('readonly', 0)]})
    number_order = fields.Char(string='رقم قرارموافقة خارج الدوام  ')
    date_time_out = fields.Date(string='تاريخ قرارموافقة خارج الدوام ')
    file_time_out = fields.Binary(string='صورة قرارموافقة خارج الدوام ')
    line_ids = fields.One2many('hr.overtime.ligne', 'overtime_id', string=u'خارج دوام', states={'draft': [('readonly', 0)]})
    state = fields.Selection([('draft', '  طلب'),
                             ('waiting', '  المعالي أو اللجنة'),
                             ('extern', 'جهة خارجية'),
                             ('done', 'اعتمدت'),
                             ('cancel', 'ملغاة')], string='الحالة')

    

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


    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft'  :
                raise UserError(_(u'لا يمكن حذف خارج دوام  إلا في حالة طلب !'))
        return super(HrOvertime, self).unlink()
    
class HrOvertimeLigne(models.Model):
    _name = 'hr.overtime.ligne'
    _description = u' خارج دوام'

    overtime_id = fields.Many2one('hr.overtime', string=' خارج دوام', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string=u' إسم الموظف', required=1)
    type_time_out = fields.Selection([('friday_saturday', ' أيام الجمعة والسبت'),
                                    ('holidays', 'أيام الأعياد'),
                                    ('normal_days', 'الايام العادية')
                                   ], string='نوع خارج الدوام',  default='friday_saturday')
    days_number = fields.Integer(string='عدد الايام ')
    heure_number = fields.Integer(string='عدد الساعات')
    date_from = fields.Date(string=u'التاريخ من ', default=fields.Datetime.now())
    date_to = fields.Date(string=u'التاريخ الى')
    mission = fields.Char(string='المهمة')
  


