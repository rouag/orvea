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
                            ('cancel', u'ملغاة'),
                            ('cutoff', u'مقطوعة'),
                              ], string='الحالة', readonly=1, default='draft')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1,  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), advanced_search=True)
    note = fields.Text(string='ملاحظات')
    date_from = fields.Date(string=u'تاريخ البدء', required=1)
    date_to = fields.Date(string=u'تاريخ الإنتهاء', required=1)
    duration = fields.Integer(string=u'الأيام', required=1, compute='_compute_duration')
    result = fields.Selection([
        ('suceed', u'نجح'),
        ('not_succeed', u' لم ينجح')], string=u'النتيجة', readonly=True)
    num_speech = fields.Char(string=u'رقم القرار', required=1)
    date_speech = fields.Date(string=u'تاريخ القرار', required=1)
    speech_file = fields.Binary(string=u'القرار', required=1)
    speech_file_name = fields.Char()
    diplom_type = fields.Selection([('hight', u'دبلوم من الدراسات العليا'),
                              ('middle', u'الليسانس او الباكالوريوس او دبلوم متوسط')], string='نوع الدبلوم', required=1)
    acceptance_certificate = fields.Binary(string=u'مرفق القبول من الجامعة او المعهد', required=1)
    acceptance_certificate_name = fields.Char()
    language_exam = fields.Binary(string=u'مرفق اجتياز امتحان في لغة الدراسة', required=1)
    language_exam_file_name = fields.Char()
    scholarship_type = fields.Many2one('hr.scholarship.type', string='نوع الابتعاث', required=1)
    diplom_id = fields.Many2one('hr.employee.diploma', string="الشهادة", required=1)
    Faculty_id = fields.Many2one('res.partner', string="  الجامعة/المعهد", required=1)

    @api.one
    @api.depends('date_from', 'date_to')
    def _compute_duration(self):
        if self.date_from and self.date_to:
            date_from = fields.Date.from_string(self.date_from)
            date_to = fields.Date.from_string(self.date_to)
            self.duration = (date_to - date_from).days

    @api.model
    def create(self, vals):
        res = super(HrScholarship, self).create(vals)
        res.check_constraintes()
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.scholarship.seq')
        res.write(vals)
        return res

    @api.one
    def action_psm(self):
        self.state = 'psm'

    @api.one
    def action_refuse(self):
        self.state = 'draft'

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_cutoff(self):
        self.state = 'cutoff'

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.one
    def action_succeeded(self):
        if fields.Date.from_string(self.date_to) > fields.Date.from_string(fields.Date.today()):
            raise ValidationError(u"الدورة لم تنتهي بعد")
        self.result = 'suceed'
        self.state = 'finished'

    @api.one
    def action_not_succeeded(self):
        if self.date_to:
            if fields.Date.from_string(self.date_to) > fields.Date.from_string(fields.Date.today()):
                raise ValidationError(u"الدورة لم تنتهي بعد")
        self.result = 'not_succeed'
        self.env['hr.employee.promotion.history'].decrement_promotion_duration(self.employee_id, self.duration)
        self.state = 'finished'

    @api.multi
    def check_constraintes(self):
        self.ensure_one()
        if self.diplom_type == 'hight':
            if self.employee_id.service_duration < 2*365:
                raise ValidationError(u"ليس لديك سنتين في الخدمة")
        if self.diplom_type == 'middle':
            if self.employee_id.service_duration < 3*365:
                raise ValidationError(u"ليس لديك ثلاث سنوات في الخدمة")

        employee_evaluation_id1 = self.env['hr.employee.evaluation.level'].search([('employee_id', '=', self.employee_id.id),('year', '=',self.date_from.year-1)], limit=1)
        employee_evaluation_id2 = self.env['hr.employee.evaluation.level'].search([('employee_id', '=', self.employee_id.id),('year', '=',self.date_from.year-2)], limit=1)
        if employee_evaluation_id1 and employee_evaluation_id2:
            if employee_evaluation_id1.degree_id.point_to < self.env.ref['assessment_good'].degree_id.point_from or employee_evaluation_id1.degree_id.point_to < self.env.ref['assessment_good'].degree_id.point_from:
                raise ValidationError(u"لم تتحصل على تقييم الأدائ الوظيفي‬ المطلوب.")
        else:
            raise ValidationError(u"لا يوجد تقييم وظيفي خاص بالموظف للسنتين الفارطتين")


class HrScholarshipType(models.Model):

    _name = 'hr.scholarship.type'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'نوع الابتعاث'

    name = fields.Char(string=' المسمى')
    code = fields.Char(string=' الرمز')
    pension_percent = fields.Float(string=u'(%)نسبة راتب التقاعد')
    salary_percent = fields.Float(string=u'(%)نسبة الراتب')
    hr_allowance_type_id = fields.Many2many('hr.allowance.type', string='البدلات المستثنات')
    traveling_family_ticket = fields.Boolean(string=u'تذكرة سفر عائليّة', default=False)
    note = fields.Text(string='ملاحظات')

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
        if self.salary_percent < 0 or self.salary_percent > 100:
            raise ValidationError(u"نسبة الراتب خاطئة ")
    