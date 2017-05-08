# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class HrEvaluationPoint(models.Model):
    _name = "hr.evaluation.point"
    _description = "Job  Points"

    name = fields.Char(string=u'أسم', required=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', required=1)
    seniority_ids = fields.One2many('hr.evaluation.point.seniority', 'hr_evaluation_point_id', string=u'نقاط الأقدمية')
    education_ids = fields.One2many('hr.evaluation.point.education', 'hr_evaluation_point_id', string=u'نقاط التعليم')
    training_ids = fields.One2many('hr.evaluation.point.training', 'hr_evaluation_point_id', string=u'نقاط التدريب')
    functionality_ids = fields.One2many('hr.evaluation.point.functionality', 'hr_evaluation_point_id',
                                        string=u'نقاط  الإداء الوظيفي')
    max_point_seniority = fields.Integer(string=u'الحد الأقصى لنقاط الأقدمية', required=1)
    max_point_education = fields.Integer(string=u'الحد الأقصى لنقاط التعليم', required=1)
    max_point_training = fields.Integer(string=u'الحد الأقصى لنقاط التدريب', required=1)
    max_point_functionality = fields.Integer(string=u'الحد الأقصى لنقاط  الإداء الوظيفي', required=1)
    _sql_constraints = {
        ('grade_id_uniq', 'unique(grade_id)', ' اعدادات احتساب النقاط لهذه الرتبة موجود')
    }


class HrEvaluationPointSeniority(models.Model):
    _name = 'hr.evaluation.point.seniority'
    _description = 'seniority  Points'

    name = fields.Char(string=u'المسمى', required=1)
    hr_evaluation_point_id = fields.Many2one('hr.evaluation.point', string='المرتبة', )
    year_from = fields.Integer(string=u'من (سنة)', required=1)
    year_to = fields.Integer(string=u'إلى (سنة)', required=1)
    point = fields.Float(string=u'عدد النقاط', required=1)


class hr_evaluation_point_education(models.Model):
    _name = 'hr.evaluation.point.education'
    _description = 'education  Points'

    name = fields.Char(string=u'المسمى', required=1)
    hr_evaluation_point_id = fields.Many2one('hr.evaluation.point', string='المرتبة', )
    nature_education = fields.Selection(
        [('after_secondry', 'كل سنة دراسية بعد الثانوية'), ('before_secondry', 'كل سنة دراسية قبل الثانوية')],
        string='المؤهل', required=1)
    type_education = fields.Selection(
        [('in_speciality_job', 'في طبيعة العمل'), ('not_speciality_job', ' ليست في طبيعة العمل')],
        string='إختصاص الدراسة', required=1)
    year_point = fields.Float(string=u"نقاط في السنة", required=1)


class HrEvaluationPointTraining(models.Model):
    _name = 'hr.evaluation.point.training'
    _description = 'Training Points'

    name = fields.Char(string=u'المسمى', required=1)
    hr_evaluation_point_id = fields.Many2one('hr.evaluation.point', string='المرتبة')
    point = fields.Float(string=u"نقاط ", required=1)
    day_number = fields.Float(string=u" المدة باليوم", required=1)
    type_training = fields.Selection(
        [('direct_experience', 'الخبرات المباشرة'), ('indirect_experience', 'الخبرات غير المباشرة')],
        string='نوع التدريب', required=1)


# @api.depends('year_point', 'year_no')
#     def _calc_total(self):
#         for rec in self:
#             rec.total = rec.year_point * rec.year_no

class HrEvaluationPointFunctionality(models.Model):
    _name = 'hr.evaluation.point.functionality'
    _description = 'functionality Performance Points'

    hr_evaluation_point_id = fields.Many2one('hr.evaluation.point', string='المرتبة', )
    degree_id = fields.Many2one('hr.evaluation.result.foctionality', string='التقدير', )
    point = fields.Float(string=u"نقاط ", required=1)


class HrEvaluationResultFoctionality(models.Model):
    _name = 'hr.evaluation.result.foctionality'
    _description = u'إعدادات نتائج تقييم الوظيفي'

    name = fields.Char(string=u'النتيجة' )
    point_from = fields.Float(string=u"من درجة ", required=1)
    point_to = fields.Float(string=u"إلى درجة ", required=1)
