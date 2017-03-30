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
    years_last_transfert = fields.Integer(string=u'عدد السنوات من أخر نقل', default=3)

    # الإعارة
    lend_duration = fields.Integer(string=u'مدة الإعارة (باليوم)', default=354)
    one_max_lend_duration = fields.Integer(string=u'الحد الأقصى للتمديد في المرة (بالأيام)', default=354)
    max_lend_duration_sum = fields.Integer(string=u'الحد الأقصى لمجموع الاعارات (باليوم)', default=354)
    lend_number = fields.Integer(string=u'عدد مرات التمديد', default=3)
    periode_between_lend = fields.Integer(string=u'المدة بين إعارتين (بالسنة)', default=3)
    extend_lend_duration = fields.Integer(string=u'مدة تمديد الإعارة (باليوم)', default=354)
    # والتكليف‬‬
    assign_duration = fields.Integer(string=u'مدة التكليف‬‬ (باليوم)', default=354)
    # الرواتب
    allowance_job_nature = fields.Many2one('hr.allowance.type', string=u'بدل طبيعة العمل', default=lambda self: self.env.ref('smart_hr.hr_allowance_type_07'))
    allowance_proportion = fields.Float(string=u'نسبة بدل طبيعة العمل (%)', default=15)
    allowance_deputation = fields.Many2one('hr.allowance.type', string=u'بدل إنتداب',  default=lambda self: self.env.ref('smart_hr.hr_allowance_type_15'))
    deputation_days = fields.Integer(string=u'عدد ايام بدل الانتباب', default=3)
    allowance_deportation = fields.Many2one('hr.allowance.type', string=u'بدل ترحيل',  default=lambda self: self.env.ref('smart_hr.hr_allowance_type_11'))
    deportation_amount = fields.Float(string=u'مبلغ بدل الترحيل', default=0.0)
    retirement_proportion = fields.Float(string=u'حصة الحكومة من التقاعد (%)', default=9)

    @api.multi
    def button_setting(self):
        hr_setting = self.env['hr.setting'].search([], limit=1)
        if hr_setting:
            value = {
                'name': u'‫إعدادات النقل، الإعارة والتكليف‬‬',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.setting',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': hr_setting.id,
            }
            return value


class HrAuthorityBoardSetting(models.Model):
    _name = 'hr.authority.board.setting'
    _description = u'‫إعدادات مجلس الهيئة‬‬'
    
    name = fields.Char(string='إعداد مجلس الهيئة‬‬')
    users_number = fields.Integer(string=u'عدد اعضاء الهيئة')
    job_required_ids = fields.Many2many('hr.job', string='وظائف اعضاء مجلس الهيئة')

    @api.multi
    def button_authority_board_setting(self):
        hr_authority_board_setting = self.env['hr.authority.board.setting'].search([], limit=1)
        if hr_authority_board_setting:
            value = {
                'name': u'إعدادات  مجلس الهيئة',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.authority.board.setting',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': hr_authority_board_setting.id,
            }
            return value
