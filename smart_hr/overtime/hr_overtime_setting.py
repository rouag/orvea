# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError


class HrOvertimeSetting(models.Model):
    _name = 'hr.overtime.setting'
    _description = u'‫إعدادات خارج الدوام'

    name = fields.Char(string='name', default=u'إعدادات  خارج الدوام')
    normal_days = fields.Float(string='معدل ساعات التكليف خلال الأيام العادية لا يزيد في اليوم الواحد  عن نسبة من الراتب اليومي')
    friday_saturday = fields.Float(string='معدل ساعات التكليف خلال أيام  الجمعة والسبت  يحتسب بحد أعلى قدره  نسبة من الراتب الأساسي')
    holidays = fields.Float(string='معدل ساعات التكليف خلال أيام الأعياد يحتسب بحد أعلى قدره')
    grade_ids = fields.Many2many('salary.grid.grade', 'overtime_grade_rel', 'overtime_id', 'grade_id', string=u'المراتب التي لا تستحق بدل نقل')
    allowance_transport_id = fields.Many2one('hr.allowance.type', string='بدل النقل',default=lambda self: self.env.ref('smart_hr.hr_allowance_type_01'))
    allowance_overtime_id = fields.Many2one('hr.allowance.type', string='بدل خارج الدوام',default=lambda self: self.env.ref('smart_hr.hr_allowance_type_14'))
    days_normal = fields.Float(string='معدل يوم خارج الدوام للايام العادية مقابل يوم عمل')
    days_holidays = fields.Float(string='معدل يوم خارج الدوام  للأعياد   مقابل يوم عمل')
    days_weekend = fields.Float(string='معدل يوم خارج الدوام ليومي الجمعة و السبت  مقابل يوم عمل')
    grade_oblig_ids = fields.Many2many('salary.grid.grade',  string=u'المراتب التي تستحق تكليف من الوزير أو من في حكمه')
    
    
    @api.multi
    def button_setting(self):
        overtime_setting = self.env['hr.overtime.setting'].search([], limit=1)
        if overtime_setting:
            value = {
                'name': u'إعدادات خارج الدوام',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.overtime.setting',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': overtime_setting.id,
            }
            return value


