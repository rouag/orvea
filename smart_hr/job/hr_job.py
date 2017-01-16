# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class HrJob(models.Model):
    _inherit = 'hr.job'
    _description = u'الوظائف'

    name = fields.Many2one('hr.job.name', string='المسمى', required=1)
    number = fields.Char(string='الرقم الوظيفي', required=1, states={'unoccupied': [('readonly', 0)]})
    department_id = fields.Many2one('hr.department', string='الإدارة', required=1, states={'unoccupied': [('readonly', 0)]})
    general_id = fields.Many2one('hr.groupe.job', ' المجموعة العامة', ondelete='cascade')
    specific_id = fields.Many2one('hr.groupe.job', ' المجموعة النوعية', ondelete='cascade')
    serie_id = fields.Many2one('hr.groupe.job', ' سلسلة الفئات', ondelete='cascade')
    type_id = fields.Many2one('salary.grid.type', string='التصنيف', required=1, states={'unoccupied': [('readonly', 0)]})
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', required=1, states={'unoccupied': [('readonly', 0)]})
    state = fields.Selection([('unoccupied', 'شاغرة'), ('occupied', 'مشغولة'), ('cancel', 'ملغاة')], readonly=1, default='unoccupied')
    employee = fields.Many2one('hr.employee', string=u'الموظف')
    deputed_employee = fields.Boolean(string=u'موظف ندب', advanced_search=True)
    # حجز الوظيفة
    occupation_date_from = fields.Date(string=u'حجز الوظيفة من')
    occupation_date_to = fields.Date(string=u'حجز الوظيفة الى',)
    is_occupied_compute = fields.Boolean(string='is occupied compute', compute='_compute_is_occupated')
    is_occupied = fields.Boolean(string='is occupied', default=False)
    # سلخ
    is_striped_from = fields.Boolean(string='is striped from', default=False)
    is_striped_to = fields.Boolean(string='is striped to', default=False)
    # تحوير‬
    update_date = fields.Date(string=u'تاريخ التحوير')

    def _compute_is_occupated(self):
        for rec in self:
            if rec.occupation_date_to:
                if rec.occupation_date_to >= datetime.today().strftime('%Y-%m-%d'):
                    rec.write({'is_occupied': True})
                else:
                    self.action_job_unreserve()

    @api.multi
    def action_job_unreserve(self):
        self.ensure_one()
        self.occupation_date_from = False
        self.occupation_date_to = False
        self.is_occupied = False

    @api.multi
    def action_job_reserve(self):
        self.ensure_one()
        context = {}
        context['job_id'] = self.id
        return {
            'name': u'حجز الوظيفة',
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'hr.job.reservation',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
            }


class HrJobName(models.Model):
    _name = 'hr.job.name'
    _description = u'المسميات الوظيفية '
    name = fields.Char(string=u'المسمى', required=1)
    number = fields.Char(string=u'الرمز', required=1)
    job_description = fields.Text(string=u'متطلبات الوظيفية')
    _sql_constraints = [('number_uniq', 'unique(number)', 'رمز هذا المسمى موجود.')]


class HrJobReservation(models.Model):
    _name = 'hr.job.reservation'
    _description = u'الوظائف'
    _rec_name = 'date_from'

    date_from = fields.Date(string=u'التاريخ من', readonly=1, default=fields.Datetime.now())
    date_to = fields.Date(string=u'التاريخ الى')

    @api.onchange('date_from', 'date_to')
    def onchange_dates(self):
        self.ensure_one()
        if self.date_from and self.date_to:
            if self.date_from >= self.date_to:
                raise ValidationError(u"تاريخ من يجب ان يكون أصغر من تاريخ الى")

    @api.multi
    def action_job_reserve_confirm(self):
        if self.date_from and self.date_to:
            print self.date_from
            print self.date_to
            self.env['hr.job'].search([('id', '=', self._context['job_id'])]).write({'occupation_date_from': self.date_from, 'occupation_date_to': self.date_to})


