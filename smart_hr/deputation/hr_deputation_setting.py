# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError


class HrDeputationSetting(models.Model):
    _name = 'hr.deputation.setting'
    _description = u'‫إعدادات الانتدابات‬‬'

    name = fields.Char(string='name', default=u'إعدادات الانتدابات')
    deputation_distance = fields.Float(string=u'المسافة المحدد للإنتداب', default=75)
    annual_balance = fields.Integer(string='الرصيد السنوي')
    line_ids = fields.One2many('hr.deputation.allowance', 'deputation_setting_id', string=u'تفاصيل البدلات')

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


class HrDeputationAllowance(models.Model):
    _name = 'hr.deputation.allowance'

    deputation_setting_id = fields.Many2one('hr.deputation.setting', string='Setting', ondelete='cascade')
    internal_transport_amount = fields.Float(string='بدل نقل داخلي')
    external_transport_amount = fields.Float(string='بدل نقل خارجي')
    internal_deputation_amount = fields.Float(string='بدل إنتداب داخلي')
    grade_ids = fields.Many2many('salary.grid.grade', 'deputation_allowance_grade_rel', 'deputation_allowance_id', 'grade_id', string=u'المراتب')


