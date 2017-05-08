# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class NotificationSetting(models.Model):
    _name = 'notification.setting'
    _rec_name = 'name_setting'

    name_setting = fields.Char("إعدادات الاشعارات ")
<<<<<<< HEAD
    notification_setting_line_ids = fields.One2many('notification.setting.line', 'notification_setting_id', string='الاشعارات',)

=======
    notif_all = fields.Boolean('إشعار')
    accept_notif_all = fields.Boolean(string='كل الاشعارات')
    sms_all = fields.Boolean('رسائل الجوال')
    email_all = fields.Boolean('البريد الالكتروني')
    notification_setting_line_ids = fields.One2many('notification.setting.line', 'notification_setting_id', string='الاشعارات',)



    @api.onchange('accept_notif_all')
    def _onchange_accept_notif_all(self):
        if self.accept_notif_all == True :
            for rec in self.notification_setting_line_ids:
                rec.notif =True
        if self.accept_notif_all == False :
            for rec in self.notification_setting_line_ids:
                rec.notif = False

>>>>>>> 276a72932207909ed91b8ca99faaeae2fb13647f
    @api.multi
    def open_notif_setting(self):
        setting = self.search([])
        if setting:
            value = {'name': _(u'اعدادات الاشعارات'),
                     'view_type': 'form',
                     'view_mode': 'form',
                     'res_model': 'notification.setting',
                     'view_id': False,
                     'type': 'ir.actions.act_window',
<<<<<<< HEAD
                     'res_id': setting[0].id,
=======
                     'res_id': setting[-1].id,
>>>>>>> 276a72932207909ed91b8ca99faaeae2fb13647f
                     }
        else:
            vals = {'name_setting': u'إعدادات الاشعارات',
                    'delai_before_notif': 1}
            record = self.create(vals)
            value = {
                'name': _(u'إعدادات الاشعارات '),
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

    type = fields.Selection([('refuse_leave', 'رفض إجازة'),
<<<<<<< HEAD
                             ('accept_refuse', 'موافقة على إجازة'),
                             ('posting', 'تعين')], string='النوع', default='refuse_leave')
    notif = fields.Boolean('إشعار')
    sms = fields.Boolean('رسائل الجوال')
    email = fields.Boolean('البريد الالكتروني')
    interval_between_notif = fields.Integer('المدة')
=======
                            ('hr_holidays_type', 'إجراء إجازة'),
                            ('hr_holidays_extension_type', 'إجراءتمديد رصيد الاجازات  '),
                            ('hr_holidays_cancellation_type', ' إجراء قطع و الغاء الاجازات'),
                            ('hr_promotion_type', '  إجراء الترقية'),
                            ('hr_overtime_type', ' إجراء  خارج دوام'),
                            ('hr_employee_appoint_type', ' إجراء تعين'),
                            ('hr_employee_appoint_direct_type', ' إجراءمباشرة تعين'),
                            ('hr_employee_training_type', ' إجراء التدريب'),
                            ('hr_employee_deputation_type', ' إجراء إنتداب'),
                            ('hr_employee_job_create_type', ' إجراء إحداث الوظائف'),
                            ('hr_employee_hr_job_strip_type', ' إجراء سلخ وظائف'),
                            ('hr_employee_hr_job_cancel_type', ' إجراء إلغاء الوظائف'),
                            ('hr_employee_hr_job_move_type', ' إجراء نقل وظائف'),
                            ('hr_employee_hr_job_scal_down_grade_type', ' إجراء رفع أو خفض وظائف'),
                            ('hr_employee_job_update_type', ' إجراء تحوير‬ وظائف'),
                            ('hr_employee_authorization_type', ' إجراء طلبات الإستئذان'),
                            ('hr_employee_contract_type', ' إجراء العقد'),
                            ('hr_employee_commissioning_type', ' إجراء تكليف موظف'),
                            ('hr_employee_transfert_type', ' إجراء طلب نقل'),
                            ('hr_cron_test_years_employee_type', ' إشعار بلوغ سن التقاعد'),
                            ('hr_cron_test_periode_employee_type', ' إشعار نهاية مدة التجربة'),
                            ('hr_cron_commissioning_end_type', ' إشعار نهاية تكليف موظف'),
        
                            ('accept_refuse', 'موافقة على إجازة'),
                             ('posting', 'تعين')], string=' نوع الاجراء')
    notif = fields.Boolean('إشعار')
    sms = fields.Boolean('رسائل الجوال')
    
    email = fields.Boolean('البريد الالكتروني')
>>>>>>> 276a72932207909ed91b8ca99faaeae2fb13647f
    notification_setting_id = fields.Many2one('notification.setting')