class HrJobCreate(models.Model):
    _name = 'hr.job.create'
    _inherit = ['mail.thread']
    _description = u'إحداث وظائف'

    name = fields.Char(string='المسمى', required=1, readonly=1, states={'new': [('readonly', 0)]})
    fiscal_year = fields.Char(string='السنه المالية', default=(date.today().year), readonly=1)
    decision_number = fields.Char(string=u"رقم القرار", required=1, readonly=1, states={'new': [('readonly', 0)]})
    speech_number = fields.Char(string=u'رقم الخطاب')
    speech_date = fields.Date(string=u'تاريخ الخطاب')
    speech_file = fields.Binary(string=u'صورة الخطاب')
    line_ids = fields.One2many('hr.job.create.line', 'job_create_id', readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'في إنتظار الموافقة'),
                              ('budget', u'إدارة الميزانية'),
                              ('communication', u'إدارة الإتصالات'),
                              ('external', u'وزارة المالية'),
                              ('hrm', u'شؤون الموظفين'),
                              ('done', u'اعتمدت')
                              ], readonly=1, default='new')
    general_id = fields.Many2one('hr.groupe.job', ' المجموعة العامة', ondelete='cascade')
    specific_id = fields.Many2one('hr.groupe.job', ' المجموعة النوعية', ondelete='cascade')
    serie_id = fields.Many2one('hr.groupe.job', ' سلسلة الفئات', ondelete='cascade')
    grade_ids = fields.One2many('salary.grid.grade', 'job_create_id', string='المرتبة')
    draft_budget = fields.Binary(string=u'مشروع الميزانية')

    @api.onchange('serie_id')
    def onchange_serie_id(self):
        if self.serie_id:
            grides = []
            for classment in self.serie_id.hr_classment_job_ids:
                grides.append(classment.grade_id.id)
            self.grade_ids = grides

    @api.multi
    def action_waiting(self):
        self.ensure_one()
        self.state = 'waiting'

    @api.multi
    def action_hrm(self):
        self.ensure_one()
        self.state = 'hrm'
        # Add to log
        self.message_post(u"تمت الموافقة من قبل الجهة الخارجية (وزارة المالية)")

    @api.multi
    def action_budget(self):
        self.ensure_one()
        self.state = 'budget'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def action_external(self):
        self.ensure_one()
        if not self.draft_budget:
            raise ValidationError(u"الرجاء إرفاق مشروع الميزانية.")
        self.state = 'external'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"' (إدارة الإتصالات)")

    @api.multi
    def action_communication(self):
        self.ensure_one()
        self.state = 'communication'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"' (إدارة الميزانية)")

    @api.multi
    def action_done(self):
        self.ensure_one()
        for line in self.line_ids:
            job_val = {'name': line.name.id,
                       'number': line.job_number,
                       'type_id': line.type_id.id,
                       'grade_id': line.grade_id.id,
                       'department_id': line.department_id.id,
                       'general_id': self.general_id.id,
                       'specific_id': self.specific_id.id,
                       'serie_id': self.serie_id.id
                       }
            self.env['hr.job'].create(job_val)
        self.state = 'done'
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت إحداث الوظائف من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def action_refuse(self):
        self.ensure_one()
        self.state = 'new'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم رفض الطلب من قبل '" + unicode(user.name) + u"'")


