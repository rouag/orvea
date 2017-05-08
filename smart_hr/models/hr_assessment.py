# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class hr_assessment_probation(models.Model):
    _name = 'hr.assessment.probation'
    _description = 'Job Assessment Through Probation Period'

    name = fields.Char(string=u'رقم القرار', )
    date = fields.Date(string=u'التاريخ', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('eval_1', u'التقييم الاول'),
        ('eval_2', u'التقييم الثانى'),
        ('done', u'اعتمدت'),
    ], string=u'الحالة', default="draft")
    # Evaluation fields
    from_date_1 = fields.Date(string=u'تاريخ من')
    to_date_1 = fields.Date(string=u'تاريخ الى')
    enthusiasm_1 = fields.Integer(string=u'الحماس في العمل', default=1)
    learn_1 = fields.Integer(string=u'القدرته علي التعلم', default=1)
    guidance_1 = fields.Integer(string=u'تقبل و استيعاب التوجيه', default=1)
    worktime_1 = fields.Integer(string=u'المحافظة على اوقات الدوام', default=1)
    behavior_1 = fields.Integer(string=u'السلوك العام', default=1)
    conduct_1 = fields.Integer(string=u'حسن التصرف', default=1)
    relation_1 = fields.Integer(string=u'العلاقات مع الرؤساء و الزملاء و المراجعين', default=1)
    eval_total_1 = fields.Integer(string=u'مجموع التقييم الاول', compute='_calc_eval_1')
    ###
    from_date_2 = fields.Date(string=u'تاريخ من')
    to_date_2 = fields.Date(string=u'تاريخ الى')
    enthusiasm_2 = fields.Integer(string=u'الحماس في العمل', default=1)
    learn_2 = fields.Integer(string=u'القدرته علي التعلم', default=1)
    guidance_2 = fields.Integer(string=u'تقبل و استيعاب التوجيه', default=1)
    worktime_2 = fields.Integer(string=u'المحافظة على اوقات الدوام', default=1)
    behavior_2 = fields.Integer(string=u'السلوك العام', default=1)
    conduct_2 = fields.Integer(string=u'حسن التصرف', default=1)
    relation_2 = fields.Integer(string=u'العلاقات مع الرؤساء و الزملاء و المراجعين', default=1)
    eval_total_2 = fields.Integer(string=u'مجموع التقييم الثانى', compute='_calc_eval_2')
    ###
    total_score = fields.Integer(string=u'الإجمــالي', compute='_calc_eval_total')
    performance_report = fields.Char(string=u'الاداء العام', compute='_calc_eval_total')

    @api.one
    @api.constrains('enthusiasm_1', 'learn_1', 'guidance_1', 'worktime_1', 'behavior_1', 'conduct_1', 'relation_1',
                    'enthusiasm_2', 'learn_2', 'guidance_2', 'worktime_2', 'behavior_2', 'conduct_2', 'relation_2',
                    'state')
    def constraint_scores(self):
        if self.state == 'eval_1':
            if not (1 <= self.enthusiasm_1 <= 10):
                raise ValidationError(u"'الحماس في العمل' يجب أن تكون القيمة ما بين 1 و 10.")
            if not (1 <= self.learn_1 <= 9):
                raise ValidationError(u"'القدرته علي التعلم' يجب أن تكون القيمة ما بين 1 و 9.")
            if not (1 <= self.guidance_1 <= 8):
                raise ValidationError(u"'تقبل و استيعاب التوجيه' يجب أن تكون القيمة ما بين 1 و 8.")
            if not (1 <= self.worktime_1 <= 7):
                raise ValidationError(u"'المحافظة على اوقات الدوام' يجب أن تكون القيمة ما بين 1 و 7.")
            if not (1 <= self.behavior_1 <= 7):
                raise ValidationError(u"'السلوك العام' يجب أن تكون القيمة ما بين 1 و 7.")
            if not (1 <= self.conduct_1 <= 5):
                raise ValidationError(u"'حسن التصرف' يجب أن تكون القيمة ما بين 1 و 5.")
            if not (1 <= self.relation_1 <= 4):
                raise ValidationError(u"'العلاقات مع الرؤساء و الزملاء و المراجعين' يجب أن تكون القيمة ما بين 1 و 4.")
        elif self.state == 'eval_2':
            if not (1 <= self.enthusiasm_2 <= 10):
                raise ValidationError(u"'الحماس في العمل' يجب أن تكون القيمة ما بين 1 و 10.")
            if not (1 <= self.learn_2 <= 9):
                raise ValidationError(u"'القدرته علي التعلم' يجب أن تكون القيمة ما بين 1 و 9.")
            if not (1 <= self.guidance_2 <= 8):
                raise ValidationError(u"'تقبل و استيعاب التوجيه' يجب أن تكون القيمة ما بين 1 و 8.")
            if not (1 <= self.worktime_2 <= 7):
                raise ValidationError(u"'المحافظة على اوقات الدوام' يجب أن تكون القيمة ما بين 1 و 7.")
            if not (1 <= self.behavior_2 <= 7):
                raise ValidationError(u"'السلوك العام' يجب أن تكون القيمة ما بين 1 و 7.")
            if not (1 <= self.conduct_2 <= 5):
                raise ValidationError(u"'حسن التصرف' يجب أن تكون القيمة ما بين 1 و 5.")
            if not (1 <= self.relation_2 <= 4):
                raise ValidationError(u"'العلاقات مع الرؤساء و الزملاء و المراجعين' يجب أن تكون القيمة ما بين 1 و 4.")

    @api.depends('enthusiasm_1', 'learn_1', 'guidance_1', 'worktime_1',
                 'behavior_1', 'conduct_1', 'relation_1')
    def _calc_eval_1(self):
        for rec in self:
            rec.eval_total_1 = (rec.enthusiasm_1 or 1) + (rec.learn_1 or 1) \
                               + (rec.guidance_1 or 1) + (rec.worktime_1 or 1) \
                               + (rec.behavior_1 or 1) + (rec.conduct_1 or 1) \
                               + (rec.relation_1 or 1)

    @api.depends('enthusiasm_2', 'learn_2', 'guidance_2', 'worktime_2',
                 'behavior_2', 'conduct_2', 'relation_2')
    def _calc_eval_2(self):
        for rec in self:
            rec.eval_total_2 = (rec.enthusiasm_2 or 1) + (rec.learn_2 or 1) \
                               + (rec.guidance_2 or 1) + (rec.worktime_2 or 1) \
                               + (rec.behavior_2 or 1) + (rec.conduct_2 or 1) \
                               + (rec.relation_2 or 1)

    @api.depends('eval_total_1', 'eval_total_2')
    def _calc_eval_total(self):
        job_perf_obj = self.env['hr.assessment.point.job']
        def get_grade(value):
            domain = [
                ('eval_type', '=', 'probation_period'),
            ]
            job_perf = job_perf_obj.search(domain)
            for jp in job_perf:
                if jp.point_from <= value <= jp.point_to:
                    return jp.eval_name
        for rec in self:
            rec.total_score = (rec.eval_total_1 or 0.0) + (rec.eval_total_2 or 0.0)
            if rec.total_score:
                rec.performance_report = get_grade(rec.total_score)

    @api.model
    def create(self, vals):
        ret = super(hr_assessment_probation, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.assess.prob.seq')
        ret.write(vals)
        return ret

    @api.one
    def button_eval_1(self):
        for eval in self:
            eval.state = 'eval_1'

    @api.one
    def button_eval_2(self):
        for eval in self:
            eval.state = 'eval_2'

    @api.one
    def button_done(self):
        for eval in self:
            eval.state = 'done'

class hr_assessment_users(models.Model):
    _name = 'hr.assessment.users'
    _description = 'Job Assessment for Users, Temporary Jobs and Employees on Wages'

    name = fields.Char(string=u'رقم القرار', )
    date = fields.Date(string=u'التاريخ', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('done', u'اعتمدت'),
    ], string=u'الحالة', default="draft")
    # Evaluation Fields
    work_performance_score = fields.Integer(string=u'مستوى اداء العمل', default=1)
    maintain_worktime_score = fields.Integer(string=u'المحافظة على اوقات الدوام', default=1)
    guidance_score = fields.Integer(string=u'تقبل و استيعاب التوجيه', default=1)
    superiors_score = fields.Integer(string=u'التعامل مع الرؤساء', default=1)
    colleagues_score = fields.Integer(string=u'التعامل مع الزملاء', default=1)
    audit_score = fields.Integer(string=u'التعامل مع المراجعين', default=1)
    ###
    total_score = fields.Integer(string=u'مجموع نقاط', compute="_calc_total_score")
    performance_report = fields.Char(string=u'الاداء العام', compute="_calc_total_score")
    last_performance_report = fields.Char(string=u"آخر أداء")

    @api.depends('work_performance_score', 'maintain_worktime_score', 'guidance_score',
                 'superiors_score', 'colleagues_score', 'audit_score')
    def _calc_total_score(self):
        job_perf_obj = self.env['hr.assessment.point.job']
        def get_grade(value):
            domain = [
                ('eval_type', '=', 'user_temp_job'),
            ]
            job_perf = job_perf_obj.search(domain)
            for jp in job_perf:
                if value >= jp.point_from and value <= jp.point_to:
                    return jp.eval_name
        for rec in self:
            rec.total_score = (rec.work_performance_score or 1) + (rec.maintain_worktime_score or 1) \
                               + (rec.guidance_score or 1) + (rec.superiors_score or 1) \
                               + (rec.colleagues_score or 1) + (rec.audit_score or 1)
            if rec.total_score:
                rec.performance_report = get_grade(rec.total_score)

    @api.one
    @api.constrains('work_performance_score', 'maintain_worktime_score', 'guidance_score',
                 'superiors_score', 'colleagues_score', 'audit_score', 'state')
    def constraint_scores(self):
        if self.state == 'draft':
            if not (1 <= self.work_performance_score <= 6):
                raise ValidationError(u"'مستوى اداء العمل:' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.maintain_worktime_score <= 6):
                raise ValidationError(u"'المحافظة على اوقات الدوام' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.guidance_score <= 6):
                raise ValidationError(u"'تقبل و استيعاب التوجيه' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.superiors_score <= 6):
                raise ValidationError(u"'التعامل مع الرؤساء' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.colleagues_score <= 6):
                raise ValidationError(u"'التعامل مع الزملاء' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.audit_score <= 6):
                raise ValidationError(u"'التعامل مع المراجعين' يجب أن تكون القيمة ما بين 1 و 6.")

    @api.model
    def create(self, vals):
        ret = super(hr_assessment_users, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.assess.users.seq')
        ret.write(vals)
        return ret

    @api.one
    def button_done(self):
        for eval in self:
            eval.state = 'done'

class hr_assessment_specialized(models.Model):
    _name = 'hr.assessment.specialized'
    _description = 'Job Assessment for Specialized Jobs'

    name = fields.Char(string=u'رقم القرار', )
    date = fields.Date(string=u'التاريخ', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    category_type = fields.Selection([
        ('a', u'أ'),
        ('b', u'ب'),
    ], string=u'الفئة', default='a')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('done', u'اعتمدت'),
    ], string=u'الحالة', default='draft')
    # Evaluation
    goal_understand = fields.Integer(string=u'التفهم لاهداف الجهاز', default=1)
    skill_plan = fields.Integer(string=u'المهارة فى التخطيط', default=1)
    skill_decision = fields.Integer(string=u'المهارة فى اتخاذ القرار', default=1)
    skill_supervision = fields.Integer(string=u'المهارة فى الاشراف الفنى', default=1)
    performance_specialization = fields.Integer(string=u'مستوى الاداء فى مجال التخصص', default=1)
    follow_specialization = fields.Integer(string=u'المتابعة لما يستجد فى مجال التخصص', default=1)
    high_responsibilities = fields.Integer(string=u'امكانية تحمل مسئولية اعلى', default=1)
    knowing_system = fields.Integer(string=u'المعرفة بنظم واجراءات العمل', default=1)
    work_method = fields.Integer(string=u'القدرة على تطوير اساليب العمل', default=1)
    maintain_work_hours = fields.Integer(string=u'المحافظة على اوقات الدوام', default=1)
    safety_prevention = fields.Integer(string=u'الحرص على امور السلامة والوقاية', default=1)
    careful_work = fields.Integer(string=u'توخى الدقة فى العمل', default=1)
    total_eval = fields.Integer(string=u'مجموع نقاط التقييم الوظائف', compute='_calc_eval')
    # Personal traits
    good_conduct = fields.Integer(string=u'حسن التصرف', default=1)
    reliance_degree = fields.Integer(string=u'درجة الاعتماد عليه/عليها', default=1)
    appearance_care = fields.Integer(string=u'الاهتمام بالمظهر', default=1)
    accept_process = fields.Integer(string=u'تقبل التجديد فى اساليب العمل', default=1)
    total_personal_traits = fields.Integer(string=u'مجموع نقاط صفات الشخصية', compute='_calc_personal_traits')
    # Relationships with others
    superiors = fields.Integer(string=u'الرؤساء', default=1)
    colleagues = fields.Integer(string=u'الزملاء', default=1)
    public = fields.Integer(string=u'الجمهور', default=1)
    total_relationships = fields.Integer(string=u'مجموع نقاط العلاقات مع الآخرين', compute='_calc_relationships')
    # General Notes
    strengths_ids = fields.One2many('hr.assessment.specialized.strength', 'assessment_specialized_id', string=u'نقاط القوة')
    weaknesses_ids = fields.One2many('hr.assessment.specialized.weakness', 'assessment_specialized_id', string=u'نقاط الضعف')
    total_general = fields.Integer(string=u'مجموع نقاط الملاحظات العامة', compute='_calc_general')
    # Total
    total_score = fields.Integer(string=u'الإجمــالي', compute="_calc_total_score")
    performance_report = fields.Char(string=u'الاداء العام', compute="_calc_total_score")
    last_report = fields.Selection([
        ('good', u'جيد'),
        ('average', u'متوسط'),
        ('weak', u'ضعيف'),
    ], string=u'مقدار التحسن منذ التقرير الأخير')
    recommendations = fields.Text(string=u'التوصيات العامة لتطوير قدرات الموظف')
    notes = fields.Text(string=u'ملاحظات')

    @api.model
    def create(self, vals):
        ret = super(hr_assessment_specialized, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.assess.spec.seq')
        ret.write(vals)
        return ret

    @api.depends('goal_understand', 'skill_plan', 'skill_decision', 'skill_supervision',
                 'performance_specialization', 'follow_specialization', 'high_responsibilities',
                 'knowing_system', 'work_method', 'maintain_work_hours', 'safety_prevention', 'careful_work',
                 'category_type')
    def _calc_eval(self):
        for rec in self:
            rec.total_eval = (rec.goal_understand if rec.category_type == 'a' else 0.0) \
                            + (rec.skill_plan if rec.category_type == 'a' else 0.0) \
                            + (rec.skill_decision if rec.category_type == 'a' else 0.0) \
                            + (rec.skill_supervision or 0.0) + (rec.performance_specialization or 0.0) \
                            + (rec.follow_specialization or 0.0) + (rec.high_responsibilities or 0.0) \
                            + (rec.knowing_system or 0.0) + (rec.work_method or 0.0) \
                            + (rec.maintain_work_hours or 0.0) + (rec.safety_prevention or 0.0) \
                            + (rec.careful_work if rec.category_type == 'b' else 0.0)

    @api.one
    @api.constrains('goal_understand', 'skill_plan', 'skill_decision', 'skill_supervision',
                    'performance_specialization', 'follow_specialization', 'high_responsibilities',
                    'knowing_system', 'work_method', 'maintain_work_hours', 'safety_prevention',
                    'careful_work', 'state')
    def constraint_eval(self):
        if self.state == 'draft':
            if not (1 <= self.goal_understand <= 6):
                raise ValidationError(u"'التفهم لاهداف الجهاز' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.skill_plan <= 6):
                raise ValidationError(u"'المهارة فى التخطيط' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.skill_decision <= 6):
                raise ValidationError(u"'المهارة فى اتخاذ القرار' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.skill_supervision <= 6):
                raise ValidationError(u"'المهارة فى الاشراف الفنى' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.performance_specialization <= 6):
                raise ValidationError(u"'مستوى الاداء فى مجال التخصص' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.follow_specialization <= 6):
                raise ValidationError(u"'المتابعة لما يستجد فى مجال التخصص' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.high_responsibilities <= 6):
                raise ValidationError(u"'امكانية تحمل مسئولية اعلى' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.knowing_system <= 6):
                raise ValidationError(u"'المعرفة بنظم واجراءات العمل' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.work_method <= 6):
                raise ValidationError(u"'القدرة على تطوير اساليب العمل' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.maintain_work_hours <= 6):
                raise ValidationError(u"'المحافظة على اوقات الدوام' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.safety_prevention <= 6):
                raise ValidationError(u"'الحرص على امور السلامة والوقاية' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.careful_work <= 6):
                raise ValidationError(u"'توخى الدقة فى العمل' يجب أن تكون القيمة ما بين 1 و 6.")

    @api.depends('good_conduct', 'reliance_degree', 'appearance_care', 'accept_process', 'category_type')
    def _calc_personal_traits(self):
        for rec in self:
            rec.total_personal_traits = (rec.good_conduct or 0.0) + (rec.reliance_degree or 0.0) \
                                    + (rec.appearance_care if rec.category_type == 'b' else 0.0) \
                                    + (rec.accept_process if rec.category_type == 'b' else 0.0)

    @api.one
    @api.constrains('good_conduct', 'reliance_degree', 'appearance_care', 'accept_process', 'state')
    def constraint_personal_traits(self):
        if self.state == 'draft':
            if not (1 <= self.good_conduct <= 6):
                raise ValidationError(u"'حسن التصرف' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.reliance_degree <= 6):
                raise ValidationError(u"'درجة الاعتماد عليه/عليها' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.appearance_care <= 6):
                raise ValidationError(u"'الاهتمام بالمظهر' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.accept_process <= 6):
                raise ValidationError(u"'تقبل التجديد فى اساليب العمل' يجب أن تكون القيمة ما بين 1 و 6.")

    @api.depends('superiors', 'colleagues', 'public', 'category_type')
    def _calc_relationships(self):
        for rec in self:
            rec.total_relationships = (rec.superiors or 0.0) + (rec.colleagues or 0.0) + (rec.public or 0.0)

    @api.one
    @api.constrains('superiors', 'colleagues', 'public', 'state')
    def constraint_relationships(self):
        if self.state == 'draft':
            if not (1 <= self.superiors <= 6):
                raise ValidationError(u"'الرؤساء' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.colleagues <= 6):
                raise ValidationError(u"'الزملاء' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.public <= 6):
                raise ValidationError(u"'الجمهور' يجب أن تكون القيمة ما بين 1 و 6.")

    @api.depends('strengths_ids.point', 'weaknesses_ids.point', 'category_type')
    def _calc_general(self):
        total = 0.0
        for rec in self:
            for sline in rec.strengths_ids:
                total += sline.point
            for wline in rec.weaknesses_ids:
                total += wline.point
            rec.total_general = (total or 0.0)

    @api.one
    @api.constrains('strengths_ids', 'weaknesses_ids', 'state')
    def constraint_general(self):
        if self.state == 'draft':
            if len(self.strengths_ids.ids) > 3:
                raise ValidationError(u"فقط 3 نقاط المسموح بها في 'نقاط القوة'.")
            if len(self.weaknesses_ids.ids) > 3:
                raise ValidationError(u"فقط 3 نقاط المسموح بها في 'نقاط الضعف'.")

    @api.depends('total_general', 'total_relationships', 'total_personal_traits', 'total_eval',
                 'category_type')
    def _calc_total_score(self):
        job_perf_obj = self.env['hr.assessment.point.job']
        def get_grade(value):
            domain = [
                ('eval_type', '=', 'special_job'),
            ]
            job_perf = job_perf_obj.search(domain)
            for jp in job_perf:
                if jp.point_from <= value <= jp.point_to:
                    return jp.eval_name
        for rec in self:
            rec.total_score = (rec.total_general or 0.0) + (rec.total_relationships or 0.0) \
                               + (rec.total_personal_traits or 0.0) + (rec.total_eval or 0.0)
            if rec.total_score:
                rec.performance_report = get_grade(rec.total_score)

    @api.one
    def button_done(self):
        for eval in self:
            eval.state = 'done'

class hr_assessment_specialized_strength(models.Model):
    _name = 'hr.assessment.specialized.strength'
    _description = 'Job Assessment for Specialized Jobs Strengths'

    name = fields.Char(string=u'الوصف')
    point = fields.Integer(string=u'النقاط', compute="_set_points", store=True)
    assessment_specialized_id = fields.Many2one('hr.assessment.specialized', string='Job assessment Ref.')
    assessment_veterinary_medicine_id = fields.Many2one('hr.assessment.veterinary.medicine', string='Job assessment Ref.')
    assessment_executive_admin_id = fields.Many2one('hr.assessment.executive.admin', string='Job assessment Ref.')

    @api.depends('name')
    def _set_points(self):
        for rec in self:
            rec.point = 3.0

class hr_assessment_specialized_weakness(models.Model):
    _name = 'hr.assessment.specialized.weakness'
    _description = 'Job Assessment for Specialized Jobs Weaknesses'

    name = fields.Char(string=u'الوصف')
    point = fields.Integer(string=u'النقاط', compute="_set_points", store=True)
    assessment_specialized_id = fields.Many2one('hr.assessment.specialized', string='Job assessment Ref.')
    assessment_veterinary_medicine_id = fields.Many2one('hr.assessment.veterinary.medicine', string='Job assessment Ref.')
    assessment_executive_admin_id = fields.Many2one('hr.assessment.executive.admin', string='Job assessment Ref.')

    @api.depends('name')
    def _set_points(self):
        for rec in self:
            rec.point = -3.0

class hr_assessment_veterinary_medicine(models.Model):
    _name = 'hr.assessment.veterinary.medicine'
    _description = "Job Assessment for Veterinary Medicine Jobs"

    name = fields.Char(string=u'رقم القرار', )
    date = fields.Date(string=u'التاريخ', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    form_type = fields.Selection([
        ('below', u'10 فما دون'),
        ('above', u'11 و 12 و 13'),
    ], string=u'نوع النموذج', default='below')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('done', u'اعتمدت'),
    ], string=u'الحالة', default='draft')
    # Evaluation
    skill_monitor = fields.Integer(string=u'المهارة فى المتابعة والتوجيه', default=1)
    ability_train = fields.Integer(string=u'القدرة على تدريب غيره من العاملين', default=1)
    ability_improve = fields.Integer(string=u'القدرة على تطوير اساليب العمل', default=1)
    goal_understand = fields.Integer(string=u'التفهم لاهداف الجهاز', default=1)
    know_work = fields.Integer(string=u'المعرفة بالاسس والمفاهيم المتعلقة بالعمل', default=1)
    know_system = fields.Integer(string=u'المعرفة بنظم العمل واجراءاته', default=1)
    ability_overcome = fields.Integer(string=u'القدرة على التغلب على صعوبات العمل', default=1)
    ability_research = fields.Integer(string=u'القدرة على اعداد الدراسات والبحوث', default=1)
    high_responsibilities = fields.Integer(string=u'امكانية تحمل مسئولية اعلى', default=1)
    maintain_work_hours = fields.Integer(string=u'المحافظة على اوقات الدوام', default=1)
    ability_communication = fields.Integer(string=u'القدرة على اقامة اتصالات فعالة مع الاخرين', default=1)
    follow_specialization = fields.Integer(string=u'المتابعة لما يستجد فى مجال التخصص', default=1)
    skill_report = fields.Integer(string=u'المهارة فى اعداد التقارير', default=1)
    ability_diagnose = fields.Integer(string=u'القدرة على تشخيص امراض الحيوانات وتحديد العلاج المناسب', default=1)
    ability_epidemic = fields.Integer(string=u'القدرة على اتخاذ الترتيبات اللازمة للقضاء على الامراض الوبائية', default=1)
    field_visit = fields.Integer(string=u'القيام بالزيارات الميدانية وعمليات التوجيه والارشاد', default=1)
    know_equipments = fields.Integer(string=u'المعرفة بالطرق السليمة لعمل الاجهزة والمواد المستخدمة', default=1)
    special_uniform = fields.Integer(string=u'التقيد بالزى الخاص بالعمل وتطبيك اسس السلامة', default=1)
    total_eval = fields.Integer(string=u'مجموع نقاط التقييم الوظائف', compute='_calc_total_eval')
    # Personal traits
    ability_dialogue = fields.Integer(string=u'القدرة على الحوار وعرض الراى', default=1)
    responsibility_appreciation = fields.Integer(string=u'تقدير المسئولية', default=1)
    good_conduct = fields.Integer(string=u'حسن التصرف', default=1)
    accept_guidance = fields.Integer(string=u'تقبل التوجيهات والاستعداد لتنفيذها', default=1)
    appearance_care = fields.Integer(string=u'الاهتمام بالمظهر', default=1)
    total_personal_traits = fields.Integer(string=u'مجموع نقاط صفات الشخصية', compute='_calc_personal_traits')
    # Relations with others
    superiors = fields.Integer(string=u'الرؤساء', default=1)
    colleagues = fields.Integer(string=u'الزملاء', default=1)
    subordinates = fields.Integer(string=u'المرؤوسين', default=1)
    total_relationships = fields.Integer(string=u'مجموع نقاط العلاقات مع الآخرين', compute='_calc_relationships')
    # General Notes
    strengths_ids = fields.One2many('hr.assessment.specialized.strength', 'assessment_veterinary_medicine_id', string=u'نقاط القوة')
    weaknesses_ids = fields.One2many('hr.assessment.specialized.weakness', 'assessment_veterinary_medicine_id', string=u'نقاط الضعف')
    total_general = fields.Integer(string=u'مجموع نقاط الملاحظات العامة', compute='_calc_general')
    # Total
    total_score = fields.Integer(string=u'الإجمــالي', compute="_calc_total_score")
    performance_report = fields.Char(string=u'الاداء العام', compute="_calc_total_score")
    last_report = fields.Selection([
        ('good', u'جيد'),
        ('average', u'متوسط'),
        ('weak', u'ضعيف'),
    ], string=u'مقدار التحسن منذ التقرير الأخير')
    recommendations = fields.Text(string=u'التوصيات العامة لتطوير قدرات الموظف')
    notes = fields.Text(string=u'ملاحظات')

    @api.model
    def create(self, vals):
        ret = super(hr_assessment_veterinary_medicine, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.assess.vet.seq')
        ret.write(vals)
        return ret

    @api.one
    def button_done(self):
        for eval in self:
            eval.state = 'done'

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.job_id and rec.employee_id.job_id.level > 10:
                rec.form_type = 'above'
            elif rec.employee_id and rec.employee_id.job_id and rec.employee_id.job_id.level <= 10:
                rec.form_type = 'below'

    @api.depends('skill_monitor', 'ability_train', 'ability_improve', 'goal_understand',
                    'know_work', 'know_system', 'ability_overcome', 'ability_research',
                    'high_responsibilities', 'maintain_work_hours', 'ability_communication',
                    'follow_specialization', 'skill_report', 'ability_diagnose', 'ability_epidemic',
                    'field_visit', 'know_equipments', 'special_uniform', 'form_type')
    def _calc_total_eval(self):
        for rec in self:
            rec.total_eval = (rec.skill_monitor if rec.form_type == 'above' else 0.0) \
                            + (rec.ability_train if rec.form_type == 'above' else 0.0) \
                            + (rec.ability_improve if rec.form_type == 'above' else 0.0) \
                            + (rec.goal_understand or 0.0) + (rec.know_work or 0.0) \
                            + (rec.know_system or 0.0) + (rec.ability_overcome or 0.0) \
                            + (rec.ability_research or 0.0) + (rec.high_responsibilities or 0.0) \
                            + (rec.maintain_work_hours or 0.0) + (rec.ability_communication or 0.0) \
                            + (rec.follow_specialization or 0.0) + (rec.skill_report or 0.0) \
                            + (rec.ability_diagnose or 0.0) + (rec.ability_epidemic or 0.0) \
                            + (rec.field_visit or 0.0) + (rec.know_equipments or 0.0) \
                            + (rec.special_uniform or 0.0)

    @api.depends('ability_dialogue', 'responsibility_appreciation',
                 'good_conduct', 'accept_guidance',
                 'appearance_care')
    def _calc_personal_traits(self):
        for rec in self:
            rec.total_personal_traits = (rec.ability_dialogue or 0.0) + (rec.responsibility_appreciation or 0.0) \
                                    + (rec.good_conduct or 0.0) + (rec.accept_guidance or 0.0) \
                                    + (rec.appearance_care or 0.0)

    @api.depends('superiors', 'colleagues', 'subordinates')
    def _calc_relationships(self):
        for rec in self:
            rec.total_relationships = (rec.superiors or 0.0) + (rec.colleagues or 0.0) + (rec.subordinates or 0.0)

    @api.depends('strengths_ids.point', 'weaknesses_ids.point')
    def _calc_general(self):
        total = 0.0
        for rec in self:
            for sline in rec.strengths_ids:
                total += sline.point
            for wline in rec.weaknesses_ids:
                total += wline.point
            rec.total_general = (total or 0.0)

    @api.depends('total_general', 'total_relationships',
                 'total_personal_traits', 'total_eval')
    def _calc_total_score(self):
        job_perf_obj = self.env['hr.assessment.point.job']
        def get_grade(form_type, value):
            if form_type == 'below':
                domain = [
                    ('eval_type', '=', 'veterinary_10'),
                ]
            else:
                domain = [
                    ('eval_type', '=', 'veterinary_11_12_13'),
                ]
            job_perf = job_perf_obj.search(domain)
            for jp in job_perf:
                if jp.point_from <= value <= jp.point_to:
                    return jp.eval_name
        for rec in self:
            rec.total_score = (rec.total_general or 0.0) + (rec.total_relationships or 0.0) \
                               + (rec.total_personal_traits or 0.0) + (rec.total_eval or 0.0)
            if rec.total_score:
                rec.performance_report = get_grade(rec.form_type, rec.total_score)

    @api.one
    @api.constrains('strengths_ids', 'weaknesses_ids', 'state')
    def constraint_general(self):
        if self.state == 'draft':
            if len(self.strengths_ids.ids) > 3:
                raise ValidationError(u"فقط 3 نقاط المسموح بها في 'نقاط القوة'.")
            if len(self.weaknesses_ids.ids) > 3:
                raise ValidationError(u"فقط 3 نقاط المسموح بها في 'نقاط الضعف'.")

    @api.one
    @api.constrains('superiors', 'colleagues', 'subordinates')
    def constraint_relationships(self):
        if self.state == 'draft':
            if not (1 <= self.superiors <= 3):
                raise ValidationError(u"'الرؤساء' يجب أن تكون القيمة ما بين 1 و 3.")
            if not (1 <= self.colleagues <= 3):
                raise ValidationError(u"'الزملاء' يجب أن تكون القيمة ما بين 1 و 3.")
            if not (1 <= self.subordinates <= 3):
                raise ValidationError(u"'المرؤوسين' يجب أن تكون القيمة ما بين 1 و 3.")

    @api.one
    @api.constrains('ability_dialogue', 'responsibility_appreciation',
                    'good_conduct', 'accept_guidance',
                    'appearance_care', 'state')
    def constraint_personal_traits(self):
        if self.state == 'draft':
            if not (1 <= self.ability_dialogue <= 4):
                raise ValidationError(u"'القدرة على الحوار وعرض الراى' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.responsibility_appreciation <= 4):
                raise ValidationError(u"'تقدير المسئولية' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.good_conduct <= 4):
                raise ValidationError(u"'حسن التصرف' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.accept_guidance <= 4):
                raise ValidationError(u"'تقبل التوجيهات والاستعداد لتنفيذها' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.appearance_care <= 3):
                raise ValidationError(u"'الاهتمام بالمظهر' يجب أن تكون القيمة ما بين 1 و 3.")

    @api.one
    @api.constrains('skill_monitor', 'ability_train', 'ability_improve', 'goal_understand',
                    'know_work', 'know_system', 'ability_overcome', 'ability_research',
                    'high_responsibilities', 'maintain_work_hours', 'ability_communication',
                    'follow_specialization', 'skill_report', 'ability_diagnose', 'ability_epidemic',
                    'field_visit', 'know_equipments', 'special_uniform', 'state')
    def constraint_eval(self):
        if self.state == 'draft':
            if not (1 <= self.skill_monitor <= 4):
                raise ValidationError(u"'المهارة فى المتابعة والتوجيه' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.ability_train <= 4):
                raise ValidationError(u"'القدرة على تدريب غيره من العاملين' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.ability_improve <= 4):
                raise ValidationError(u"'القدرة على تطوير اساليب العمل' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.goal_understand <= 4):
                raise ValidationError(u"'التفهم لاهداف الجهاز' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.know_work <= 3):
                raise ValidationError(u"'المعرفة بالاسس والمفاهيم المتعلقة بالعمل' يجب أن تكون القيمة ما بين 1 و 3.")
            if not (1 <= self.know_system <= 3):
                raise ValidationError(u"'المعرفة بنظم العمل واجراءاته' يجب أن تكون القيمة ما بين 1 و 3.")
            if not (1 <= self.ability_overcome <= 4):
                raise ValidationError(u"'القدرة على التغلب على صعوبات العمل' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.ability_research <= 4):
                raise ValidationError(u"'القدرة على اعداد الدراسات والبحوث' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.high_responsibilities <= 3):
                raise ValidationError(u"'امكانية تحمل مسئولية اعلى' يجب أن تكون القيمة ما بين 1 و 3.")
            if not (1 <= self.maintain_work_hours <= 5):
                raise ValidationError(u"'المحافظة على اوقات الدوام' يجب أن تكون القيمة ما بين 1 و 5.")
            if not (1 <= self.ability_communication <= 3):
                raise ValidationError(u"'القدرة على اقامة اتصالات فعالة مع الاخرين' يجب أن تكون القيمة ما بين 1 و 3.")
            if not (1 <= self.follow_specialization <= 3):
                raise ValidationError(u"'المتابعة لما يستجد فى مجال التخصص' يجب أن تكون القيمة ما بين 1 و 3.")
            if not (1 <= self.skill_report <= 3):
                raise ValidationError(u"'المهارة فى اعداد التقارير' يجب أن تكون القيمة ما بين 1 و 3.")
            if not (1 <= self.ability_diagnose <= 6):
                raise ValidationError(u"'القدرة على تشخيص امراض الحيوانات وتحديد العلاج المناسب' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.ability_epidemic <= 6):
                raise ValidationError(u"'القدرة على اتخاذ الترتيبات اللازمة للقضاء على الامراض الوبائية' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.field_visit <= 6):
                raise ValidationError(u"'القيام بالزيارات الميدانية وعمليات التوجيه والارشاد' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.know_equipments <= 3):
                raise ValidationError(u"'المعرفة بالطرق السليمة لعمل الاجهزة والمواد المستخدمة' يجب أن تكون القيمة ما بين 1 و 3.")
            if not (1 <= self.special_uniform <= 4):
                raise ValidationError(u"'التقيد بالزى الخاص بالعمل وتطبيك اسس السلامة' يجب أن تكون القيمة ما بين 1 و 4.")

class hr_assessment_executive(models.Model):
    _name = 'hr.assessment.executive'
    _description = 'Job Assessment for Executive Jobs'

    name = fields.Char(string=u'رقم القرار', )
    date = fields.Date(string=u'التاريخ', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    form_type = fields.Selection([
        ('a', u'11 و 12 و 13'),
        ('b', u'10 فما دون'),
    ], string=u'نوع النموذج ', default='b')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('done', u'اعتمدت'),
    ], string=u'الحالة', default='draft')
    # Evaluation
    ability_improve = fields.Integer(string=u'القدرة على تطوير اساليب العمل', default=1)
    ability_train = fields.Integer(string=u'القدرة على تدريب غيره من العاملين', default=1)
    ability_completion_work = fields.Integer(string=u'القدرة على تحديد متطلبات إنجاز العمل', default=1)
    skill_execution = fields.Integer(string=u'المهارة في التنفيذ', default=1)
    ability_timetable = fields.Integer(string=u'القدرة على تحديد خطوات العمل والبرنامج الزمني', default=1)
    maintain_worktime_score = fields.Integer(string=u'المحافظة على اوقات الدوام', default=1)
    implementation_safety = fields.Integer(string=u'تطبيق أسس السلامة المعتمدة في العمل', default=1)
    know_equipments = fields.Integer(string=u'المعرفة بالطرق السليمة لعمل الاجهزة والمواد المستخدمة', default=1)
    know_work = fields.Integer(string=u'المعرفة بالاسس والمفاهيم المتعلقة بالعمل', default=1)
    ability_overcome = fields.Integer(string=u'القدرة على التغلب على صعوبات العمل', default=1)
    followup_developments_work = fields.Integer(string=u'المتابعة لما يستجد فى مجال العمل', default=1)
    ability_communication = fields.Integer(string=u'القدرة على اقامة اتصالات فعالة مع الاخرين', default=1)
    high_responsibilities = fields.Integer(string=u'امكانية تحمل مسئولية اعلى', default=1)
    knowing_system = fields.Integer(string=u'المعرفة بنظم واجراءات العمل', default=1)
    submit_ideas = fields.Integer(string=u'تقديم الأفكار والمقترحات', default=1)
    completion_work_time = fields.Integer(string=u'إنجاز العمل في الوقت المحدد', default=1)
    ability_review = fields.Integer(string=u'القدرة على المراجعة والتدقيق', default=1)
    total_eval = fields.Integer(string=u'مجموع نقاط التقييم الوظائف', compute='_calc_total_eval')
    # Personal traits
    ability_dialogue = fields.Integer(string=u'القدرة على الحوار وعرض الراى', default=1)
    responsibility_appreciation = fields.Integer(string=u'تقدير المسئولية', default=1)
    good_conduct = fields.Integer(string=u'حسن التصرف', default=1)
    guidance_score = fields.Integer(string=u'تقبل و استيعاب التوجيه', default=1)
    appearance_care = fields.Integer(string=u'الاهتمام بالمظهر', default=1)
    total_personal_traits = fields.Integer(string=u'مجموع نقاط صفات الشخصية', compute='_calc_personal_traits')
    # Relations with others
    superiors_score = fields.Integer(string=u'التعامل مع الرؤساء', default=1)
    colleagues_score = fields.Integer(string=u'التعامل مع الزملاء', default=1)
    audit_score = fields.Integer(string=u'التعامل مع المراجعين', default=1)
    total_relationships = fields.Integer(string=u'مجموع نقاط العلاقات مع الآخرين', compute='_calc_relationships')
    # Total Assessment
    total_score = fields.Integer(string=u'الإجمــالي', compute='_calc_relationships')
    performance_report = fields.Char(string=u'الاداء العام', compute="_calc_total_score")
    recommendations = fields.Text(string=u'التوصيات العامة لتطوير قدرات الموظف')
    notes = fields.Text(string=u'ملاحظات')

    @api.model
    def create(self, vals):
        ret = super(hr_assessment_executive, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.assess.exec.seq')
        ret.write(vals)
        return ret

    @api.one
    def button_done(self):
        for eval in self:
            eval.state = 'done'

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.job_id and rec.employee_id.job_id.level > 10:
                rec.form_type = 'a'
            elif rec.employee_id and rec.employee_id.job_id and rec.employee_id.job_id.level <= 10:
                rec.form_type = 'b'

    @api.depends('ability_improve', 'ability_train', 'ability_completion_work', 'skill_execution',
                 'ability_timetable', 'maintain_worktime_score', 'implementation_safety', 'know_equipments',
                 'know_work', 'ability_overcome', 'followup_developments_work', 'ability_communication',
                 'high_responsibilities', 'knowing_system', 'submit_ideas', 'completion_work_time',
                 'ability_review', 'form_type')
    def _calc_total_eval(self):
        for rec in self:
            rec.total_eval = (rec.ability_improve if rec.form_type == 'a' else 0.0) \
                            + (rec.ability_train if rec.form_type == 'a' else 0.0) \
                            + (rec.ability_completion_work or 0.0) + (rec.skill_execution or 0.0) \
                            + (rec.ability_timetable or 0.0) + (rec.maintain_worktime_score or 0.0) \
                            + (rec.implementation_safety or 0.0) + (rec.know_equipments or 0.0) \
                            + (rec.know_work or 0.0) + (rec.ability_overcome or 0.0) \
                            + (rec.followup_developments_work or 0.0) + (rec.ability_communication or 0.0) \
                            + (rec.high_responsibilities or 0.0) + (rec.knowing_system or 0.0) \
                            + (rec.submit_ideas or 0.0) \
                            + (rec.completion_work_time if rec.form_type == 'b' else 0.0) \
                            + (rec.ability_review if rec.form_type == 'b' else 0.0)

    @api.depends('ability_dialogue', 'responsibility_appreciation',
                 'good_conduct', 'guidance_score', 'appearance_care')
    def _calc_personal_traits(self):
        for rec in self:
            rec.total_personal_traits = (rec.ability_dialogue or 0.0) + (rec.responsibility_appreciation or 0.0) \
                                    + (rec.good_conduct or 0.0) + (rec.guidance_score or 0.0) \
                                    + (rec.appearance_care or 0.0)

    @api.depends('superiors_score', 'colleagues_score', 'audit_score')
    def _calc_relationships(self):
        for rec in self:
            rec.total_relationships = (rec.superiors_score or 0.0) + (rec.colleagues_score or 0.0) + (rec.audit_score or 0.0)

    @api.depends('total_eval', 'total_personal_traits', 'total_relationships')
    def _calc_total_score(self):
        job_perf_obj = self.env['hr.assessment.point.job']
        def get_grade(value):
            domain = [
                ('eval_type', '=', 'executive'),
            ]
            job_perf = job_perf_obj.search(domain)
            for jp in job_perf:
                if jp.point_from <= value <= jp.point_to:
                    return jp.eval_name
        for rec in self:
            rec.total_score = (rec.total_eval or 0.0) + (rec.total_personal_traits or 0.0) + (rec.total_relationships or 0.0)
            if rec.total_score:
                rec.performance_report = get_grade(rec.total_score)

    @api.constrains('ability_improve', 'ability_train', 'ability_completion_work', 'skill_execution',
                    'ability_timetable', 'maintain_worktime_score', 'implementation_safety', 'know_equipments',
                    'know_work', 'ability_overcome', 'followup_developments_work', 'ability_communication',
                    'high_responsibilities', 'knowing_system', 'submit_ideas', 'completion_work_time',
                    'ability_review', 'state')
    def constraint_eval(self):
        if self.state == 'draft':
            if self.form_type == 'a':
                if not (1 <= self.skill_execution <= 7):
                    raise ValidationError(u"المهارة في التنفيذ' يجب أن تكون القيمة ما بين 1 و 7.")
                if not (1 <= self.maintain_worktime_score <= 6):
                    raise ValidationError(u"'المحافظة على اوقات الدوام' يجب أن تكون القيمة ما بين 1 و 6.")
                if not (1 <= self.ability_overcome <= 4):
                    raise ValidationError(u"'القدرة على التغلب على صعوبات العمل' يجب أن تكون القيمة ما بين 1 و 4.")
                if not (1 <= self.followup_developments_work <= 4):
                    raise ValidationError(u"'المتابعة لما يستجد فى مجال العمل' يجب أن تكون القيمة ما بين 1 و 4.")
                if not (1 <= self.ability_communication <= 4):
                    raise ValidationError(u"'القدرة على اقامة اتصالات فعالة مع الاخرين' يجب أن تكون القيمة ما بين 1 و 4.")
                if not (1 <= self.high_responsibilities <= 3):
                    raise ValidationError(u"'امكانية تحمل مسئولية اعلى' يجب أن تكون القيمة ما بين 1 و 3.")
            elif self.form_type == 'b':
                if not (1 <= self.skill_execution <= 6):
                    raise ValidationError(u"'المهارة في التنفيذ' يجب أن تكون القيمة ما بين 1 و 6.")
                if not (1 <= self.maintain_worktime_score <= 7):
                    raise ValidationError(u"'المحافظة على اوقات الدوام' يجب أن تكون القيمة ما بين 1 و 7.")
                if not (1 <= self.ability_overcome <= 3):
                    raise ValidationError(u"'القدرة على التغلب على صعوبات العمل' يجب أن تكون القيمة ما بين 1 و 3.")
                if not (1 <= self.followup_developments_work <= 3):
                    raise ValidationError(u"'المتابعة لما يستجد فى مجال العمل' يجب أن تكون القيمة ما بين 1 و 3.")
                if not (1 <= self.ability_communication <= 3):
                    raise ValidationError(u"'القدرة على اقامة اتصالات فعالة مع الاخرين' يجب أن تكون القيمة ما بين 1 و 3.")
                if not (1 <= self.high_responsibilities <= 4):
                    raise ValidationError(u"'امكانية تحمل مسئولية اعلى' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.ability_completion_work <= 7):
                raise ValidationError(u"'القدرة على تحديد متطلبات إنجاز العمل' يجب أن تكون القيمة ما بين 1 و 7.")
            if not (1 <= self.ability_timetable <= 6):
                raise ValidationError(u"'القدرة على تحديد خطوات العمل والبرنامج الزمني' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.implementation_safety <= 5):
                raise ValidationError(u"'تطبيق أسس السلامة المعتمدة في العمل' يجب أن تكون القيمة ما بين 1 و 5.")
            if not (1 <= self.know_equipments <= 4):
                raise ValidationError(u"'المعرفة بالطرق السليمة لعمل الاجهزة والمواد المستخدمة' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.know_work <= 4):
                raise ValidationError(u"'المعرفة بالاسس والمفاهيم المتعلقة بالعمل' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.knowing_system <= 3):
                raise ValidationError(u"'المعرفة بنظم واجراءات العمل' يجب أن تكون القيمة ما بين 1 و 3.")
            if not (1 <= self.submit_ideas <= 3):
                raise ValidationError(u"'تقديم الأفكار والمقترحات' يجب أن تكون القيمة ما بين 1 و 3.")
            if not (1 <= self.ability_improve <= 6):
                raise ValidationError(u"'القدرة على تطوير اساليب العمل' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.ability_train <= 6):
                raise ValidationError(u"'القدرة على تدريب غيره من العاملين' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.completion_work_time <= 7):
                raise ValidationError(u"'إنجاز العمل في الوقت المحدد' يجب أن تكون القيمة ما بين 1 و 7.")
            if not (1 <= self.ability_review <= 7):
                raise ValidationError(u"'القدرة على المراجعة والتدقيق' يجب أن تكون القيمة ما بين 1 و 7.")

    @api.constrains('ability_dialogue', 'responsibility_appreciation', 'good_conduct',
                    'guidance_score', 'appearance_care', 'state')
    def constraint_personal_traits(self):
        if self.state == 'draft':
            if self.form_type == 'a':
                if not (1 <= self.ability_dialogue <= 4):
                    raise ValidationError(u"'القدرة على الحوار وعرض الراى' يجب أن تكون القيمة ما بين 1 و 4.")
                if not (1 <= self.appearance_care <= 3):
                    raise ValidationError(u"'الاهتمام بالمظهر' يجب أن تكون القيمة ما بين 1 و 3.")
            elif self.form_type == 'b':
                if not (1 <= self.ability_dialogue <= 3):
                    raise ValidationError(u"'القدرة على الحوار وعرض الراى' يجب أن تكون القيمة ما بين 1 و 3.")
                if not (1 <= self.appearance_care <= 4):
                    raise ValidationError(u"'الاهتمام بالمظهر' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.responsibility_appreciation <= 4):
                raise ValidationError(u"'تقدير المسئولية' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.good_conduct <= 4):
                raise ValidationError(u"'حسن التصرف' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.guidance_score <= 4):
                raise ValidationError(u"'تقبل و استيعاب التوجيه' يجب أن تكون القيمة ما بين 1 و 4.")

    @api.constrains('superiors_score', 'colleagues_score', 'audit_score', 'state')
    def constraint_relations_others(self):
        if self.state == 'draft':
            if not (1 <= self.superiors_score <= 3):
                raise ValidationError(u"'التعامل مع الرؤساء' يجب أن تكون القيمة ما بين 1 و 3.")
            if not (1 <= self.colleagues_score <= 3):
                raise ValidationError(u"'التعامل مع الزملاء' يجب أن تكون القيمة ما بين 1 و 3.")
            if not (1 <= self.audit_score <= 3):
                raise ValidationError(u"'التعامل مع المراجعين' يجب أن تكون القيمة ما بين 1 و 3.")

class hr_assessment_executive_admin(models.Model):
    _name = 'hr.assessment.executive.admin'
    _description = 'Job Assessment for Executive Jobs for Administrators'

    name = fields.Char(string=u'رقم القرار', )
    date = fields.Date(string=u'التاريخ', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    form_type = fields.Selection([
        ('a', u'11 و 12 و 13'),
        ('b', u'10 فما دون'),
    ], string=u'نوع النموذج ', default='b')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('done', u'اعتمدت'),
    ], string=u'الحالة', default='draft')
    # Evaluation
    ability_improve = fields.Integer(string=u'القدرة على تطوير أساليب العمل', default=1)
    ability_train = fields.Integer(string=u'القدرة على تدريب غيره من العاملين', default=1)
    ability_completion_work = fields.Integer(string=u'القدرة على تحديد متطلبات إنجاز العمل', default=1)
    skill_execution = fields.Integer(string=u'المهارة في التنفيذ', default=1)
    ability_timetable = fields.Integer(string=u'القدرة على تحديد خطوات العمل والبرنامج الزمني', default=1)
    maintain_worktime_score = fields.Integer(string=u'المحافظة على اوقات الدوام', default=1)
    ability_overcome = fields.Integer(string=u'القدرة على التغلب على صعوبات العمل', default=1)
    know_work = fields.Integer(string=u'المعرفة بالاسس والمفاهيم المتعلقة بالعمل', default=1)
    knowing_system = fields.Integer(string=u'المعرفة بنظم واجراءات العمل', default=1)
    followup_developments_work = fields.Integer(string=u'المتابعة لما يستجد فى مجال العمل', default=1)
    attend_meetings = fields.Integer(string=u'المشاركة الفعالة فى الأجتماعات', default=1)
    ability_communication = fields.Integer(string=u'القدرة على اقامة اتصالات فعالة مع الاخرين', default=1)
    high_responsibilities = fields.Integer(string=u'امكانية تحمل مسئولية اعلى', default=1)
    goal_understand = fields.Integer(string=u'التفهم لاهداف الجهاز', default=1)
    submit_ideas = fields.Integer(string=u'تقديم الأفكار والمقترحات', default=1)
    completion_work_time = fields.Integer(string=u'إنجاز العمل في الوقت المحدد', default=1)
    ability_review = fields.Integer(string=u'القدرة على المراجعة والتدقيق', default=1)
    total_eval = fields.Integer(string=u'مجموع نقاط التقييم الوظائف', compute='_calc_total_eval')
    # Personal traits
    ability_dialogue = fields.Integer(string=u'القدرة على الحوار وعرض الراى', default=1)
    responsibility_appreciation = fields.Integer(string=u'تقدير المسئولية', default=1)
    good_conduct = fields.Integer(string=u'حسن التصرف', default=1)
    accept_guidance = fields.Integer(string=u'تقبل التوجيهات والاستعداد لتنفيذها', default=1)
    appearance_care = fields.Integer(string=u'الاهتمام بالمظهر', default=1)
    total_personal_traits = fields.Integer(string=u'مجموع نقاط صفات الشخصية', compute='_calc_personal_traits')
    # Relations with others
    superiors_score = fields.Integer(string=u'التعامل مع الرؤساء', default=1)
    colleagues_score = fields.Integer(string=u'التعامل مع الزملاء', default=1)
    audit_score = fields.Integer(string=u'التعامل مع المراجعين', default=1)
    total_relationships = fields.Integer(string=u'مجموع نقاط العلاقات مع الآخرين', compute='_calc_relationships')
    # General Notes
    strengths_ids = fields.One2many('hr.assessment.specialized.strength', 'assessment_executive_admin_id', string=u'نقاط القوة')
    weaknesses_ids = fields.One2many('hr.assessment.specialized.weakness', 'assessment_executive_admin_id', string=u'نقاط الضعف')
    total_general = fields.Integer(string=u'مجموع نقاط الملاحظات العامة', compute='_calc_general')
    # Total Assessment
    total_score = fields.Integer(string=u'الإجمــالي', compute='_calc_relationships')
    performance_report = fields.Char(string=u'الاداء العام', compute="_calc_total_score")
    recommendations = fields.Text(string=u'التوصيات العامة لتطوير قدرات الموظف')
    notes = fields.Text(string=u'ملاحظات')

    @api.model
    def create(self, vals):
        ret = super(hr_assessment_executive_admin, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.assess.exec.admin.seq')
        ret.write(vals)
        return ret

    @api.one
    def button_done(self):
        for eval in self:
            eval.state = 'done'

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.job_id and rec.employee_id.job_id.level > 10:
                rec.form_type = 'a'
            elif rec.employee_id and rec.employee_id.job_id and rec.employee_id.job_id.level <= 10:
                rec.form_type = 'b'

    @api.depends('ability_improve', 'ability_train', 'ability_completion_work', 'skill_execution',
                 'ability_timetable', 'maintain_worktime_score', 'ability_overcome', 'know_work',
                 'knowing_system', 'followup_developments_work', 'attend_meetings', 'ability_communication',
                 'high_responsibilities', 'goal_understand', 'submit_ideas', 'completion_work_time',
                 'ability_review')
    def _calc_total_eval(self):
        for rec in self:
            rec.total_eval = (rec.ability_improve if rec.form_type == 'a' else 0.0) \
                             + (rec.ability_train if rec.form_type == 'a' else 0.0) \
                             + (rec.ability_completion_work or 0.0) + (rec.skill_execution or 0.0) \
                             + (rec.ability_timetable or 0.0) + (rec.maintain_worktime_score or 0.0) \
                             + (rec.ability_overcome or 0.0) + (rec.know_work or 0.0) \
                             + (rec.knowing_system or 0.0) + (rec.followup_developments_work or 0.0) \
                             + (rec.attend_meetings or 0.0) + (rec.ability_communication or 0.0) \
                             + (rec.high_responsibilities or 0.0) + (rec.goal_understand or 0.0) \
                             + (rec.submit_ideas or 0.0) \
                             + (rec.completion_work_time if rec.form_type == 'b' else 0.0) \
                             + (rec.ability_review if rec.form_type == 'b' else 0.0)

    @api.depends('ability_dialogue', 'responsibility_appreciation',
                 'good_conduct', 'accept_guidance', 'appearance_care')
    def _calc_personal_traits(self):
        for rec in self:
            rec.total_personal_traits = (rec.ability_dialogue or 0.0) + (rec.responsibility_appreciation or 0.0) \
                                        + (rec.good_conduct or 0.0) + (rec.accept_guidance or 0.0) \
                                        + (rec.appearance_care or 0.0)

    @api.depends('superiors_score', 'colleagues_score', 'audit_score')
    def _calc_relationships(self):
        for rec in self:
            rec.total_relationships = (rec.superiors_score or 0.0) + (rec.colleagues_score or 0.0) \
                                      + (rec.audit_score or 0.0)

    @api.depends('strengths_ids.point', 'weaknesses_ids.point')
    def _calc_general(self):
        total = 0.0
        for rec in self:
            for sline in rec.strengths_ids:
                total += sline.point
            for wline in rec.weaknesses_ids:
                total += wline.point
            rec.total_general = (total or 0.0)

    @api.depends('total_eval', 'total_personal_traits', 'total_relationships', 'total_general')
    def _calc_total_score(self):
        job_perf_obj = self.env['hr.assessment.point.job']
        def get_grade(value):
            domain = [
                ('eval_type', '=', 'executive'),
            ]
            job_perf = job_perf_obj.search(domain)
            for jp in job_perf:
                if jp.point_from <= value <= jp.point_to:
                    return jp.eval_name
        for rec in self:
            rec.total_score = (rec.total_eval or 0.0) + (rec.total_personal_traits or 0.0) + (
                            rec.total_relationships or 0.0) + (rec.total_general or 0.0)
            if rec.total_score:
                rec.performance_report = get_grade(rec.total_score)

    @api.constrains('ability_improve', 'ability_train', 'ability_completion_work',
                    'skill_execution', 'ability_timetable', 'maintain_worktime_score',
                    'ability_overcome', 'know_work', 'knowing_system', 'followup_developments_work',
                    'attend_meetings', 'ability_communication', 'high_responsibilities',
                    'goal_understand', 'submit_ideas', 'completion_work_time',
                    'ability_review', 'state')
    def constraint_eval(self):
        if self.state == 'draft':
            if self.form_type == 'a':
                if not (1 <= self.ability_improve <= 6):
                    raise ValidationError(u"'القدرة على تطوير أساليب العمل' يجب أن تكون القيمة ما بين 1 و 6.")
                if not (1 <= self.ability_train <= 6):
                    raise ValidationError(u"'القدرة على تدريب غيره من العاملين' يجب أن تكون القيمة ما بين 1 و 6.")
                if not (1 <= self.skill_execution <= 7):
                    raise ValidationError(u"'المهارة في التنفيذ' يجب أن تكون القيمة ما بين 1 و 7.")
                if not (1 <= self.maintain_worktime_score <= 6):
                    raise ValidationError(u"'المحافظة على اوقات الدوام' يجب أن تكون القيمة ما بين 1 و 6.")
                if not (1 <= self.followup_developments_work <= 4):
                    raise ValidationError(u"'المتابعة لما يستجد فى مجال العمل' يجب أن تكون القيمة ما بين 1 و 4.")
                if not (1 <= self.attend_meetings <= 4):
                    raise ValidationError(u"'المشاركة الفعالة فى الأجتماعات' يجب أن تكون القيمة ما بين 1 و 4.")
                if not (1 <= self.ability_communication <= 4):
                    raise ValidationError(u"'القدرة على اقامة اتصالات فعالة مع الاخرين' يجب أن تكون القيمة ما بين 1 و 4.")
                if not (1 <= self.high_responsibilities <= 3):
                    raise ValidationError(u"'امكانية تحمل مسئولية اعلى' يجب أن تكون القيمة ما بين 1 و 3.")
            elif self.form_type == 'b':
                if not (1 <= self.high_responsibilities <= 4):
                    raise ValidationError(u"'امكانية تحمل مسئولية اعلى' يجب أن تكون القيمة ما بين 1 و 4.")
                if not (1 <= self.ability_communication <= 3):
                    raise ValidationError(u"'القدرة على اقامة اتصالات فعالة مع الاخرين' يجب أن تكون القيمة ما بين 1 و 3.")
                if not (1 <= self.attend_meetings <= 3):
                    raise ValidationError(u"'المشاركة الفعالة فى الأجتماعات' يجب أن تكون القيمة ما بين 1 و 3.")
                if not (1 <= self.followup_developments_work <= 3):
                    raise ValidationError(u"'المتابعة لما يستجد فى مجال العمل' يجب أن تكون القيمة ما بين 1 و 3.")
                if not (1 <= self.skill_execution <= 6):
                    raise ValidationError(u"'المهارة في التنفيذ' يجب أن تكون القيمة ما بين 1 و 6.")
                if not (1 <= self.maintain_worktime_score <= 7):
                    raise ValidationError(u"'المحافظة على اوقات الدوام' يجب أن تكون القيمة ما بين 1 و 7.")
                if not (1 <= self.completion_work_time <= 7):
                    raise ValidationError(u"'إنجاز العمل في الوقت المحدد' يجب أن تكون القيمة ما بين 1 و 7.")
                if not (1 <= self.ability_review <= 7):
                    raise ValidationError(u"'القدرة على المراجعة والتدقيق' يجب أن تكون القيمة ما بين 1 و 7.")
            if not (1 <= self.ability_completion_work <= 7):
                raise ValidationError(u"'القدرة على تحديد متطلبات إنجاز العمل' يجب أن تكون القيمة ما بين 1 و 7.")
            if not (1 <= self.ability_timetable <= 4):
                raise ValidationError(u"'القدرة على تحديد خطوات العمل والبرنامج الزمني' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.ability_overcome <= 3):
                raise ValidationError(u"'القدرة على التغلب على صعوبات العمل' يجب أن تكون القيمة ما بين 1 و 3.")
            if not (1 <= self.know_work <= 6):
                raise ValidationError(u"'المعرفة بالاسس والمفاهيم المتعلقة بالعمل' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.knowing_system <= 6):
                raise ValidationError(u"'المعرفة بنظم واجراءات العمل' يجب أن تكون القيمة ما بين 1 و 6.")
            if not (1 <= self.goal_understand <= 7):
                raise ValidationError(u"'التفهم لاهداف الجهاز' يجب أن تكون القيمة ما بين 1 و 7.")
            if not (1 <= self.submit_ideas <= 7):
                raise ValidationError(u"'تقديم الأفكار والمقترحات' يجب أن تكون القيمة ما بين 1 و 7.")

    @api.constrains('ability_dialogue', 'responsibility_appreciation', 'good_conduct',
                    'accept_guidance', 'appearance_care', 'state')
    def constraint_personal_traits(self):
        if self.state == 'draft':
            if self.form_type == 'a':
                if not (1 <= self.ability_dialogue <= 4):
                    raise ValidationError(u"'القدرة على الحوار وعرض الراى' يجب أن تكون القيمة ما بين 1 و 4.")
                if not (1 <= self.appearance_care <= 3):
                    raise ValidationError(u"'الاهتمام بالمظهر' يجب أن تكون القيمة ما بين 1 و 3.")
            elif self.form_type == 'b':
                if not (1 <= self.ability_dialogue <= 3):
                    raise ValidationError(u"'القدرة على الحوار وعرض الراى' يجب أن تكون القيمة ما بين 1 و 3.")
                if not (1 <= self.appearance_care <= 4):
                    raise ValidationError(u"'الاهتمام بالمظهر' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.responsibility_appreciation <= 4):
                raise ValidationError(u"'تقدير المسئولية' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.good_conduct <= 4):
                raise ValidationError(u"'حسن التصرف' يجب أن تكون القيمة ما بين 1 و 4.")
            if not (1 <= self.accept_guidance <= 4):
                raise ValidationError(u"'تقبل التوجيهات والاستعداد لتنفيذها' يجب أن تكون القيمة ما بين 1 و 4.")

    @api.constrains('superiors_score', 'colleagues_score', 'audit_score', 'state')
    def constraint_relationships(self):
        if self.state == 'draft':
            if not (1 <= self.superiors_score <= 3):
                raise ValidationError(u"'التعامل مع الرؤساء' يجب أن تكون القيمة ما بين 1 و 3.")
            if not (1 <= self.colleagues_score <= 3):
                raise ValidationError(u"'التعامل مع الزملاء' يجب أن تكون القيمة ما بين 1 و 3.")
            if not (1 <= self.audit_score <= 3):
                raise ValidationError(u"'التعامل مع المراجعين' يجب أن تكون القيمة ما بين 1 و 3.")

    @api.constrains('strengths_ids', 'weaknesses_ids', 'state')
    def constraint_general(self):
        if self.state == 'draft':
            if len(self.strengths_ids.ids) > 3:
                raise ValidationError(u"فقط 3 نقاط المسموح بها في 'نقاط القوة'.")
            if len(self.weaknesses_ids.ids) > 3:
                raise ValidationError(u"فقط 3 نقاط المسموح بها في 'نقاط الضعف'.")

