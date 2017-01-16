# -*- coding: utf-8 -*-


from openerp import models, fields, api, _


class CoursesFollowUp(models.Model):

    _name = 'courses.followup'

    _description = u'متابعة الدورات الدراسيّة'

    name = fields.Char(string=u' إسم الدورة', required=1)
    date_from = fields.Date(string=u'التاريخ من ', required=1)
    date_to = fields.Date(string=u'التاريخ الى', required=1)
    result = fields.Selection([
        ('suceed', u'نجح'),
        ('not_succeed', u' لم ينجح')], string=u'النتيجة')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('progress', u'جارية'),
        ('done', u'انتهت')], string=u'حالة', default='draft')

    employee_id = fields.Many2one('hr.employee', string=u'الموظف', advanced_search=True)

    @api.one
    def action_start(self):
        self.state = 'progress'
        
    @api.one
    def action_done(self):
        self.state = 'done'