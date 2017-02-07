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
    desire_number = fields.Integer(string=u'عدد الرغبات', default=5)
    needed_days = fields.Integer(string=u'المدة بين رفض طلب نقل وطلب جديد (باليوم)', default=45)

    @api.multi
    def button_setting(self):
        hr_setting = self.env['hr.setting'].search([], limit=1)
        if not hr_setting:
            # if there is no setting record, than create onoe
            hr_setting = self.env['hr.setting'].sudo().create({'name': u'إعدادات عامة'})
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
