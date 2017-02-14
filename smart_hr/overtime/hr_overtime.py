# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
from openerp.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from umalqurra.hijri_date import HijriDate


class HrOvertime(models.Model):
    _name = 'hr.overtime'
    _order = 'id desc'
    _rec_name = 'order_date'
    _description = u'إجراء خارج دوام'

    order_date = fields.Date(string='تاريخ الطلب', default=fields.Datetime.now(), readonly=1)
    file_order = fields.Binary(string='صورة الطلب')
    decision_number = fields.Char(string='رقم القرار')
    decision_date = fields.Date(string='تاريخ القرار', default=fields.Datetime.now(), readonly=1)
    file_decision = fields.Binary(string='صورة القرار')
    amount = fields.Float(string='المبلغ')
    note = fields.Text(string=u'الملاحظات', readonly=1, states={'draft': [('readonly', 0)]})
    line_ids = fields.One2many('hr.overtime.ligne', 'overtime_id', string=u'خارج دوام', states={'draft': [('readonly', 0)]})
    state = fields.Selection([
                              ('draft', u'طلب'),
                              ('audit', u'دراسة الطلب'),
                              ('waiting', u'اللجنة'),
                              ('done', u'اعتمدت'),
                              ('order', u'دراسة التقرير'),
                              ('finish', u'منتهية'),
                                ('refuse', u'مرفوض')
                              ], string=u'حالة', default='draft', advanced_search=True)
    @api.multi
    def action_draft(self):
        for deputation in self:
            deputation.state = 'audit'
         
    @api.multi
    def action_commission(self):
        for deputation in self:
            deputation.state = 'waiting'   
   
    @api.multi
    def action_audit(self):
        for deputation in self:
            deputation.state = 'done'   
    @api.multi
    def action_waiting(self):
        for deputation in self:
            deputation.state = 'done'

    @api.multi
    def action_done(self):
        for deputation in self:
            for line in deputation.line_ids :
                self.env['base.notification'].create({'title': u'إشعار إشعار بقبول  خارج الدوام',
                                              'message': u'لقد تم إشعار بقبول  خارج الدوام',
                                              'user_id': line.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': line.id,
                                             'res_action': 'smart_hr.action_hr_overtime'})
            deputation.state = 'order'
    
    @api.multi
    def action_order(self):
        for deputation in self:
            deputation.state = 'finish'


    @api.multi
    def action_refuse(self):
        for deputation in self:
            for line in deputation.line_ids :
                self.env['base.notification'].create({'title': u'إشعار إشعار برفض  خارج الدوام',
                                              'message': u'لقد تم إشعار برفض  خارج الدوام',
                                              'user_id': line.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': line.id,
                                             'res_action': 'smart_hr.action_hr_overtime'})
            deputation.state = 'refuse'
    
    
   

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_(u'لا يمكن حذف خارج دوام  إلا في حالة طلب !'))
        return super(HrOvertime, self).unlink()


class HrOvertimeLigne(models.Model):
    _name = 'hr.overtime.ligne'
    _description = u' خارج دوام'
    

    overtime_id = fields.Many2one('hr.overtime', string=' خارج دوام', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string=u' إسم الموظف', required=1)
    type = fields.Selection([('friday_saturday', ' أيام الجمعة والسبت'),
                             ('holidays', 'أيام الأعياد'),
                             ('normal_days', 'الايام العادية')
                             ], string='نوع خارج الدوام', default='friday_saturday')
    days_number = fields.Integer(string='عدد الايام ' ,compute='_compute_duration')
    heure_number = fields.Integer(string='عدد الساعات')
    date_from = fields.Date(string=u'التاريخ من ', default=fields.Datetime.now())
    date_to = fields.Date(string=u'الى')
    mission = fields.Text(string='المهمة')
    
    
    @api.one
    @api.depends('date_from', 'date_to')
    def _compute_duration(self):
        if self.date_from and self.date_to:
            date_from = fields.Date.from_string(self.date_from)
            date_to = fields.Date.from_string(self.date_to)
            self.days_number = (date_to - date_from).days + 1
    

      