class HrJobCreateLine(models.Model):
    _name = 'hr.job.create.line'
    _description = u'الوظائف'

    name = fields.Many2one('hr.job.name', string='الوظيفة', required=1)
    number = fields.Char(string='الرمز', required=1)
    job_number = fields.Char(string='الرقم الوظيفي', required=1)
    type_id = fields.Many2one('salary.grid.type', related="grade_id.type_id", string='التصنيف', required=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', required=1)
    department_id = fields.Many2one('hr.department', string='الإدارة', required=1)
    job_create_id = fields.Many2one('hr.job.create', string=' وظائف')

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.number = self.name.number

    @api.constrains('job_number', 'grade_id')
    def _check_grade_id_job_number(self):
        if self.job_number and self.grade_id:
            # check if there is already a job with same grade and job number
            jobs = self.env['hr.job'].search([])
            for job in jobs:
                if job.grade_id == self.grade_id and job.number == self.job_number:
                    raise ValidationError(u"يوجد وظيفة بنفس الرقم والمرتبة.")

    @api.onchange('grade_id')
    def onchange_grade_idd(self):
        res = {}
        # get grades in job_create_id
        if not self.grade_id:
            grade_ids = [rec .id for rec in self.job_create_id.grade_ids]
            res['domain'] = {'grade_id': [('id', 'in', grade_ids)]}
            return res


class HrJobStripFrom(models.Model):
    _name = 'hr.job.strip.from'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    _description = u'سلخ وظائف من جهة'

    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), required=1, readonly=1)
    fiscal_year = fields.Char(string='السنه المالية', default=(date.today().year), readonly=1)
    decision_number = fields.Char(string=u"رقم القرار", required=1, readonly=1, states={'new': [('readonly', 0)]})
    speech_number = fields.Char(string=u'رقم الخطاب')
    speech_date = fields.Date(string=u'تاريخ الخطاب')
    speech_file = fields.Binary(string=u'صورة الخطاب')
    out_speech_number = fields.Char(string=u'رقم الخطاب الصادر')
    out_speech_date = fields.Date(string=u'تاريخ الخطاب الصادر')
    out_speech_file = fields.Binary(string=u'صورة الخطاب الصادر')
    in_speech_number = fields.Char(string=u'رقم الخطاب الوارد')
    in_speech_date = fields.Date(string=u'تاريخ الخطاب الوارد')
    in_speech_file = fields.Binary(string=u'صورة الخطاب الوارد ')
    line_ids = fields.One2many('hr.job.strip.from.line', 'job_strip_from_id', readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'في إنتظار الموافقة'),
                              ('hrm1', u'شؤون الموظفين'),
                              ('communication', u'إدارة الإتصالات'),
                              ('external', u'وزارة المالية'),
                              ('hrm2', u'شؤون الموظفين'),
                              ('done', u'اعتمدت')
                              ], readonly=1, default='new')
    general_id = fields.Many2one('hr.groupe.job', ' المجموعة العامة', ondelete='cascade')
    specific_id = fields.Many2one('hr.groupe.job', ' المجموعة النوعية', ondelete='cascade')
    serie_id = fields.Many2one('hr.groupe.job', ' سلسلة الفئات', ondelete='cascade')
    grade_ids = fields.One2many('salary.grid.grade', 'job_strip_from_id', string='المرتبة')

    @api.onchange('serie_id')
    def onchange_serie_id(self):
        if self.serie_id:
            grides = []
            for classment in self.serie_id.hr_classment_job_ids:
                grides.append(classment.grade_id.id)
            self.grade_ids = grides

    @api.multi
    def action_waiting(self):
        self.ensure_one()
        self.state = 'waiting'

    @api.multi
    def action_hrm1(self):
        self.ensure_one()
        self.state = 'hrm1'

    @api.multi
    def action_hrm2(self):
        self.ensure_one()
        self.state = 'hrm2'
        # Add to log
        self.message_post(u"تمت الموافقة من قبل الجهة الخارجية (وزارة المالية)")

    @api.multi
    def action_budget(self):
        self.ensure_one()
        self.state = 'budget'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def action_external(self):
        self.ensure_one()
        self.state = 'external'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"' (إدارة الإتصالات)")

    @api.multi
    def action_communication(self):
        self.ensure_one()
        self.state = 'communication'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"' (إدارة الميزانية)")

    @api.multi
    def action_done(self):
        self.ensure_one()
        for line in self.line_ids:
            job_val = {'name': line.name.id,
                       'number': line.job_number,
                       'type_id': line.type_id.id,
                       'grade_id': line.grade_id.id,
                       'department_id': line.department_id.id,
                       'general_id': self.general_id.id,
                       'specific_id': self.specific_id.id,
                       'serie_id': self.serie_id.id,
                       'is_striped_from': True
                       }
            self.env['hr.job'].create(job_val)
        self.state = 'done'
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت إحداث الوظائف من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def action_refuse(self):
        self.ensure_one()
        self.state = 'new'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم رفض الطلب من قبل '" + unicode(user.name) + u"'")


