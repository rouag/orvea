# -*- coding: utf-8 -*-


from openerp import models, fields, api
from pychart.arrow import default


class BaseNotification(models.Model):
    _name = 'base.notification'
    _rec_name = 'title'
    
    @api.model
    def create(self, vals):
        if vals.get("type", False):
            type = vals.get("type", False)
            notification_setting_line = self.env['notification.setting.line'].search([('type','=',type)])
            if notification_setting_line :
                vals['notif'] = notification_setting_line.notif
                vals['email'] = notification_setting_line.email
                vals['sms'] = notification_setting_line.sms
                vals['interval_between_notif'] = notification_setting_line.interval_between_notif
        return super(BaseNotification, self).create(vals)
    
    @api.multi
    def resend_notif(self):
        self.to_read = True
    
    def _template_notif(self):
        models_data = self.env['ir.model.data']
        template_id = models_data.get_object_reference('smart_base', 'notification_template_warning')[1]
        return template_id

    user_id = fields.Many2one('res.users', string='الموظف')
    show_date = fields.Datetime(string='تاريخ التنبيه')
    message = fields.Char(string='المحتوى')
    title = fields.Char(string='العنوان')
    to_read = fields.Boolean(string='للتنبيه', default=True)
    res_id = fields.Integer(string='Res ID')
    res_action = fields.Char(string='action name (module_name.action_name)')
    interval_between_notif = fields.Integer('المدة')
    first_notif = fields.Boolean(string='أول تنبيه', default=True)
    notif = fields.Boolean('إشعار')
    sms = fields.Boolean('رسائل الجوال')
    email = fields.Boolean('البريد الالكتروني')
    template_id = fields.Many2one('mail.template', string='القالب')
    date_moins_que = fields.Date( method=True, string="date moins que")
    date_plus_que = fields.Date( method=True, string="date plus que")
    type = fields.Selection([
        ('refuse_leave', 'رفض إجازة'),
        ('accept_refuse', 'موافقة على إجازة'),
        ('posting', 'تعين'),
    ], 'النوع', default='refuse_leave')
