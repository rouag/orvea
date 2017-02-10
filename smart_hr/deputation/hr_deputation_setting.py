# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date


class HrDeputationSetting(models.Model):
    _name = 'hr.deputation.setting'
    _description = u'‫إعدادات الانتدابات‬‬'

    name = fields.Char(string='name')
    deputation_distance = fields.Float(string=u'المسافة المحدد للإنتداب', default=75)

    @api.multi
    def button_setting(self):
        deputation_setting = self.env['hr.deputation.setting'].search([], limit=1)
        if deputation_setting:
            value = {
                'name': u'إعدادات عامة',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.deputation.setting',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': deputation_setting.id,
            }
            return value