class HrJobStripFromLine(models.Model):
    _name = 'hr.job.strip.from.line'
    _description = u'الوظائف'

    name = fields.Many2one('hr.job.name', string=u'الوظيفة', required=1)
    number = fields.Char(string=u'الرمز', required=1)
    job_number = fields.Char(string=u'الرقم الوظيفي', required=1)
    type_id = fields.Many2one('salary.grid.type', related="grade_id.type_id", string=u'التصنيف', required=1)
    grade_id = fields.Many2one('salary.grid.grade', string=u'المرتبة', required=1)
    department_id = fields.Many2one('hr.department', string=u'الإدارة', required=1)
    job_strip_from_id = fields.Many2one('hr.job.strip.from', string=u' وظائف')

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.number = self.name.number

    @api.constrains('job_number', 'grade_id')
    def _check_grade_id_job_number(self):
        if self.job_number and self.grade_id:
            # check if there is already a job with same grade and job number
            jobs = self.env['hr.job'].search([])
            for job in jobs:
                if job.grade_id == self.grade_id and job.number == self.job_number:
                    raise ValidationError(u"يوجد وظيفة بنفس الرقم والمرتبة.")

    @api.onchange('grade_id')
    def onchange_grade_id(self):
        res = {}
        # get grades in job_strip_from_id
        if not self.grade_id:
            grade_ids = [rec .id for rec in self.job_strip_from_id.grade_ids]
            res['domain'] = {'grade_id': [('id', 'in', grade_ids)]}
            return res


class HrJobStripTo(models.Model):
    _name = 'hr.job.strip.to'
    _inherit = ['mail.thread']
    _description = u' سلخ وظيفة إلى جهة'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), required=1, readonly=1)
    speech_number = fields.Char(string=u'رقم الخطاب')
    speech_date = fields.Date(string=u'تاريخ الخطاب')
    speech_file = fields.Binary(string=u'صورة الخطاب')
    out_speech_number = fields.Char(string=u'رقم الخطاب الصادر')
    out_speech_date = fields.Date(string=u'تاريخ الخطاب الصادر')
    out_speech_file = fields.Binary(string=u'صورة الخطاب الصادر')
    in_speech_number = fields.Char(string=u'رقم الخطاب الوارد')
    in_speech_date = fields.Date(string=u'تاريخ الخطاب الوارد')
    in_speech_file = fields.Binary(string=u'صورة الخطاب الوارد ')
    line_ids = fields.One2many('hr.job.strip.to.line', 'job_strip_to_id')
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'في إنتظار الموافقة'),
                              ('hrm1', u'شؤون الموظفين'),
                              ('communication', u'إدارة الإتصالات'),
                              ('external', u'وزارة المالية'),
                              ('hrm2', u'شؤون الموظفين'),
                              ('done', u'اعتمدت')
                              ], readonly=1, default='new')

    @api.multi
    def action_waiting(self):
        self.ensure_one()
        self.state = 'waiting'

    @api.multi
    def action_hrm1(self):
        self.ensure_one()
        self.state = 'hrm1'

    @api.multi
    def action_hrm2(self):
        self.ensure_one()
        self.state = 'hrm2'
        # Add to log
        self.message_post(u"تمت الموافقة من قبل الجهة الخارجية (وزارة المالية)")

    @api.multi
    def action_budget(self):
        self.ensure_one()
        self.state = 'budget'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def action_external(self):
        self.ensure_one()
        self.state = 'external'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"' (إدارة الإتصالات)")

    @api.multi
    def action_communication(self):
        self.ensure_one()
        self.state = 'communication'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"' (إدارة الميزانية)")

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.state = 'done'
        for job in self.line_ids:
            job.job_id.state = 'cancel'
            job.job_id.is_striped_to = True
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت إلغاء الوظائف من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def action_refuse(self):
        self.ensure_one()
        self.state = 'new'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم رفض الطلب من قبل '" + unicode(user.name) + u"'")


