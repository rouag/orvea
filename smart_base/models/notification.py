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
        ('hr_holidays_type', 'إجراء إجازة'),
        ('hr_holidays_extension_type', 'إجراءتمديد رصيد الاجازات  '),
        ('hr_holidays_cancellation_type', '  إجراء قطع و الغاء الاجازات'),
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
        ('hr_cron_commissioning_end_type', ' إشعار نهاية تكليف موظف'),
        ('posting', 'تعين'),
        ] , '  نوع الاجراء ')
