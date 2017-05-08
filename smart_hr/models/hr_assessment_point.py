# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError

class hr_assessment_point_job(models.Model):
    _name = "hr.assessment.point.job"
    _description = "Job Performance Points"

    eval_type = fields.Selection([
        ('probation_period', u'تقييم الاداء الوظيفى خلال فتره التجربة'),
        ('user_temp_job', u'تقييم الاداء الوظيفى خلال المستخدمين والمعينين على بند الاجور والوظائف المؤقته'),
        ('special_job', u'تقييم الاداء الوظيفى لشاغلى الوظائف التخصصية'),
        ('veterinary_10', u'تقييم الاداء الوظيفى لشاغلى وظائف الطب البيطرى للمراتب العاشره فما دون'),
        ('veterinary_11_12_13', u'تقييم الاداء الوظيفى لشاغلى وظائف الطب البيطرى للمراتب 11 و 12 و 13'),
        ('administrative', u'تقييم الاداء الوظيفى للوظائف الادارية'),
        ('supervisor', u'تقييم الاداء الوظيفى للوظائف الاشرافية'),
        ('executive', u'تقييم الاداء الوظيفى للوظائف التنفيذية'),
    ], string=u'نوع التقييم', )
    eval_name = fields.Char(string=u'أسم')
    point_from = fields.Integer(string=u'نقاط من')
    point_to = fields.Integer(string=u'نقاط إلى')
    score = fields.Float(string=u'نقاط تقييم')

class hr_assessment_point_education(models.Model):
    _name = 'hr.assessment.point.education'
    _description = 'Education Qualification Points'

    name = fields.Char(string=u'مؤهلات الدراسى')
    year_point = fields.Float(string=u"نقاط في السنة")
    year_no = fields.Float(string=u"عدد سنوات")
    total = fields.Float(string=u"الإجمــالي", compute="_calc_total")

    @api.depends('year_point', 'year_no')
    def _calc_total(self):
        for rec in self:
            rec.total = rec.year_point * rec.year_no

class hr_assessment_point_training(models.Model):
    _name = 'hr.assessment.point.training'
    _description = 'Training Performance Points'

    type_no = fields.Selection([
        ('day', u'أيام'),
        ('week', u'أسابيع'),
    ], string=u'أيام أو أسابيع', default='day')
    number = fields.Integer(string=u'عدد')
    direct_score = fields.Float(string=u'نقاط التدريب المباشر')
    indirect_score = fields.Float(string=u'نقاط التدريب الغير مباشر')

class hr_assessment_point_seniority(models.Model):
    _name = 'hr.assessment.point.seniority'
    _description = 'Seniority Points'

    year = fields.Integer(string=u'سنوات')
    month = fields.Integer(string=u'أشهر')
    score = fields.Float(string=u'النقاط')


class hrAssessmentResultConfig(models.Model):
    _name = 'hr.assessment.result.config'
    _description = u'إعدادات نتائج تقييم موظف'
   
    name = fields.Char(string = u'النتيجة', )
    
    leave_type = fields.Many2one('hr.holidays.status', string='leave type')