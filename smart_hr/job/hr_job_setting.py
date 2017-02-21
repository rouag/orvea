# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date


class HrGrouupGeneral(models.Model):
    _name = 'hr.groupe.job'
    _description = u'‫المجموعة العامة‬‬'

    @api.multi
    def _get_all_child_ids(self, field_name, arg, context=None):
        result = dict.fromkeys(self._ids)
        for i in ids:
            result[i] = self.search([('parent_id', 'child_of', i)], context=context)
        return result

    name = fields.Char(string=u'المسمى', required=1)
    parent_id = fields.Many2one('hr.groupe.job', ' المجموعة الأب', ondelete='cascade')
    child_ids = fields.One2many('hr.groupe.job', 'parent_id', 'المجموعات الفرعية')
    all_child_ids = fields.Many2many(compute='_get_all_child_ids', type='many2many', relation='hr.groupe.job'),
    numero = fields.Char(string=u'الرمز',)
    rank_from = fields.Many2one('salary.grid.grade', string=u'‫‬ ‫المرتبة‬ ‫من‬ ')
    rank_to = fields.Many2one('salary.grid.grade', string=u'‫‬ ‫المرتبة ‬إلى‬')
    allowanse_ids = fields.Many2many('hr.allowance.type', string=u'البدلات')
    reward_postman = fields.Boolean(string=u'مكافأة موزع البريد')
    direct_public_funds_reward = fields.Boolean(string=u'مكافأة‬ مباشرة الأموال العامة')
    hr_training_ids = fields.One2many('hr.job.training', 'categorie_serie_id', string=u'الدورات التدريبية',)
    hr_classment_job_ids = fields.One2many('hr.job.classment', 'categorie_serie_id', string=u'الرتبة',)
    department_id = fields.Many2one('hr.department', string='الإدارة', )
    skils_ids = fields.Many2many('hr.skils.job', 'skills_job_rel', 'skil_id', 'job_id', string=u'المهارات‬ ‫و‬ ‫القدرات')
    job_name_ids = fields.Many2many('hr.job.name', string=u'المسميات الوظيفية')
    group_type = fields.Selection([
        ('general', u'المجموعة العامة‬‬'),
        ('spicific', u'المجموعة النوعية '),
        ('serie', u'سلسلة الفئات'),
    ], string=u' ‫نوع‬ المجموعة ', )
    type_exeprience = fields.Selection([
        ('direct', u'‫مباشرة‬‬‬'),
        ('theroric', u'‫نظيرة‬ '),
        ('excepted', u'‫مقبولة‬'),
    ], string=u' ‫نوعية‬ الخبرة‬ ‫', )

    _sql_constraints = [
        ('name_uniq', 'unique(numero,group_type)', 'لايمكن اظافة مجموعتين بنفس الإسم'),
    ]


class HrJobTraining(models.Model):
    _name = 'hr.job.training'
    name = fields.Char(string=u' المسمى الدورات التدريبية ', required=1, related='traninig_id.name', readonly=1)
    categorie_serie_id = fields.Many2one('hr.groupe.job', string=u'سلسلة الفئات‬')
    traninig_id = fields.Many2one('hr.training', string=u'الدورات التدريبية ', required=True)
    type = fields.Many2one('hr.training.type', string=u' ‫نوع‬ ‫الدورة‬ ')


class HrJobClassment(models.Model):
    _name = 'hr.job.classment'
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة',)
    name = fields.Char(string=u'مسمى الرتبة', related='grade_id.name',)
    categorie_serie_id = fields.Many2one('hr.groupe.job', string=u'سلسلة الفئات‬')
    education_level_id = fields.Many2one('hr.employee.education.level', string=u'المستوى التعليمي ')
    experience = fields.Integer(string=u'سنوات الخبرة المطلوبة',)

    _sql_constraints = [
        ('name_uniq', 'unique(name,education_level_id)', 'لايمكن اظافة رتبتين بنفس الشهادة العلمية')
    ]
