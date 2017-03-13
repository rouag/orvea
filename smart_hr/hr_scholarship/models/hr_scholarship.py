# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta


class HrScholarship(models.Model):
    _name = 'hr.scholarship'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'الابتعاث'

    name = fields.Char(string=' المسمى', readonly=1)
    date = fields.Date(string='تاريخ الطلب', readonly=1, default=fields.Datetime.now())
    state = fields.Selection([('draft', u'طلب'),
                              ('psm', u'المصاقة على الابتعاث '),
                              ('done', u'اعتمد'),
                              ('finished', u'انتهى'),
                              ('cancel', u'ملغى'),
                              ('cutoff', u'مقطوع'),
                              ], string='الحالة', readonly=1, default='draft')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1,
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)],
                                                                                      limit=1), advanced_search=True)
    note = fields.Text(string='ملاحظات')
    date_from = fields.Date(string=u'تاريخ البدء', required=1)
    date_to = fields.Date(string=u'تاريخ الإنتهاء', required=1)
    duration = fields.Integer(string=u'عدد الأيام ', required=1, compute='_compute_duration')
    result = fields.Selection([
        ('suceed', u'نجح'),
        ('not_succeed', u' لم ينجح')], string=u'النتيجة', readonly=True)
    num_speech = fields.Char(string=u'رقم القرار', required=1)
    date_speech = fields.Date(string=u'تاريخ القرار', required=1)
    speech_file = fields.Binary(string=u'القرار', required=1, attachment=True)
    speech_file_name = fields.Char()
    diplom_type = fields.Selection(
        [('hight', u'دبلوم من الدراسات العليا'), ('middle', u'الليسانس او الباكالوريوس او دبلوم متوسط')],
        string='نوع الدبلوم', required=1)
    acceptance_certificate = fields.Binary(string=u'مرفق القبول من الجامعة او المعهد', required=1, attachment=True)
    acceptance_certificate_name = fields.Char()
    language_exam = fields.Binary(string=u'مرفق اجتياز امتحان في لغة الدراسة', required=1, attachment=True)
    language_exam_file_name = fields.Char()
    scholarship_type = fields.Many2one('hr.scholarship.type', string='نوع الابتعاث', required=1)
    diplom_id = fields.Many2one('hr.employee.diploma', string="الشهادة", required=1)
    Faculty_id = fields.Many2one('res.partner', string="  الجامعة/المعهد", required=1,
                                 domain=[('company_type', 'in', ['faculty', 'school'])])
    is_extension = fields.Boolean(string=u'ممددة')
    parent_id = fields.Many2one('hr.scholarship', string=u'Parent')
    extension_scholarship_ids = fields.One2many('hr.scholarship', 'parent_id', string=u'التمديدات')
    extended_scholarship_id = fields.Many2one('hr.scholarship', string=u'الابتعاث الممدد')
    order_number = fields.Char(string=u'رقم الخطاب')
    order_date = fields.Date(string=u'تاريخ الخطاب')
    file_decision = fields.Binary(string=u'الخطاب', attachment=True)
    file_decision_name = fields.Char(string=u'اسم الخطاب')
    order_source = fields.Char(string=u'مصدر الخطاب')
    is_started = fields.Boolean(string=u'بدأت', compute='_compute_is_started', default=False)
    salary_percent = fields.Float(string=u'نسبة الراتب(%)')
    hr_allowance_type_id = fields.Many2many('hr.allowance.type', string='البدلات المستثنات')

    @api.one
    @api.depends('extension_scholarship_ids')
    def _is_extended(self):
        # Check if the holiday have a pending or completed extension leave
        is_extended = False
        for ext in self.extension_scholarship_ids:
            if ext.state != 'refuse':
                is_extended = True
                break
        self.is_extended = is_extended

    @api.one
    @api.depends('date_from', 'date_to')
    def _compute_duration(self):
        if self.date_from and self.date_to:
            self.duration = self.env['hr.smart.utils'].compute_duration(self.date_from, self.date_to)

    @api.model
    def create(self, vals):
        res = super(HrScholarship, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.scholarship.seq')
        res.write(vals)
        return res

    @api.multi
    def action_psm(self):
        self.ensure_one()
        self.check_constraintes()
        self.state = 'psm'

    @api.multi
    def action_refuse(self):
        self.ensure_one()
        self.state = 'draft'

    @api.multi
    def action_done(self):
        #             create history_line
        self.ensure_one()
        type = self.scholarship_type.name.encode('utf-8')
        #         self.env['hr.employee.history'].sudo().add_action_line(self.employee_id, self.num_speech, self.date_speech, "ابتعاث")
        self.state = 'done'

    @api.multi
    def action_cutoff(self):
        self.ensure_one()
        if not self.is_started:
            raise ValidationError(u'لا يمكن قطع ابتعاث لم يبدأ بعد.')
        self.state = 'cutoff'

    @api.multi
    def action_cancel(self):
        self.ensure_one()
        if self.is_started:
            raise ValidationError(u' لا يمكن الغاء ابتعاث بدأ.')
        self.state = 'cancel'

    @api.multi
    def action_succeeded(self):
        self.ensure_one()
        if fields.Date.from_string(self.date_to) > fields.Date.from_string(fields.Date.today()):
            raise ValidationError(u"الدورة لم تنتهي بعد")
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': u'احتساب مؤهل علمي جديد',
                'res_model': 'hr.scholarship.succced.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new'}

    @api.multi
    def action_not_succeeded(self):
        self.ensure_one()
        if self.date_to:
            if fields.Date.from_string(self.date_to) > fields.Date.from_string(fields.Date.today()):
                raise ValidationError(u"الدورة لم تنتهي بعد")
        self.result = 'not_succeed'
        self.env['hr.employee.promotion.history'].decrement_promotion_duration(self.employee_id, self.duration)
        self.state = 'finished'

    @api.multi
    def check_constraintes(self):
        self.ensure_one()
        #         constraint service_duration and education level
        date_from = fields.Date.from_string(self.date_from)
        needed_service_duration = self.env['hr.scholarship.service.duration'].search(
            [('scholarship_type', '=', self.scholarship_type.id), ('diplom_type', '=', self.diplom_type)], limit=1)
        if needed_service_duration:
            if self.employee_id.service_duration < needed_service_duration.service_duration:
                raise ValidationError(u"ليس لديك السنوات المطلوبة في الخدمة")
            education_level_ids = []
            if self.diplom_type == 'hight':
                education_level_ids = self.env['hr.employee.job.education.level'].search(
                    [('employee_id', '=', self.employee_id.id),
                     ('level_education_id', 'in', [self.env.ref('smart_hr.certificate_baccalaureate').id,
                                                   self.env.ref('smart_hr.certificate_licence').id])])
            if self.diplom_type == 'middle':
                education_level_ids = self.env['hr.employee.job.education.level'].search(
                    [('employee_id', '=', self.employee_id.id),
                     ('level_education_id', '=', self.env.ref('smart_hr.certificate_after_secondary_education').id)])
            #             if not education_level_ids:
            #                 raise ValidationError(u"الرجاء مراجعة المؤهلات العلمية للموظف")
            #             for level in education_level_ids:
            #                 if (date_from - fields.Date.from_string(level.diploma_date)).days < needed_service_duration.service_duration:
            #                     raise ValidationError(u"لم تمضي السنوات المطلوبة في الخدمة بعد الحصول على آخر دپلوم")
            #
            #             education_level_ids = self.env['hr.employee.job.education.level'].search([('employee_id', '=', self.employee_id.id),
            #                                                                                       ('level_education_id', '=', self.env.ref('smart_hr.certificate_after_secondary_education').id)])
            #         else:
            #             raise ValidationError(u" الرجاء مراجعة إعداد مدة الخدمة اللازمة قبل الابتعاث")

            #         constraint evaluation
        employee_evaluation_id1 = self.env['hr.employee.evaluation.level'].search(
            [('employee_id', '=', self.employee_id.id), ('year', '=', date_from.year - 1)], limit=1)
        employee_evaluation_id2 = self.env['hr.employee.evaluation.level'].search(
            [('employee_id', '=', self.employee_id.id), ('year', '=', date_from.year - 2)], limit=1)
        if employee_evaluation_id1 and employee_evaluation_id2:
            if employee_evaluation_id1.degree_id.point_to < self.env.ref(
                    'smart_hr.assessment_hr_good').point_from or employee_evaluation_id1.degree_id.point_to < self.env.ref(
                    'smart_hr.assessment_hr_good').point_from:
                raise ValidationError(u"لم تتحصل على تقييم الأدائ الوظيفي‬ المطلوب.")
        else:
            raise ValidationError(u"لا يوجد تقييم وظيفي خاص بالموظف للسنتين الفارطتين")

    @api.multi
    def button_extend(self):

        view_id = self.env.ref('smart_hr.hr_scholarship_form').id
        context = self._context.copy()
        default_date_from = fields.Date.to_string(fields.Date.from_string(self.date_to) + timedelta(days=1))
        context.update({
            u'default_is_extension': True,
            u'default_extended_scholarship_id': self.id,
            u'default_date_from': default_date_from,
            u'readonly_by_pass': True,
            u'default_diplom_type': self.diplom_type,
            u'default_scholarship_type': self.scholarship_type.id,
            u'default_employee_id': self.employee_id.id,
            u'default_diplom_id': self.diplom_id.id,
            u'default_Faculty_id': self.Faculty_id.id,
            u'default_acceptance_certificate': self.acceptance_certificate,
            u'default_language_exam': self.language_exam,
            u'default_acceptance_certificate_name': self.acceptance_certificate_name,
            u'default_language_exam_file_name': self.language_exam_file_name,
        })
        return {
            'name': 'تمديد الابتعاث',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'hr.scholarship',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': False,
            'target': 'current',
            'context': context,
        }

    @api.multi
    def _compute_is_started(self):
        self.ensure_one()
        if self.date_from <= datetime.today().strftime('%Y-%m-%d'):
            self.is_started = True

    @api.one
    @api.constrains('date_from', 'date_to')
    def check_dates_periode(self):
        # Date validation

        if self.date_from > self.date_to:
            raise ValidationError(u"تاريخ من يجب ان يكون أصغر من تاريخ الى")

    @api.multi
    def unlink(self):
        # Validation
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(u'لا يمكن حذف ابتعاث فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(HrScholarship, self).unlink()


class HrScholarshipType(models.Model):
    _name = 'hr.scholarship.type'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'نوع الابتعاث'

    name = fields.Char(string=' المسمى')
    code = fields.Char(string=' الرمز')
    pension_percent = fields.Float(string=u'نسبة راتب التقاعد(%)')
    traveling_family_ticket = fields.Boolean(string=u'تذكرة سفر عائليّة', default=False)
    note = fields.Text(string='ملاحظات')
    service_duration_needed = fields.One2many('hr.scholarship.service.duration', 'scholarship_type',
                                              string=u'مدة الخدمة اللازمة قبل الابتعاث')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result

    @api.one
    @api.constrains('pension_percent')
    def check_pension_percent(self):
        if self.pension_percent < 0 or self.pension_percent > 100:
            raise ValidationError(u"نسبة راتب التقاعد خاطئة ")


class HrScholarshipServiceDuration(models.Model):
    _name = 'hr.scholarship.service.duration'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'مدة الخدمة اللازمة قبل الابتعاث'

    name = fields.Char(string=' المسمى')
    service_duration = fields.Integer(string=u'(المدة (يوم')
    diplom_type = fields.Selection(
        [('hight', u'دبلوم من الدراسات العليا'), ('middle', u'الليسانس او الباكالوريوس او دبلوم متوسط')],
        string='نوع الدبلوم', )
    scholarship_type = fields.Many2one('hr.scholarship.type')
