# -*- coding: utf-8 -*-


from openerp import models, fields, api
from pychart.arrow import default


class BaseNotification(models.Model):
    _name = 'base.notification'
    _rec_name = 'title'
    
    @api.model
    def create(self, vals):
        record = super(BaseNotification, self).create(vals)
        if record.type:
            notification_setting_line = self.env['notification.setting.line'].search([('type','=',record.type)])
            if notification_setting_line :
                record.notif = notification_setting_line.notif
                record.email = notification_setting_line.email
                record.sms = notification_setting_line.sms
                record.interval_between_notif = notification_setting_line.interval_between_notif
        return record
    
    @api.multi
    def resend_notif(self):
        self.to_read = True
    
    def _template_notif(self):
        models_data = self.env['ir.model.data']
        template_id = models_data.get_object_reference('smart_base', 'notification_template_warning')[1]
        return template_id

    user_id = fields.Many2one('res.users', string='employee')
    show_date = fields.Datetime(string='show date')
    message = fields.Char(string='Message')
    title = fields.Char(string='Title')
    to_read = fields.Boolean(string='To read', default=True)
    res_id = fields.Integer(string='Res ID')
    res_action = fields.Char(string='action name (module_name.action_name)')
    interval_between_notif = fields.Integer('المدة')
    first_notif = fields.Boolean(string='First Notif', default=True)
    notif = fields.Boolean('إشعار')
    sms = fields.Boolean('رسائل الجوال')
    email = fields.Boolean('البريد الالكتروني')
    template_id = fields.Many2one('mail.template', string='القالب', default=_template_notif)
    date_moins_que = fields.Date( method=True, string="date moins que")
    date_plus_que = fields.Date( method=True, string="date plus que")
    type = fields.Selection([
        ('refuse_leave', 'رفض إجازة'),
        ('accept_refuse', 'موافقة على إجازة'),
        ('posting', 'تعين'),
    ], 'النوع', default='refuse_leave')
