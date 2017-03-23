# -*- coding: utf-8 -*-


from openerp import models, fields, api, _


class HrDecisionSetting(models.Model):
    _name = 'hr.decision.setting'
    _inherit = ['mail.thread']
    _description = u'اعدادات القرارات'

    name = fields.Char(string='name', default=u'إعدادات القرارات')
    sequence_id = fields.Many2many('ir.sequence', default=lambda self: self.env.ref('smart_hr.hr_decision_seq'), string='تسلسل القرارات')
    number_next = fields.Integer(string='التسلسل التالي', related='sequence_id.number_next_actual')
    new_number_next = fields.Integer(string='التسلسل الجديد')

    @api.multi
    def button_setting(self):
        decision_setting = self.env['hr.decision.setting'].search([], limit=1)
        if decision_setting:
            value = {
                'name': u'اعدادات تسلسل القرارات',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.decision.setting',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': decision_setting.id,
            }
            return value

    @api.multi
    def write(self, vals):
        if 'new_number_next' in vals:
            self.sequence_id.number_next = vals['new_number_next']
            vals['new_number_next'] = 0
        return super(HrDecisionSetting, self).write(vals)