class HrJobStripToLine(models.Model):
    _name = 'hr.job.strip.to.line'
    _description = u'الوظائف'

    job_strip_to_id = fields.Many2one('hr.job.strip.to', string='الوظيفة', required=1)
    job_id = fields.Many2one('hr.job', string='الوظيفة', required=1)
    type_id = fields.Many2one('salary.grid.type', string='التصنيف', required=1, readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', required=1, readonly=1)
    department_id = fields.Many2one('hr.department', string='الإدارة', required=1, readonly=1)

    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id:
            self.type_id = self.job_id.type_id.id
            self.grade_id = self.job_id.grade_id.id
            self.department_id = self.job_id.department_id.id


class HrJobCancel(models.Model):
    _name = 'hr.job.cancel'
    _inherit = ['mail.thread']
    _description = u' إلغاء الوظائف'
    _rec_name = 'speech_number'

    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), required=1, readonly=1)
    speech_number = fields.Char(string='رقم الخطاب', required=1)
    speech_date = fields.Date(string='تاريخ الخطاب', required=1)
    speech_file = fields.Binary(string='صورة الخطاب', required=1)
    decision_number = fields.Char(string=u'رقم القرار')
    decision_date = fields.Date(string=u'تاريخ القرار')
    decision_file = fields.Binary(string=u'ملف القرار')
    job_cancel_ids = fields.One2many('hr.job.cancel.line', 'job_cancel_line_id')
    state = fields.Selection([('new', 'طلب'),
                              ('waiting', 'في إنتظار الموافقة'),
                              ('hrm', 'شؤون الموظفين'),
                              ('done', 'اعتمدت'),
                              ('refused', 'رفض')],
                             readonly=1, default='new')

    @api.multi
    def action_waiting(self):
        self.ensure_one()
        self.state = 'waiting'

    @api.multi
    def action_hrm(self):
        self.ensure_one()
        self.state = 'hrm'

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.state = 'done'
        for job in self.job_cancel_ids:
            job.job_id.state = 'cancel'
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت إلغاء الوظائف من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def action_refuse(self):
        self.ensure_one()
        self.state = 'refused'
        # send notification for the employee who is request cancelling job
        self.env['base.notification'].create({'title': u'إشعار برفض طلب إلغاء وظيفة',
                                              'message': u'لقد تم رفض طلبكم بإلغاء وظيفة',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'res_model': 'hr.job.cancel',
                                              'res_id': self.id,
                                              'res_action': 'smart_hr.action_hr_job_cancel'})


class HrJobCancelLine(models.Model):
    _name = 'hr.job.cancel.line'
    _description = u'الوظائف'

    job_cancel_line_id = fields.Many2one('hr.job.cancel', string='الوظيفة', required=1)
    job_id = fields.Many2one('hr.job', string='الوظيفة', required=1)
    type_id = fields.Many2one('salary.grid.type', string='التصنيف', required=1, readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', required=1, readonly=1)
    department_id = fields.Many2one('hr.department', string='الإدارة', required=1, readonly=1)

    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id:
            self.type_id = self.job_id.type_id.id
            self.grade_id = self.job_id.grade_id.id
            self.department_id = self.job_id.department_id.id


class HrJobMoveDeparrtment(models.Model):
    _name = 'hr.job.move.department'
    _inherit = ['mail.thread']
    _description = u'نقل وظائف'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), required=1, readonly=1)
    out_speech_number = fields.Char(string=u'رقم الخطاب الصادر')
    out_speech_date = fields.Date(string=u'تاريخ الخطاب الصادر')
    out_speech_file = fields.Binary(string=u'صورة الخطاب الصادر')
    in_speech_number = fields.Char(string=u'رقم الخطاب الوارد')
    in_speech_date = fields.Date(string=u'تاريخ الخطاب الوارد')
    in_speech_file = fields.Binary(string=u'صورة الخطاب الوارد')
    job_movement_ids = fields.One2many('hr.job.move.department.line', 'job_move_department_id')
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'في إنتظار الموافقة'),
                              ('hrm1', u'شؤون الموظفين'),
                              ('budget', u'إدارة الميزانية'),
                              ('communication', u'إدارة الإتصالات'),
                              ('external', u'وزارة الخدمة المدنية'),
                              ('hrm2', u'شؤون الموظفين'),
                              ('done', u'اعتمدت')
                              ], readonly=1, default='new')

    @api.multi
    def action_waiting(self):
        self.ensure_one()
        self.state = 'waiting'

    @api.multi
    def action_hrm1(self):
        self.ensure_one()
        self.state = 'hrm1'

    @api.multi
    def action_budget(self):
        self.ensure_one()
        self.action_job_reserve()
        self.state = 'budget'

    @api.multi
    def action_communication(self):
        self.ensure_one()
        self.state = 'communication'

    @api.multi
    def action_external(self):
        self.ensure_one()
        self.state = 'external'

    @api.multi
    def action_hrm2(self):
        self.ensure_one()
        self.state = 'hrm2'

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.state = 'done'
        for job in self.job_movement_ids:
            job.job_id.grade_id = job.new_grade_id.id
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت نقل الوظائف من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def action_refuse(self):
        self.ensure_one()
        self.state = 'new'

    @api.multi
    def action_job_unreserve(self):
        self.ensure_one()
        for rec in self.job_movement_ids:
            rec.job_id.write({'is_occupied': False, 'department_id': rec.new_department_id.id})
        self.state = 'done'

    @api.multi
    def action_job_reserve(self):
        self.ensure_one()
        for rec in self.job_movement_ids:
            rec.job_id.write({'is_occupied': True})


