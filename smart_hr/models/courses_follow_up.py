# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class CoursesFollowUp(models.Model):

    _name = 'courses.followup'

    _description = u'متابعة الدورات الدراسيّة'

    name = fields.Char(string=u' إسم الدورة', required=1)
    result = fields.Selection([
        ('suceed', u'نجح'),
        ('not_succeed', u' لم ينجح')], string=u'النتيجة', readonly=True)
    state = fields.Selection([
        ('progress', u'جارية'),
        ('done', u'انتهت'),
            ('cancel', u'ملغاة'),
        ('cut', u'قطعت'),
        ], string=u'حالة', default='draft')

    employee_id = fields.Many2one('hr.employee', string=u'الموظف', advanced_search=True , required=1)
    holiday_id = fields.Many2one('hr.holidays', string=u'الاجازة')

    @api.one
    def action_succeeded(self):
        self.result = 'suceed'
        self.state = 'done'

    @api.one
    def action_not_succeeded(self):
        self.result = 'not_succeed'
        self.state = 'done'
