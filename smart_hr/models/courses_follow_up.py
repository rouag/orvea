# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class CoursesFollowUp(models.Model):

    _name = 'courses.followup'

    _description = u'متابعة الدورات الدراسيّة'

    name = fields.Char(string=u' موضوع الدورة', required=1, readonly = True)
    result = fields.Selection([
        ('suceed', u'نجح'),
        ('not_succeed', u' لم ينجح')], string=u'النتيجة', readonly = True)
    state = fields.Selection([
        ('progress', u'جارية'),
        ('done', u'انتهت'),
            ('cancel', u'ملغاة'),
        ('cut', u'قطعت'),
        ], string=u'الحالة', default='progress', )

    employee_id = fields.Many2one('hr.employee', string=u'الموظف', advanced_search = True , required = 1, readonly = True)
    holiday_id = fields.Many2one('hr.holidays', string=u'رقم الاجازة',readonly = True)
    date_from = fields.Date(string=u' تاريخ البدء  ', related='holiday_id.date_from')
    date_to = fields.Date(string=u' تاريخ الإنتهاء ', related='holiday_id.date_to')
    duration = fields.Integer(string=u'الأيام', related='holiday_id.duration')
    courses_city = fields.Char(string=u'المدينة', related='holiday_id.courses_city',readonly = True)
    courses_country = fields.Char(string=u'الدولة', related='holiday_id.courses_country',readonly = True)


    @api.one
    def action_succeeded(self):
        if fields.Date.from_string(self.date_to) > fields.Date.from_string(fields.Date.today()):
            raise ValidationError(u"الدورة لم تنتهي بعد")
        self.result = 'suceed'
        self.state = 'done'

    @api.one
    def action_not_succeeded(self):
        if self.date_to:
            if fields.Date.from_string(self.date_to) > fields.Date.from_string(fields.Date.today()):
                raise ValidationError(u"الدورة لم تنتهي بعد")
        self.result = 'not_succeed'
        self.env['hr.employee.promotion.history'].decrement_promotion_duration(self.employee_id,self.duration)
        self.state = 'done'