class HrJobMoveDeparrtmentLine(models.Model):
    _name = 'hr.job.move.department.line'
    _description = u'نقل وظائف'

    job_id = fields.Many2one('hr.job', string='الوظيفة', required=1)
    type_id = fields.Many2one('salary.grid.type', string='التصنيف', readonly=1, required=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة ', readonly=1, required=1)
    department_id = fields.Many2one('hr.department', string=' الإدارة الحالية', readonly=1, required=1)
    new_department_id = fields.Many2one('hr.department', string='الإدارة الجديد', required=1)
    job_move_department_id = fields.Many2one('hr.job.move.department', string='الوظيفة', required=1)

    @api.onchange('job_id')
    def _onchange_job_id(self):
        res = {}
        if not self.job_id and self._context['job_movement_ids']:
            job_ids = [rec[2]['job_id'] for rec in self._context['job_movement_ids']]
            nex_job_ids = [rec.id for rec in self.env['hr.job'].search([('id', 'not in', job_ids)])]
            res['domain'] = {'job_id': [('id', 'in', nex_job_ids)]}

        if self.job_id:
            self.type_id = self.job_id.type_id.id
            self.grade_id = self.job_id.grade_id.id
            self.department_id = self.job_id.department_id.id
        return res


class HrJobMoveGrade(models.Model):
    _name = 'hr.job.move.grade'
    _inherit = ['mail.thread']
    _description = u'رفع أو خفض وظائف'
    _rec_name = 'decision_number'

    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), required=1, readonly=1)
    decision_number = fields.Char(string=u'رقم القرار', required=1)
    decision_date = fields.Date(string=u'تاريخ القرار', required=1)
    move_date = fields.Date(string=u'التاريخ', readonly=1, default=fields.Datetime.now(), required=1)
    fiscal_year = fields.Char(string='السنه المالية', default=(date.today().year), readonly=1)
    out_speech_number = fields.Char(string=u'رقم الخطاب الصادر')
    out_speech_date = fields.Date(string=u'تاريخ الخطاب الصادر')
    out_speech_file = fields.Binary(string=u'صورة الخطاب الصادر')
    in_speech_number = fields.Char(string=u'رقم الخطاب الوارد')
    in_speech_date = fields.Date(string=u'تاريخ الخطاب الوارد')
    in_speech_file = fields.Binary(string=u'صورة الخطاب الوارد')
    job_movement_ids = fields.One2many('hr.job.move.grade.line', 'job_movement_line_id')
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'في إنتظار الموافقة'),
                              ('hrm1', u'شؤون الموظفين'),
                              ('budget', u'إدارة الميزانية'),
                              ('communication', u'إدارة الإتصالات'),
                              ('external', u'وزارة المالية'),
                              ('hrm2', u'شؤون الموظفين'),
                              ('done', u'اعتمدت')
                              ], readonly=1, default='new')
    move_type = fields.Selection([('scale_up', u'رفع'),
                                  ('scale_down', u'خفض')
                                  ])

    @api.multi
    def action_waiting(self):
        self.ensure_one()
        self.state = 'waiting'

    @api.multi
    def action_hrm1(self):
        self.ensure_one()
        self.state = 'hrm1'

    @api.multi
    def action_budget(self):
        self.ensure_one()
        self.action_job_reserve()
        self.state = 'budget'

    @api.multi
    def action_communication(self):
        self.ensure_one()
        self.state = 'communication'

    @api.multi
    def action_external(self):
        self.ensure_one()
        self.state = 'external'

    @api.multi
    def action_hrm2(self):
        self.ensure_one()
        self.state = 'hrm2'

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.state = 'done'
        for job in self.job_movement_ids:
            job.job_id.grade_id = job.new_grade_id.id
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت " + self.move_type + u" الوظائف من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def action_refuse(self):
        self.ensure_one()
        self.state = 'new'

    @api.multi
    def action_job_unreserve(self):
        self.ensure_one()
        for rec in self.job_movement_ids:
            rec.job_id.write({'is_occupied': False, 'number': rec.job_number, 'grade_id': rec.new_grade_id.id})
        self.state = 'done'

    @api.multi
    def action_job_reserve(self):
        self.ensure_one()
        for rec in self.job_movement_ids:
            rec.job_id.write({'is_occupied': True})


