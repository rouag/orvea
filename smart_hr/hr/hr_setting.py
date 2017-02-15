# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date


class HrSetting(models.Model):
    _name = 'hr.setting'
    _description = u'‫إعدادات النقل، الإعارة والتكليف‬‬'

    name = fields.Char(string='name')
    # النقل
    desire_number = fields.Integer(string=u'عدد الرغبات', default=5)
    needed_days = fields.Integer(string=u'المدة بين رفض طلب نقل وطلب جديد (باليوم)', default=45)
    # الإعارة
    lend_duration = fields.Integer(string=u'مدة الإعارة (باليوم)', default=365)
    one_max_lend_duration = fields.Integer(string=u'الحد الأقصى للتمديد في المرة (بالأيام)', default=365)
    max_lend_duration_sum = fields.Integer(string=u'الحد الأقصى لمجموع الاعارات (بالسنة)', default=365)
    lend_number = fields.Integer(string=u'عدد مرات التمديد', default=3)
    periode_between_lend = fields.Integer(string=u'المدة بين إعارتين (بالسنة)', default=3)
    extend_lend_duration = fields.Integer(string=u'مدة تمديد الإعارة (باليوم)', default=365)
    # والتكليف‬‬
    assign_duration = fields.Integer(string=u'مدة والتكليف‬‬ (باليوم)', default=365)
    # الرواتب
    salary_proportion = fields.Float(string=u'نسبة الراتب (%)', default=100)
    allowance_job_nature = fields.Many2one('hr.allowance.type', string=u'بدل طبيعة العمل')
    allowance_proportion = fields.Float(string=u'نسبة البدل (%)', default=15)
    allowance_deputation = fields.Many2one('hr.allowance.type', string=u'بدل إنتداب')
    deputation_days = fields.Integer(string=u'عدد الايام', default=3)
    allowance_deportation = fields.Many2one('hr.allowance.type', string=u'بدل ترحيل')
    deportation_amount = fields.Float(string=u'المبلغ', default=0.0)

    @api.multi
    def button_setting(self):
        hr_setting = self.env['hr.setting'].search([], limit=1)
        if hr_setting:
            value = {
                'name': u'إعدادات عامة',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.setting',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': hr_setting.id,
            }
            return value
