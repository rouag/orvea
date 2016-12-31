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
            result[i] = self.search( [('parent_id', 'child_of', i)], context=context)

        return result
    
    name = fields.Char(string=u'المسمى', required=1)
    parent_id = fields.Many2one('hr.groupe.job', ' المجموعة الأب', ondelete='cascade',  advanced_search=True)
    child_ids= fields.One2many('hr.groupe.job', 'parent_id', 'المجموعات الفرعية')
    all_child_ids= fields.Many2many(compute='_get_all_child_ids', type='many2many', relation='hr.groupe.job'),
    numero  = fields.Char(string=u'الرمز',)
    rank_from =fields.Integer(string=u'‫‬ ‫المرتبة‬ ‫من‬ ',)
    rank_to =fields.Integer(string=u'‫‬ ‫المرتبة ‬إلى‬',)
    instead_risk=fields.Boolean(string=u'بدل خطر')
    instead_damage=fields.Boolean(string=u' بدل ‫ضرر‬')
    instead_job_nature=fields.Boolean(string=u' بدل‫ طبيعة‬  ‫عمل‬ ')
    reward_postman=fields.Boolean(string=u'مكافأة موزع البريد')
    direct_public_funds_reward=fields.Boolean(string=u'مكافأة‬ مباشرة الأموال العامة')
    hr_training_ids=fields.One2many('hr.job.trainning', 'ategorie_serie_id', string=u'الدورات التدريبية',)
    hr_classment_job_ids=fields.One2many('hr.job.classment', 'ategorie_serie_id', string=u'الرتبة',)
    skils_ids = fields.Many2many('hr.skils.job', 'skills_job_rel', 'skil_id', 'job_id', string=u'المهارات‬ ‫و‬ ‫القدرات')
    type_groupe= fields.Selection([
        ('general', u'المجموعة العامة‬‬'),
        ('spicific', u'المجموعة النوعية '),
        ('serie', u'سلسلة الفئات'),
    ], string=u' ‫نوع‬ المجموعة ', )
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'لايمكن اظافة مجموعتين بنفس الإسم'),
        ('name_uniq', 'unique(numero)', 'لايمكن اظافة مجموعتين بنفس الرمز')
    ]
    
    
    @api.onchange('rank_to')
    def onchange_rank(self):
        print '1111'
        if self.rank_from <=0:
             raise ValidationError(u'يجب أن تكون المرتبة  أكبر من 0‬')
        if self.rank_from and self.rank_to:
            if self.rank_to - self.rank_from <=0 :
                    raise ValidationError(u'يجب أن تكون المرتبة ‬إلى أكبر من المرتبة‬ ‫من‬')
            else :
                classment_ids=[]
                i = self.rank_from 
                while  i <= self.rank_to :
                    classment_id=self.env['hr.job.classment'].create({'name': i,  }).id
                    classment_ids.append(classment_id)
                    i=i+1
            self.hr_classment_job_ids= classment_ids
    
#     @api.onchange('rank_from')
#     def onchange_rank(self):
#         if self.rank_from <=0:
#             raise ValidationError(u'يجب أن تكون المرتبة  أكبر من 0‬')
#            
        
    
    
# hr_job_description_ids=fields.One2many('hr.job.description', 'categorie_serie_id', string=u'مسمى ‬‫‫الفئة‬',readonly=1)
class HrJobTraining(models.Model):
    _name = 'hr.job.trainning'
    name = fields.Char(string=u' المسمى الدورات التدريبية ', required=1,related='traninig_id.name',readonly=1)
    ategorie_serie_id=fields.Many2one('hr.groupe.job', string=u'سلسلة الفئات‬')
    traninig_id=fields.Many2one('hr.training', string=u'الدورات التدريبية ', required=True ,)
    type= fields.Selection([
        ('direct', u'‫مباشرة‬'),
        ('in_direct', u' غير‬‬ ‫مباشرة‬ '),
        ('no_compte', u'لاتحتسب'),
    ], string=u' ‫نوع‬ ‫الدورة‬ ', default='direct')
    
    
class HrJobClassment(models.Model):
    _name = 'hr.job.classment'
    name = fields.Char(string=u'مسمى الرتبة', required=1,readonly=1)
    ategorie_serie_id=fields.Many2one('hr.groupe.job', string=u'سلسلة الفئات‬')
#     traninig_id=fields.Many2one('hr.training', string=u'الدورات التدريبية ', required=True ,)
    exeperince=fields.Char(string=u'سنوات الخبرة المطلوبة',)
    
#     _sql_constraints = [
#         ('name_uniq', 'unique(name)', 'لايمكن اظافة رتبتين بنفس الشهادة العلمية'),
#         ]