class HrJobMoveGradeLine(models.Model):
    _name = 'hr.job.move.grade.line'
    _description = u'رفع أو خفض وظائف'

    job_movement_line_id = fields.Many2one('hr.job.move.grade', string='الوظيفة', required=1, ondelete="cascade")
    job_id = fields.Many2one('hr.job', string='الوظيفة', domain=[('state', '=', 'unoccupied'), ('is_occupied', '=', False)], required=1)
    type_id = fields.Many2one('salary.grid.type', string='التصنيف', readonly=1, required=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة الحالية', readonly=1, required=1)
    new_grade_id = fields.Many2one('salary.grid.grade', string=' المرتبة الجديد', required=1)
    department_id = fields.Many2one('hr.department', string='الإدارة', readonly=1, required=1)
    job_number = fields.Char(string='الرقم الوظيفي', required=1)

    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id:
            self.type_id = self.job_id.type_id.id
            self.grade_id = self.job_id.grade_id.id
            self.department_id = self.job_id.department_id.id
            self.job_number = self.job_id.number
            res = {}
            grade_ids = []
            # get availble grades depend on move_type type رفع أو خفض
            for rec in self.job_id.serie_id.hr_classment_job_ids:
                print self._context
                if self._context['operation'] == 'scale_down':
                    if int(self.job_id.grade_id.code) > int(rec.grade_id.code):
                        grade_ids.append(rec.grade_id.id)
                if self._context['operation'] == 'scale_up':
                    if int(self.job_id.grade_id.code) < int(rec.grade_id.code):
                        grade_ids.append(rec.grade_id.id)
            res['domain'] = {'new_grade_id': [('id', 'in', grade_ids)]}
            return res

    @api.constrains('job_number', 'new_grade_id')
    def _check_new_grade_id_job_number(self):
        if self.job_number and self.new_grade_id:
            # check if there is already a job with new grade and same job number
            jobs = self.env['hr.job'].search([])
            for job in jobs:
                if job.grade_id == self.new_grade_id and job.number == self.job_number:
                    raise ValidationError(u"يوجد وظيفة بنفس الرقم والمرتبة.")


class HrJobMoveUpdate(models.Model):
    _name = 'hr.job.update'
    _inherit = ['mail.thread']
    _description = u'تحوير‬ وظائف'
    _rec_name = "employee_id"

    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), required=1, readonly=1)
    out_speech_number = fields.Char(string=u'رقم الخطاب الصادر')
    out_speech_date = fields.Date(string=u'تاريخ الخطاب الصادر')
    out_speech_file = fields.Binary(string=u'صورة الخطاب الصادر')
    in_speech_number = fields.Char(string=u'رقم الخطاب الوارد')
    in_speech_date = fields.Date(string=u'تاريخ الخطاب الوارد')
    in_speech_file = fields.Binary(string=u'صورة الخطاب الوارد')
    job_update_ids = fields.One2many('hr.job.update.line', 'job_update_line_id')
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'في إنتظار الموافقة'),
                              ('hrm1', u'شؤون الموظفين'),
                              ('budget', u'إدارة الميزانية'),
                              ('communication', u'إدارة الإتصالات'),
                              ('external', u'وزارة الخدمة المدنية'),
                              ('hrm2', u'شؤون الموظفين'),
                              ('done', u'اعتمدت')
                              ], readonly=1, default='new')

    @api.multi
    def action_waiting(self):
        self.ensure_one()
        self.state = 'waiting'

    @api.multi
    def action_hrm1(self):
        self.ensure_one()
        self.state = 'hrm1'

    @api.multi
    def action_budget(self):
        self.ensure_one()
        self.action_job_reserve()
        self.state = 'budget'

    @api.multi
    def action_communication(self):
        self.ensure_one()
        self.state = 'communication'

    @api.multi
    def action_external(self):
        self.ensure_one()
        self.state = 'external'

    @api.multi
    def action_hrm2(self):
        self.ensure_one()
        self.state = 'hrm2'

    @api.multi
    def action_refuse(self):
        self.ensure_one()
        self.state = 'new'

    @api.multi
    def action_job_unreserve(self):
        self.ensure_one()
        for rec in self.job_update_ids:
            rec.job_id.write({'is_occupied': False})
            rec.job_id.name = rec.new_name
            rec.job_id.date_update = datetime.now()
            rec.job_id.type_id = rec.new_type_id
        self.state = 'done'
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم تحوير‬ الوظائف من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def action_job_reserve(self):
        self.ensure_one()
        for rec in self.job_update_ids:
            rec.job_id.write({'is_occupied': True})


