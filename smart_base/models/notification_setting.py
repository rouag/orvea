# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class NotificationSetting(models.Model):
    _name = 'notification.setting'
    _rec_name = 'name_setting'
    
    name_setting = fields.Char("إعدادات الاشعارات ")
    notification_setting_line_ids = fields.One2many('notification.setting.line', 'notification_setting_id', string='الاشعارات',)
    
    @api.multi
    def open_notif_setting(self):
        setting = self.search([])
        if setting:
            value = {
                     'name': _('اعدادات الاشعارات'),
                     'view_type': 'form',
                     'view_mode': 'form',
                     'res_model': 'notification.setting',
                     'view_id': False,
                     'type': 'ir.actions.act_window',
                     'res_id': setting[0].id,
                     }
        else:
            vals = {
                     'name_setting': 'إعدادات الاشعارات',
                     'delai_before_notif': 1,
                     }
            record = self.create(vals)
            value = {
                'name': _('إعدادات الاشعارات '),
                'view_type': 'form',
                     'view_mode': 'form',
                     'res_model': 'notification.setting',
                     'view_id': False,
                     'type': 'ir.actions.act_window',
                'res_id': record.id,
            }
        return value
    
class NotificationSettingLine(models.Model):
    _name = 'notification.setting.line'
    
    @api.model
    def _get_notif_setting(self):
        notification_setting_ids = self.env['notification.setting'].search([])
        return notification_setting_ids[0].id

    
    type = fields.Selection([
        ('refuse_leave', 'رفض إجازة'),
        ('accept_refuse', 'موافقة على إجازة'),
        ('posting', 'تعين'),
    ], 'النوع', default='refuse_leave')
    notif = fields.Boolean('إشعار')
    sms = fields.Boolean('رسائل الجوال')
    email = fields.Boolean('البريد الالكتروني')
    interval_between_notif = fields.Integer('المدة')
    notification_setting_id = fields.Many2one('notification.setting', default=_get_notif_setting)
    
    
     