class HrJobMoveUpdateLine(models.Model):
    _name = 'hr.job.update.line'
    _description = u'تحوير‬ وظيفة'

    job_update_line_id = fields.Many2one('hr.job.update', string=u'التحوير‬')
    job_id = fields.Many2one('hr.job', string=u'الوظيفة', required=1)
    old_name = fields.Many2one('hr.job.name', related='job_id.name', readonly=1, string=u'المسمى الحالي', required=1)
    new_name = fields.Many2one('hr.job.name', string=u'المسمى الجديد', required=1)
    old_type_id = fields.Many2one('salary.grid.type', related='job_id.type_id', string=u'التصنيف الحالي', readonly=1, required=1)
    new_type_id = fields.Many2one('salary.grid.type', string=u'التصنيف الجديد', required=1)
    grade_id = fields.Many2one('salary.grid.grade', related='job_id.grade_id', string=u'المرتبة', readonly=1, required=1)
    department_id = fields.Many2one('hr.department', related='job_id.department_id', string=u'الإدارة', readonly=1, required=1)

    @api.onchange('job_id')
    def onchange_job_id(self):
        if not self.job_id:
            res = {}
            # get jobs that are  updated or created from more than one year
            all_job_ids = self.env['hr.job'].search([])
            print all_job_ids
            job_ids = []
            for job in all_job_ids:
                now_date = fields.Date.from_string(fields.Datetime.now())
                if job.update_date:
                    update_date = fields.Date.from_string(job.update_date)
                    diff = relativedelta(now_date, update_date).years
                    if diff >= 1:
                        job_ids.append(job.id)
                else:
                    create_date = fields.Date.from_string(job.create_date)
                    diff = relativedelta(now_date, create_date).years
                    if diff >= 1:
                        job_ids.append(job.id)
            res['domain'] = {'job_id': [('id', 'in', job_ids)]}
            return res
