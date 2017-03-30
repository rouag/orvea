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

    name = fields.Many2one('hr.job.name', string='المسمى الوظيفي', required=1)
    name_number = fields.Char(related='name.number', string=u'الرمز الوظيفي', readonly=1)
    job_name_code = fields.Char(related="name.number", string='الرمز', required=1)
    activity_type = fields.Many2one('hr.job.type.activity', string=u'نوع النشاط')
    number = fields.Char(string='رقم الوظيفة', required=1, states={'unoccupied': [('readonly', 0)]})
    department_id = fields.Many2one('hr.department', string='الإدارة', required=1,
                                    states={'unoccupied': [('readonly', 0)]})
    general_id = fields.Many2one('hr.groupe.job', ' المجموعة العامة', ondelete='cascade', required=1)
    specific_id = fields.Many2one('hr.groupe.job', ' المجموعة النوعية', ondelete='cascade', required=1)
    serie_id = fields.Many2one('hr.groupe.job', ' سلسلة الفئات', ondelete='cascade', required=1)
    type_id = fields.Many2one('salary.grid.type', string='نوع السلم', required=1, states={'unoccupied': [('readonly', 0)]})
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', required=1,
                               states={'unoccupied': [('readonly', 0)]})
    state = fields.Selection(
        [('unoccupied', u'شاغرة'), ('occupied', u'مشغولة'), ('cancel', u'ملغاة'), ('reserved', u'محجوزة')],
        string=u'الحالة', readonly=1, default='unoccupied')
    state_job = fields.Selection(
        [('unoccupied', u'شاغرة'), ('occupied', u'مشغولة'), ('cancel', u'ملغاة'), ('reserved', u'محجوزة'),
         ('offer', u'إعلان'), ('addjustment', u'تحوير'), ('transfert', u'نقل'), ('recrutment', u'تعيين'),
         ('service_transfet', u'نقل خدمات'), ('promotion', u'ترقية'), ('mission', u'تكليف'), ('increase', u'رفع'),
         ('decrease', u'خفظ')], string=u'الحالة', readonly=1, default='unoccupied')
    employee = fields.Many2one('hr.employee', string=u'الموظف')
    occupied_date = fields.Date(string=u'تاريخ شغلها')
    creation_source = fields.Selection([('creation', u'إحداث'), ('striped_from', u'سلخ  من جهة'),
                                        ('striped_to', u'سلخ إلى جهة'), ('cancel', u'إلغاء'),
                                        ('scale_up', u'رفع'), ('scale_down', u'خفض'), ('update', u'تحوير‬'),
                                        ('move', u'نقل')], readonly=1, string=u'المصدر')
    # حجز الوظيفة
    occupation_date_from = fields.Date(string=u'حجز الوظيفة من')
    occupation_date_to = fields.Date(string=u'حجز الوظيفة الى', )
    is_occupied_compute = fields.Boolean(string='is occupied compute', compute='_compute_is_occupated')
    # سلخ
    is_striped_to = fields.Boolean(string='is striped to', default=False)
    # تحوير‬
    update_date = fields.Date(string=u'تاريخ التحوير')
    type_resevation = fields.Selection([('promotion', u'للترقية')], string=u'نوع الحجز')
    occupied_promotion = fields.Boolean(string='للترقية', )
    promotion_employee_id = fields.Many2one('hr.promotion.employee.job', string=u'الموظف')
    history_ids = fields.One2many('hr.job.history.actions', 'job_id', string=u'سجل الاجرءات')

    @api.multi
    @api.depends('occupation_date_to')
    def _compute_is_occupated(self):
        for rec in self:
            if rec.occupation_date_to < datetime.today().strftime('%Y-%m-%d') and rec.state == 'reserved':
                rec.action_job_unreserve()

    @api.multi
    def action_job_unreserve(self):
        self.ensure_one()
        self.occupation_date_from = False
        self.occupation_date_to = False
        self.state = 'unoccupied'
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت رفع الحجز من قبل '" + unicode(user.name) + u"'")

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


class HrJobHistoryActions(models.Model):
    _name = 'hr.job.history.actions'
    _description = u'سجل الاجرا ءات'

    action = fields.Char(string=u' الاجراء')
    action_date = fields.Date(string=u'التاريخ')
    description = fields.Text(string=u'تفصيل الاجراء')
    job_id = fields.Many2one(string=u'الوظيفة')


class HrJobName(models.Model):
    _name = 'hr.job.name'
    _description = u'المسميات الوظيفية '
    _rec_name = 'name'

    name = fields.Char(string=u'المسمى', required=1)
    number = fields.Char(string=u'الرمز', required=1)
    job_nature = fields.Selection([('supervisory', u'اشرافية'), ('not_supervisory', u'غير اشرافية')],
                                  string=u'طبيعة الوظيفة', default='not_supervisory')
    job_supervisory_name_id = fields.Many2one('hr.job.name', string=u'المسمى المشرف')
    job_supervised_name_ids = fields.One2many('hr.job.name', 'job_supervisory_name_id', string=u'المسميات المشرف عليها',
                                              readonlly=1)

    job_description = fields.Text(string=u'متطلبات الوظيفية')
    members_job = fields.Boolean(string=u'وظيفية للاعضاء')

    _sql_constraints = [('number_uniq', 'unique(number)', 'رمز هذا المسمى موجود.')]


class HrJobReservation(models.Model):
    _name = 'hr.job.reservation'
    _description = u'الوظائف'
    _rec_name = 'date_from'

    date_from = fields.Date(string=u'التاريخ من', readonly=1, default=fields.Datetime.now())
    date_to = fields.Date(string=u'التاريخ الى')
    type_resevation = fields.Selection([('promotion', u'للترقية')], string=u'نوع الحجز')

    @api.onchange('date_from', 'date_to')
    def onchange_dates(self):
        self.ensure_one()
        if self.date_from and self.date_to:
            if self.date_from >= self.date_to:
                raise ValidationError(u"تاريخ من يجب ان يكون أصغر من تاريخ الى")

    @api.multi
    def action_job_reserve_confirm(self):
        if self.date_from and self.date_to:
            self.env['hr.job'].search([('id', '=', self._context['job_id'])]).write(
                {'occupation_date_from': self.date_from, 'occupation_date_to': self.date_to, 'state': 'reserved',
                 'type_resevation': self.type_resevation})


class HrJobCreate(models.Model):
    _name = 'hr.job.create'
    _inherit = ['mail.thread']
    _description = u'إحداث وظائف'

    name = fields.Char(string='مسمى الطلب', required=1, readonly=1, states={'new': [('readonly', 0)]})
    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', required=1, readonly=1,
                                  domain=[('emp_state', 'not in', ['suspended', 'terminated']), ('employee_state', '=', 'employee')],
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid), ('emp_state', 'not in', ['suspended', 'terminated'])], limit=1))
    fiscal_year = fields.Char(string='السنه المالية', default=(date.today().year), readonly=1)
    decision_number = fields.Char(string=u"رقم القرار")
    decision_date = fields.Date(string=u'تاريخ القرار')
    decision_file = fields.Binary(string=u'نسخة القرار', attachment=True)
    decision_file_name = fields.Char(string=u'نسخة القرار مسمى')
    speech_number = fields.Char(string=u'رقم الخطاب')
    speech_date = fields.Date(string=u'تاريخ الخطاب')
    speech_file = fields.Binary(string=u'صورة الخطاب', attachment=True)
    speech_file_name = fields.Char(string=u'مسمى صورة الخطاب')
    line_ids = fields.One2many('hr.job.create.line', 'job_create_id', readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'صاحب الصلاحية'),
                              ('budget_external', u'إدارة الميزانية - وزارة المالية'),
                              ('hrm', u'شؤون الموظفين'),
                              ('done', u'اعتمدت'),
                              ('refused', u'رفض')
                              ], readonly=1, default='new', string=u'الحالة')
    general_id = fields.Many2one('hr.groupe.job', ' المجموعة العامة', ondelete='cascade')
    specific_id = fields.Many2one('hr.groupe.job', ' المجموعة النوعية', ondelete='cascade')
    serie_id = fields.Many2one('hr.groupe.job', ' سلسلة الفئات', ondelete='cascade')
    grade_ids = fields.One2many('salary.grid.grade', 'job_create_id', string='المرتبة')
    draft_budget = fields.Binary(string=u'مشروع الميزانية', attachment=True)
    draft_budget_name = fields.Char(string=u'مشروع الميزانية مسمى ')
    members_job = fields.Boolean(string=u'وظيفية للاعضاء')

    @api.onchange('serie_id')
    def onchange_serie_id(self):
        if self.serie_id:
            grides = []
            # get grades in job_create_id
            for rec in self.env['salary.grid.grade'].search([]):
                if int(rec.code) >= int(self.serie_id.rank_from.code) and int(rec.code) <= int(
                        self.serie_id.rank_to.code):
                    grides.append(rec.id)
            self.grade_ids = grides

    @api.multi
    def action_waiting(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError(u"الرجاء ادخال وظيفة.")
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_autority_owner')):
            self.state = 'waiting'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__minis')):
            self.state = 'budget_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm'
        else:
            raise ValidationError(u"الرجاء التحقق من إعدادات المخطط الإنسيابي.")

    @api.multi
    def action_hrm(self):
        self.ensure_one()
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm'
        else:
            self.action_done()
        # Add to log
        self.message_post(u"تمت الموافقة من قبل الجهة الخارجية (وزارة المالية)")

    @api.multi
    def action_budget(self):
        self.ensure_one()
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__minis')):
            self.state = 'budget_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm'
        else:
            self.action_done()
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def action_done(self):
        self.ensure_one()
        user = self.env['res.users'].browse(self._uid)
        for line in self.line_ids:
            job_val = {'name': line.name.id,
                       'number': line.job_number,
                       'type_id': line.type_id.id,
                       'grade_id': line.grade_id.id,
                       'department_id': line.department_id.id,
                       'general_id': self.general_id.id,
                       'specific_id': self.specific_id.id,
                       'serie_id': self.serie_id.id,
                       'activity_type': line.activity_type.id,
                       'creation_source': 'creation'

                       }
            job_id = self.env['hr.job'].create(job_val)
            description = u" إحداث الوظيفة من قبل " + " " + unicode(user.name) + u"'"
            job_history_vals = {
                'action': 'إحداث الوظيفة',
                'action_date': date.today(),
                'description': description,
                'job_id': job_id.id,
                }
            self.env['hr.job.history.actions'].create(job_history_vals)
        self.state = 'done'
        self.message_post(u"تمت إحداث الوظائف من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def button_refuse(self):
        self.ensure_one()
        self.state = 'refused'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم رفض الطلب من قبل '" + unicode(user.name) + u"'")

        # send notification for the employee
        self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                              'message': u'لقد تم إشعار رفض طلب إحداث وظائف',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'res_id': self.id,
                                              'res_action': 'smart_hr.action_hr_job_create',
                                              'notif': True
                                              })

    def check_workflow_state(self, state):
        '''
        @param state: hr.job.workflow.state
        @return Boolean
        '''
        work_obj = self.env.ref('smart_hr.work_job_creation_workflow')
        if work_obj:
            return state in work_obj.state_ids
        else:
            return False


class HrJobCreateLine(models.Model):
    _name = 'hr.job.create.line'
    _description = u'الوظائف'
    _rec_name = 'name'

    name = fields.Many2one('hr.job.name', string='الوظيفة', required=1)
    number = fields.Char(string='الرمز', required=1)
    activity_type = fields.Many2one('hr.job.type.activity', string=u'نوع النشاط', required=1)
    job_nature = fields.Selection([('supervisory', u'اشرافية'), ('not_supervisory', u'غير اشرافية')],
                                  string=u'طبيعة الوظيفة', default='not_supervisory')
    job_number = fields.Char(string='رقم الوظيفة', required=1)
    type_id = fields.Many2one('salary.grid.type', string='نوع السلم', required=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', required=1)
    department_id = fields.Many2one('hr.department', string='الإدارة', required=1)
    job_create_id = fields.Many2one('hr.job.create', string=' وظائف')

    @api.onchange('name')
    def onchange_name(self):
        res = {}
        if self.name:
            self.number = self.name.number
        if not self.name:
            name_ids = [rec.id for rec in self.job_create_id.serie_id.job_name_ids]
            if self.job_create_id.members_job is True:
                new_name_ids = self.env['hr.job.name'].search([('members_job', '=', True), ('id', 'in', name_ids)])
                res['domain'] = {'name': [('id', 'in', new_name_ids.ids)]}
            else:
                new_name_ids = self.env['hr.job.name'].search([('members_job', '=', False), ('id', 'in', name_ids)])
                res['domain'] = {'name': [('id', 'in', new_name_ids.ids)]}
            return res

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
            grade_ids = [rec.id for rec in self.job_create_id.grade_ids]
            res['domain'] = {'grade_id': [('id', 'in', grade_ids)]}
            return res


class HrJobStripFrom(models.Model):
    _name = 'hr.job.strip.from'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    _description = u'سلخ وظائف من جهة'

    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', required=1, readonly=1,
                                  domain=[('emp_state', 'not in', ['suspended', 'terminated']), ('employee_state', '=', 'employee')],
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid), ('emp_state', 'not in', ['suspended', 'terminated'])], limit=1))

    fiscal_year = fields.Char(string='السنه المالية', default=(date.today().year), readonly=1)
    source_location = fields.Many2one('res.partner', string=u"المصدر",
                                      domain=[('company_type', '=', 'governmental_entity')], required=1, readonly=1,
                                      states={'new': [('readonly', 0)]})
    speech_number = fields.Char(string=u'رقم الخطاب')
    speech_date = fields.Date(string=u'تاريخ الخطاب')
    speech_file = fields.Binary(string=u'صورة الخطاب', attachment=True)
    out_speech_number = fields.Char(string=u'رقم الخطاب الصادر')
    out_speech_date = fields.Date(string=u'تاريخ الخطاب الصادر')
    out_speech_file = fields.Binary(string=u'صورة الخطاب الصادر', attachment=True)
    in_speech_number = fields.Char(string=u'رقم الخطاب الوارد')
    in_speech_date = fields.Date(string=u'تاريخ الخطاب الوارد')
    in_speech_file = fields.Binary(string=u'صورة الخطاب الوارد ', attachment=True)
    line_ids = fields.One2many('hr.job.strip.from.line', 'job_strip_from_id', readonly=1,
                               states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'صاحب الصلاحية'),
                              ('hrm1', u'شؤون الموظفين'),
                              ('communication', u'إدارة الاتصالات - جهة التوظيف الأصلية'),
                              ('external', u'وزارة المالية'),
                              ('hrm2', u'شؤون الموظفين'),
                              ('done', u'اعتمدت'),
                              ('refused', u'رفض')
                              ], readonly=1, default='new')
    general_id = fields.Many2one('hr.groupe.job', ' المجموعة العامة', ondelete='cascade')
    specific_id = fields.Many2one('hr.groupe.job', ' المجموعة النوعية', ondelete='cascade')
    serie_id = fields.Many2one('hr.groupe.job', ' سلسلة الفئات', ondelete='cascade')
    grade_ids = fields.One2many('salary.grid.grade', 'job_strip_from_id', string='المرتبة')
    speech_file_name = fields.Char(string=u'مسمى صورة الخطاب')
    out_speech_file_name = fields.Char(string=u'مسمى صورة الخطاب الصادر')
    in_speech_name = fields.Char(string=u'مسمى صورة الخطاب الوارد')

    @api.onchange('serie_id')
    def onchange_serie_id(self):
        if self.serie_id:
            grides = []
            # get grades in job_create_id
            for rec in self.env['salary.grid.grade'].search([]):
                if int(rec.code) >= int(self.serie_id.rank_from.code) and int(rec.code) <= int(
                        self.serie_id.rank_to.code):
                    grides.append(rec.id)
            self.grade_ids = grides

    @api.multi
    def action_waiting(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError(u"الرجاء ادخال وظيفة.")
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_autority_owner')):
            self.state = 'waiting'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm1'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_comm_orig_employer')):
            self.state = 'communication'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg')):
            self.state = 'external'
        else:
            raise ValidationError(u"الرجاء التحقق من إعدادات المخطط الإنسيابي.")

    @api.multi
    def action_hrm1(self):
        self.ensure_one()
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm1'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_comm_orig_employer')):
            self.state = 'communication'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg')):
            self.state = 'external'
        else:
            self.action_done()
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت المصادقة من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def action_hrm2(self):
        self.ensure_one()
        self.state = 'hrm2'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت المصادقة من قبل '" + unicode(user.name) + u"' (وزارة المالية)")

    @api.multi
    def action_budget(self):
        self.ensure_one()
        self.state = 'budget'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def action_communication(self):
        self.ensure_one()
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_comm_orig_employer')):
            self.state = 'communication'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg')):
            self.state = 'external'
        else:
            self.action_done()
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"' (إدارة الميزانية)")

    @api.multi
    def action_external(self):
        self.ensure_one()
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_budg')):
            self.state = 'external'
        else:
            self.action_done()
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"' (إدارة الإتصالات)")

    @api.multi
    def action_done(self):
        self.ensure_one()
        user = self.env['res.users'].browse(self._uid)
        for line in self.line_ids:
            job_val = {'name': line.name.id,
                       'number': line.job_number,
                       'type_id': line.type_id.id,
                       'grade_id': line.grade_id.id,
                       'department_id': line.department_id.id,
                       'general_id': self.general_id.id,
                       'specific_id': self.specific_id.id,
                       'serie_id': self.serie_id.id,
                       'creation_source': 'striped_from'
                       }
            job_id = self.env['hr.job'].create(job_val)
            description = u" إحداث الوظيفة بسلخ من قبل " + " " + unicode(user.name) + u"'"
            job_history_vals = {
                'action': 'إحداث بسلخ',
                'action_date': date.today(),
                'description': description,
                'job_id':job_id.id
                }
            self.env['hr.job.history.actions'].create(job_history_vals)
        self.state = 'done'
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت إحداث الوظائف من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def button_refuse(self):
        self.ensure_one()
        self.state = 'refused'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم رفض الطلب من قبل '" + unicode(user.name) + u"'")
        # send notification for the employee
        self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                              'message': u'لقد تم إشعار رفض طلب سلخ وظائف من جهة',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'res_id': self.id,
                                              'res_action': 'smart_hr.action_hr_job_strip_from',
                                              'notif': True
                                              })

    def check_workflow_state(self, state):
        '''
        @param state: hr.job.workflow.state
        @return Boolean
        '''
        work_obj = self.env.ref('smart_hr.work_job_scale_workflow')
        if work_obj:
            return state in work_obj.state_ids
        else:
            return False


class HrJobStripFromLine(models.Model):
    _name = 'hr.job.strip.from.line'
    _description = u'الوظائف'
    _rec_name = 'name'

    name = fields.Many2one('hr.job.name', string=u'الوظيفة', required=1)
    job_name_code = fields.Char(related="name.number", string='الرمز', required=1)
    number = fields.Char(string=u'الرمز', required=1)
    job_number = fields.Char(string=u'رقم الوظيفة', required=1)
    type_id = fields.Many2one('salary.grid.type', string=u'نوع السلم', required=1)
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
            grade_ids = [rec.id for rec in self.job_strip_from_id.grade_ids]
            res['domain'] = {'grade_id': [('id', 'in', grade_ids)]}
            return res


class HrJobStripTo(models.Model):
    _name = 'hr.job.strip.to'
    _inherit = ['mail.thread']
    _description = u' سلخ وظيفة إلى جهة'
    _rec_name = 'employee_id'

    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', required=1, readonly=1,
                                  domain=[('emp_state', 'not in', ['suspended', 'terminated']), ('employee_state', '=', 'employee')],
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid), ('emp_state', 'not in', ['suspended', 'terminated'])], limit=1))
    speech_number = fields.Char(string=u'رقم الخطاب')
    destination_location = fields.Many2one('res.partner', string=u"الوجهة",
                                           domain=[('company_type', '=', 'governmental_entity')], required=1,
                                           readonly=1, states={'new': [('readonly', 0)]})
    speech_date = fields.Date(string=u'تاريخ الخطاب')
    speech_file = fields.Binary(string=u'صورة الخطاب', attachment=True)
    decision_number = fields.Char(string=u"رقم القرار")
    decision_date = fields.Date(string=u'تاريخ القرار')
    decision_file = fields.Binary(string=u'نسخة القرار', attachment=True)
    # قرار طي القيد
    decision_col_const_number = fields.Char(string=u"رقم قرار طي القيد")
    decision_col_const_date = fields.Date(string=u'تاريخ قرار طي القيد')
    decision_col_const_file = fields.Binary(string=u'نسخة قرار طي القيد', attachment=True)

    out_speech_number = fields.Char(string=u'رقم الخطاب الصادر')
    out_speech_date = fields.Date(string=u'تاريخ الخطاب الصادر')
    out_speech_file = fields.Binary(string=u'صورة الخطاب الصادر', attachment=True)
    in_speech_number = fields.Char(string=u'رقم الخطاب الوارد')
    in_speech_date = fields.Date(string=u'تاريخ الخطاب الوارد')
    in_speech_file = fields.Binary(string=u'صورة الخطاب الوارد ', attachment=True)
    line_ids = fields.One2many('hr.job.strip.to.line', 'job_strip_to_id')
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'صاحب الصلاحية'),
                              ('hrm1', u'شؤون الموظفين'),
                              ('communication_external', u'إدارة الإتصالات - وزارة المالية'),
                              ('hrm2', u'شؤون الموظفين'),
                              ('done', u'اعتمدت'),
                              ('refused', u'رفض')
                              ], readonly=1, default='new')
    speech_file_name = fields.Char(string=u'مسمى صورة الخطاب')
    out_speech_file_name = fields.Char(string=u'مسمى صورة الخطاب الصادر')
    in_speech_file_name = fields.Char(string=u'مسمى صورة الخطاب الوارد')

    @api.multi
    def action_waiting(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError(u"الرجاء ادخال وظيفة.")
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_autority_owner')):
            self.state = 'waiting'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm1'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__comm')):
            self.state = 'communication_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'
        else:
            raise ValidationError(u"الرجاء التحقق من إعدادات المخطط الإنسيابي.")

    @api.multi
    def action_hrm1(self):
        self.ensure_one()
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm1'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__comm')):
            self.state = 'communication_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'
        else:
            self.action_done()

    @api.multi
    def action_hrm2(self):
        self.ensure_one()
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'
            # Add to log
            self.message_post(u"تمت الموافقة من قبل الجهة الخارجية (وزارة المالية)")
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__comm')):
            self.state = 'communication_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'
        else:
            self.action_done()

    @api.multi
    def action_budget(self):
        self.ensure_one()
        self.state = 'budget'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def action_communication(self):
        self.ensure_one()
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__comm')):
            self.state = 'communication_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'
        else:
            self.action_done()
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"' (إدارة الميزانية)")

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.state = 'done'
        user = self.env['res.users'].browse(self._uid)
        for job in self.line_ids:
            job.job_id.state = 'cancel'
            job.job_id.is_striped_to = True
            job.job_id.creation_source = 'striped_to'
            description = u" إلغاء الوظيفة بسلخها الى " + " " + unicode(self.destination_location) + " " + u"من قبل" + " " + unicode(user.name) + u"'"
            job_history_vals = {
                'action': 'سلخ إلى جهة   ',
                'action_date': date.today(),
                'description': description,
                'job_id': job.job_id.id
                }
            self.env['hr.job.history.actions'].create(job_history_vals)
        self.message_post(u"تمت إلغاء الوظائف من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def button_refuse(self):
        self.ensure_one()
        self.state = 'refused'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم رفض الطلب من قبل '" + unicode(user.name) + u"'")
        # send notification for the employee
        self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                              'message': u'لقد تم إشعار رفض طلب سلخ وظيفة إلى جهة',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'res_id': self.id,
                                              'res_action': 'smart_hr.action_hr_job_strip_to',
                                              'notif': True
                                              })

    def check_workflow_state(self, state):
        '''
        @param state: hr.job.workflow.state
        @return Boolean
        '''
        work_obj = self.env.ref('smart_hr.work_job_scale_workflow')
        if work_obj:
            return state in work_obj.state_ids
        else:
            return False


class HrJobStripToLine(models.Model):
    _name = 'hr.job.strip.to.line'
    _description = u'الوظائف'
    _rec_name = 'job_id'

    job_strip_to_id = fields.Many2one('hr.job.strip.to', string='الوظيفة', required=1)
    job_id = fields.Many2one('hr.job', string='الوظيفة', required=1)
    job_number = fields.Char(related='job_id.number', string='رقم الوظيفة', readonly=1)
    job_name_code = fields.Char(related="job_id.name.number", string='الرمز', required=1, readonly=1)
    type_id = fields.Many2one('salary.grid.type', string='نوع السلم', required=1, readonly=1)
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

    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', required=1, readonly=1,
                                  domain=[('emp_state', 'not in', ['suspended', 'terminated']), ('employee_state', '=', 'employee')],
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid), ('emp_state', 'not in', ['suspended', 'terminated'])], limit=1))

    speech_number = fields.Char(string='رقم الخطاب', required=1)
    speech_date = fields.Date(string='تاريخ الخطاب', required=1)
    speech_file = fields.Binary(string='صورة الخطاب', required=1, attachment=True)
    decision_number = fields.Char(string=u'رقم القرار')
    decision_date = fields.Date(string=u'تاريخ القرار')
    decision_file = fields.Binary(string=u'نسخة القرار', attachment=True)
    job_cancel_ids = fields.One2many('hr.job.cancel.line', 'job_cancel_line_id')
    state = fields.Selection([('new', 'طلب'),
                              ('waiting', 'صاحب الصلاحية'),
                              ('hrm', 'شؤون الموظفين'),
                              ('done', 'اعتمدت'),
                              ('refused', 'رفض')],
                             readonly=1, default='new')
    speech_file_name = fields.Char(string=u'مسمى صورة الخطاب')
    decision_file_name = fields.Char(string=u'مسمى نسخة القرار')

    @api.multi
    def action_waiting(self):
        self.ensure_one()
        if not self.job_cancel_ids:
            raise ValidationError(u"الرجاء ادخال وظيفة.")
        self.state = 'waiting'

    @api.multi
    def action_hrm(self):
        self.ensure_one()
        self.state = 'hrm'

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.state = 'done'
        user = self.env['res.users'].browse(self._uid)
        for job in self.job_cancel_ids:
            job.job_id.state = 'cancel'
            job.job_id.creation_source = 'cancel'
            description = u" إلغاء الوظيفة من قبل " + " " + unicode(user.name) + u"'"
            job_history_vals = {
                'action': 'إلغاء الوظيفة',
                'action_date': date.today(),
                'description':  description,
                'job_id':job.job_id.id
                }
            self.env['hr.job.history.actions'].create(job_history_vals)
        self.message_post(u"تمت إلغاء الوظائف من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def button_refuse(self):
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
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم رفض الطلب من قبل '" + unicode(user.name) + u"'")
        # send notification for the employee
        self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                              'message': u'لقد تم إشعار رفض طلب إلغاء الوظائف',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'res_id': self.id,
                                              'res_action': 'smart_hr.action_hr_job_cancel',
                                              'notif': True
                                              })


class HrJobCancelLine(models.Model):
    _name = 'hr.job.cancel.line'
    _description = u'الوظائف'
    _rec_name = 'job_id'

    job_cancel_line_id = fields.Many2one('hr.job.cancel', string='الوظيفة', required=1)
    job_id = fields.Many2one('hr.job', string='الوظيفة', required=1)
    job_number = fields.Char(related='job_id.number', string='رقم الوظيفة', readonly=1)
    job_name_code = fields.Char(related="job_id.name.number", string='الرمز', required=1)
    type_id = fields.Many2one('salary.grid.type', string='نوع السلم', required=1, readonly=1)
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
    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', required=1, readonly=1,
                                  domain=[('emp_state', 'not in', ['suspended', 'terminated']), ('employee_state', '=', 'employee')],
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid), ('emp_state', 'not in', ['suspended', 'terminated'])], limit=1))

    out_speech_number = fields.Char(string=u'رقم الخطاب الصادر')
    out_speech_date = fields.Date(string=u'تاريخ الخطاب الصادر')
    out_speech_file = fields.Binary(string=u'صورة الخطاب الصادر', attachment=True)
    in_speech_number = fields.Char(string=u'رقم الخطاب الوارد')
    in_speech_date = fields.Date(string=u'تاريخ الخطاب الوارد')
    in_speech_file = fields.Binary(string=u'صورة الخطاب الوارد', attachment=True)
    move_raison = fields.Text(string=u'مبررات طلب النقل')
    job_movement_ids = fields.One2many('hr.job.move.department.line', 'job_move_department_id')
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'صاحب الصلاحية'),
                              ('hrm1', u'شؤون الموظفين'),
                              ('budget', u'إدارة الميزانية'),
                              ('communication_external', u'إدارة الإتصالات - وزارة الخدمة المدنية'),
                              ('hrm2', u'شؤون الموظفين'),
                              ('done', u'اعتمدت'),
                              ('refused', u'رفض')
                              ], readonly=1, default='new')
    out_speech_file_name = fields.Char(string=u'مسمى صورة الخطاب الصادر')
    in_speech_file_name = fields.Char(string=u'مسمى صورة الخطاب الوارد')

    @api.multi
    def action_waiting(self):
        self.ensure_one()
        if not self.job_movement_ids:
            raise ValidationError(u"الرجاء ادخال وظيفة.")
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_autority_owner')):
            self.state = 'waiting'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm1'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg_dep')):
            self.state = 'budget'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__comm')):
            self.state = 'communication_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'
        else:
            raise ValidationError(u"الرجاء التحقق من إعدادات المخطط الإنسيابي.")

    @api.multi
    def action_hrm1(self):
        self.ensure_one()
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm1'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg_dep')):
            self.state = 'budget'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__comm')):
            self.state = 'communication_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'


    @api.multi
    def action_budget(self):
        self.ensure_one()
        self.action_job_reserve()
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_budg_dep')):
            self.state = 'budget'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__comm')):
            self.state = 'communication_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'


    @api.multi
    def action_communication(self):
        self.ensure_one()
        if self.check_workflow_state(self.env.ref('smart_hr.work_budget_civil_service')):
            self.state = 'communication_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'


    @api.multi
    def action_external(self):
        self.ensure_one()
        self.state = 'external'

    @api.multi
    def action_hrm2(self):
        self.ensure_one()
        self.state = 'hrm2'

    @api.multi
    def button_refuse(self):
        self.ensure_one()
        self.state = 'refused'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم رفض الطلب من قبل '" + unicode(user.name) + u"'")
        # send notification for the employee
        if self._context['refused_from_state'] == 'waiting':
            # send notification to the employee
            self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                                  'message': u'لقد تم إشعار رفض طلب نقل وظائف',
                                                  'user_id': self.employee_id.user_id.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_job_move_department',
                                                  'notif': True
                                                  })
        if self._context['refused_from_state'] == 'communication_external':
            group_id = self.env.ref('smart_hr.group_hr_personnel_officer_jobs')
            self.send_notification_to_group(group_id)
            # send notification to the صاحب الطلب
            if self.employee_id.user_id not in group_id.users:
                self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                                      'message': u'لقد تم إشعار رفض طلب نقل وظائف',
                                                      'user_id': self.employee_id.user_id.id,
                                                      'show_date': datetime.now().strftime(
                                                          DEFAULT_SERVER_DATETIME_FORMAT),
                                                      'res_id': self.id,
                                                      'res_action': 'smart_hr.action_hr_job_move_department',
                                                      'notif': True
                                                      })

    @api.multi
    def action_job_unreserve(self):
        self.ensure_one()
        for rec in self.job_movement_ids:
            rec.job_id.write({'state': 'unoccupied', 'department_id': rec.new_department_id.id, 'creation_source': 'move'})
            description = u" نقل الوظيفة الى " + " " + unicode(rec.new_department_id.name) + u"'"
            job_history_vals = {
                'action': 'نقل الوظيفة',
                'action_date': date.today(),
                'description': description,
                'job_id': rec.job_id.id}
            self.env['hr.job.history.actions'].create(job_history_vals)
        self.state = 'done'

    @api.multi
    def action_job_reserve(self):
        self.ensure_one()
        for rec in self.job_movement_ids:
            rec.job_id.write({'state': 'reserved'})

    def check_workflow_state(self, state):
        '''
        @param state: hr.job.workflow.state
        @return Boolean
        '''
        work_obj = self.env.ref('smart_hr.work_job_move_dep_workflow')
        if work_obj:
            return state in work_obj.state_ids
        else:
            return False

    def send_notification_to_group(self, group_id):
        '''
        @param group_id: res.groups
        '''
        for recipient in group_id.users:
            self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                                  'message': u'لقد تم إشعار رفض طلب نقل وظائف',
                                                  'user_id': recipient.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_job_move_department',
                                                  'notif': True
                                                  })


class HrJobMoveDeparrtmentLine(models.Model):
    _name = 'hr.job.move.department.line'
    _description = u'نقل وظائف'
    _rec_name = 'job_id'

    job_id = fields.Many2one('hr.job', string='الوظيفة', required=1)
    job_number = fields.Char(related='job_id.number', string='رقم الوظيفة', readonly=1)
    job_name_code = fields.Char(related="job_id.name.number", string='الرمز', readonly=1)
    type_id = fields.Many2one('salary.grid.type', string='نوع السلم', readonly=1, required=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة ', readonly=1, required=1)
    department_id = fields.Many2one('hr.department', string='الإدارة', readonly=1, required=1)
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
            domain = {}
            self.type_id = self.job_id.type_id.id
            self.grade_id = self.job_id.grade_id.id
            self.department_id = self.job_id.department_id.id
            domain['new_department_id'] = [('id', '!=', self.department_id.id)]
            res['domain'] = domain
            return res
        return res


class HrJobMoveGrade(models.Model):
    _name = 'hr.job.move.grade'
    _inherit = ['mail.thread']
    _description = u'رفع أو خفض وظائف'
    _rec_name = 'decision_number'

    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', required=1, readonly=1,
                                  domain=[('emp_state', 'not in', ['suspended', 'terminated']), ('employee_state', '=', 'employee')],
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid), ('emp_state', 'not in', ['suspended', 'terminated'])], limit=1))

    decision_number = fields.Char(string=u'رقم القرار')
    decision_date = fields.Date(string=u'تاريخ القرار')
    decision_file = fields.Binary(string=u'نسخة القرار',attachment=True)
    move_date = fields.Date(string=u'التاريخ', readonly=1, default=fields.Datetime.now(), required=1)
    fiscal_year = fields.Char(string=u'السنه المالية', default=(date.today().year), readonly=1)
    out_speech_number = fields.Char(string=u'رقم الخطاب الصادر')
    out_speech_date = fields.Date(string=u'تاريخ الخطاب الصادر')
    out_speech_file = fields.Binary(string=u'صورة الخطاب الصادر', attachment=True)
    in_speech_number = fields.Char(string=u'رقم الخطاب الوارد')
    in_speech_date = fields.Date(string=u'تاريخ الخطاب الوارد')
    in_speech_file = fields.Binary(string=u'صورة الخطاب الوارد', attachment=True)
    job_movement_ids = fields.One2many('hr.job.move.grade.line', 'job_move_grade_id', required=1)
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'صاحب الصلاحية'),
                              ('hrm1', u'شؤون الموظفين'),
                              ('budget_external', u'إدارة الميزانية - وزارة المالية'),
                              ('hrm2', u'شؤون الموظفين'),
                              ('done', u'اعتمدت'),
                              ('refused', u'رفض'),
                              ], readonly=1, default='new')
    move_type = fields.Selection([('scale_up', u'رفع'),
                                  ('scale_down', u'خفض')
                                  ])
    out_speech_file_name = fields.Char(string=u'مسمى صورة الخطاب الصادر')
    in_speech_file_name = fields.Char(string=u'مسمى صورة الخطاب الوارد')

    @api.multi
    def action_waiting(self):
        self.ensure_one()
        if not self.job_movement_ids:
            raise ValidationError(u"الرجاء ادخال وظيفة.")
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_autority_owner')):
            self.state = 'waiting'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm1'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__minis')):
            self.state = 'budget_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__comm')):
            self.state = 'communication_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'
        else:
            raise ValidationError(u"الرجاء التحقق من إعدادات المخطط الإنسيابي.")

    @api.multi
    def action_hrm1(self):
        self.ensure_one()
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm1'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__minis')):
            self.state = 'budget_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__comm')):
            self.state = 'communication_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'
        else:
            self.action_done()

    @api.multi
    def action_budget(self):
        self.ensure_one()
        self.action_job_reserve()
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__minis')):
            self.state = 'budget_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__comm')):
            self.state = 'communication_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'
        else:
            self.action_done()

    @api.multi
    def action_hrm2(self):
        self.ensure_one()
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'
        else:
            self.action_done()

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.state = 'done'
        for job in self.job_movement_ids:
            if self.move_type == "scale_up":
                move_type = "رفع"
            else:
                move_type = "خفض"
            description = move_type + u" الوظيفة من المرتبة " + unicode(job.grade_id.name) +u" الى المرتبة " +unicode(job.new_grade_id.name) + '.\n'
            if job.new_job_name:
                description += " تغيير المسمى من " + unicode(job.job_id.name.name) + u"  الى " + unicode(job.new_job_name.name)+ ".\n"
            if job.new_job_number:
                description += " تغيير رقم الوظيفة من " +unicode(job.job_id.number) +u" الى " + unicode(job.new_job_number)+ ".\n"
            if job.new_department_id:
                description += "  تغيير الادارة من " +unicode(job.job_id.department_id.name) + u" الى " +unicode(job.new_department_id.name)+ ".\n"
            job_history_vals = {
                'action': move_type,
                'action_date': date.today(),
                'description': description,
                'job_id': job.job_id.id}
            self.env['hr.job.history.actions'].create(job_history_vals)
            job.job_id.state = 'cancel'
            new_job_description = u"إحداث ب"+move_type + u" الوظيفة من المرتبة " + unicode(job.grade_id.name) +u" الى المرتبة " +unicode(job.new_grade_id.name) + '.\n'
            new_job_vals = {
            'grade_id' : job.new_grade_id.id,
            'department_id' : job.new_department_id.id,
            'name': job.new_job_name.id,
            'number' : job.new_job_number,
            'creation_source' : self.move_type,
            'state' : 'unoccupied',
            'serie_id': job.job_id.serie_id.id,
            'general_id': job.job_id.general_id.id,
            'specific_id': job.job_id.specific_id.id,
            'activity_type': job.job_id.activity_type.id,
            'creation_source': self.move_type,
            'type_id' : job.job_id.type_id.id,
            }
            new_job = self.env['hr.job'].create(new_job_vals)
            new_job_history_vals = {
                'action': move_type,
                'action_date': date.today(),
                'description': new_job_description,
                'job_id': new_job.id}
            self.env['hr.job.history.actions'].create(new_job_history_vals)
            
    @api.multi
    def button_refuse(self):
        self.ensure_one()
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم رفض الطلب من قبل '" + unicode(user.name) + u"'")

        if self.state == 'waiting':
            # send notification to the employee
            if self.move_type == 'scale_up':
                action_name = 'smart_hr.action_hr_job_scal_up_grade'
            else:
                action_name = 'smart_hr.action_hr_job_scal_down_grade'
            self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                                  'message': u'لقد تم إشعار رفض طلب رفع أو خفض وظائف',
                                                  'user_id': self.employee_id.user_id.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': action_name,
                                                  'notif': True
                                                  })
        if self.state == 'budget_external':
            group_id = self.env.ref('smart_hr.group_hr_personnel_officer_jobs')
            self.send_notification_to_group(group_id)
            # send notification to the صاحب الطلب
            if self.move_type == 'scale_up':
                action_name = 'smart_hr.action_hr_job_scal_up_grade'
            else:
                action_name = 'smart_hr.action_hr_job_scal_down_grade'
            if self.employee_id.user_id not in group_id.users:
                self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                                      'message': u'لقد تم إشعار رفض طلب رفع أو خفض وظائف',
                                                      'user_id': self.employee_id.user_id.id,
                                                      'show_date': datetime.now().strftime(
                                                          DEFAULT_SERVER_DATETIME_FORMAT),
                                                      'res_id': self.id,
                                                      'res_action': action_name,
                                                      'notif': True
                                                      })
        self.state = 'refused'

    @api.multi
    def action_job_unreserve(self):
        self.ensure_one()
        for rec in self.job_movement_ids:
            rec.job_id.write({'state': 'unoccupied', 'number': rec.job_number, 'grade_id': rec.new_grade_id.id})
        self.action_done()

    @api.one
    def action_job_reserve(self):
        for rec in self.job_movement_ids:
            rec.job_id.state = 'reserved'

    def send_notification_to_group(self, group_id):
        '''
        @param group_id: res.groups
        '''
        # send notification to group hrm
        if self.move_type == 'scale_up':
            action_name = 'smart_hr.action_hr_job_scal_up_grade'
        else:
            action_name = 'smart_hr.action_hr_job_scal_down_grade'
        for recipient in group_id.users:
            self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                                  'message': u'لقد تم إشعار رفض طلب رفع أو خفض وظائف',
                                                  'user_id': recipient.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': action_name,
                                                  'notif': True
                                                  })

    def check_workflow_state(self, state):
        '''
        @param state: hr.job.workflow.state
        @return Boolean
        '''
        work_obj = self.env.ref('smart_hr.work_job_move_grade_workflow')
        if work_obj:
            return state in work_obj.state_ids
        else:
            return False


class HrJobMoveGradeLine(models.Model):
    _name = 'hr.job.move.grade.line'
    _description = u'رفع أو خفض وظائف'
    _rec_name = 'job_id'

    job_move_grade_id = fields.Many2one('hr.job.move.grade', string='الوظيفة', required=1, ondelete="cascade")
    job_id = fields.Many2one('hr.job', string='الوظيفة', required=1)
    job_number = fields.Char(string='رقم الوظيفة', required=1)
    job_name_code = fields.Char(related="job_id.name.number", string='الرمز', readonly=1)
    type_id = fields.Many2one('salary.grid.type', string='نوع السلم', readonly=1, required=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة الحالية', readonly=1, required=1)
    new_grade_id = fields.Many2one('salary.grid.grade', string=' المرتبة الجديدة', required=1)
    department_id = fields.Many2one('hr.department', string='الإدارة', readonly=1, required=1)
    new_job_number = fields.Char(string='رقم الوظيفة الجديد', required=1)
    new_department_id = fields.Many2one('hr.department', string=' الإدارة الجديدة', required=1)
    new_job_name = fields.Many2one('hr.job.name', string='المسمى الجديد', required=1)

    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id:
            self.type_id = self.job_id.type_id.id
            self.grade_id = self.job_id.grade_id.id
            self.department_id = self.job_id.department_id.id
            self.job_number = self.job_id.number
            res = {}
            grade_ids = []
            grides = []
            # get grades
            grade_ids_scale_up = self.env['salary.grid.grade'].search([(int('code'), '>=', int(self.job_id.grade_id.code))])
            grade_ids_scale_down = self.env['salary.grid.grade'].search([(int('code'), '<=', int(self.job_id.grade_id.code))])
            if self._context['operation'] == 'scale_down':
                res['domain'] = {'new_grade_id': [('id', 'in', grade_ids_scale_down.ids)]}
            if self._context['operation'] == 'scale_up':
                res['domain'] = {'new_grade_id': [('id', 'in', grade_ids_scale_up.ids)]}
            return res

        if not self.job_id:
            res = {}
            domain = [('state', '=', 'unoccupied')]
            job_ids = []
            for rec in self.env['hr.job'].search(domain):
                if self._context['operation'] == 'scale_down' and int(rec.grade_id.code) > 1:
                    job_ids.append(rec.id)
                if self._context['operation'] == 'scale_up' and int(rec.grade_id.code) < 99:
                    job_ids.append(rec.id)
            res['domain'] = {'job_id': [('id', 'in', job_ids)]}
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

    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', required=1, readonly=1,
                                  domain=[('emp_state', 'not in', ['suspended', 'terminated']), ('employee_state', '=', 'employee')],
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid), ('emp_state', 'not in', ['suspended', 'terminated'])], limit=1))

    decision_number = fields.Char(string=u"رقم القرار")
    decision_date = fields.Date(string=u'تاريخ القرار')
    out_speech_number = fields.Char(string=u'رقم الخطاب الصادر')
    out_speech_date = fields.Date(string=u'تاريخ الخطاب الصادر')
    out_speech_file = fields.Binary(string=u'صورة الخطاب الصادر', attachment=True)
    in_speech_number = fields.Char(string=u'رقم الخطاب الوارد')
    in_speech_date = fields.Date(string=u'تاريخ الخطاب الوارد')
    in_speech_file = fields.Binary(string=u'صورة الخطاب الوارد', attachment=True)
    job_update_ids = fields.One2many('hr.job.update.line', 'job_update_id', required=1)
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'صاحب الصلاحية'),
                              ('hrm1', u'شؤون الموظفين'),
                              ('budget_external', u'إدارة الميزانية - وزارة الخدمة المدنية'),
                              ('hrm2', u'شؤون الموظفين'),
                              ('done', u'اعتمدت'),
                              ('refused', u'رفض')
                              ], readonly=1, default='new')
    out_speech_file_name = fields.Char(string=u'مسمى صورة الخطاب الصادر')
    in_speech_file_name = fields.Char(string=u'مسمى صورة الخطاب الوارد')

    @api.multi
    def action_waiting(self):
        if not self.job_update_ids:
            raise ValidationError(u"الرجاء ادخال وظيفة.")
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_autority_owner')):
            self.state = 'waiting'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm1'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__minis')):
            self.state = 'budget_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'
        else:
            raise ValidationError(u"الرجاء التحقق من إعدادات المخطط الإنسيابي.")

    @api.multi
    def action_hrm1(self):
        self.ensure_one()
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm1'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_budg__minis')):
            self.state = 'budget_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'
        else:
            self.action_done()

    @api.multi
    def action_budget(self):
        self.ensure_one()
        self.action_job_reserve()
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_budg_dep_minis')):
            self.state = 'budget_external'
        elif self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'
        else:
            self.action_done()

    @api.multi
    def action_hrm2(self):
        self.ensure_one()
        if self.check_workflow_state(self.env.ref('smart_hr.work_job_personnel_affairs')):
            self.state = 'hrm2'
        else:
            self.action_done()

    @api.multi
    def button_refuse(self):
        self.ensure_one()
        self.state = 'refused'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم رفض الطلب من قبل '" + unicode(user.name) + u"'")
        if self.state == 'waiting':
            # send notification to the employee
            self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                                  'message': u'لقد تم إشعار رفض طلب تحوير‬ وظائف',
                                                  'user_id': self.employee_id.user_id.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_job_update',
                                                  'notif': True
                                                  })
        if self.state == 'budget_external':
            group_id = self.env.ref('smart_hr.group_hr_personnel_officer_jobs')
            # send notification to group hrm
            self.send_notification_to_group(group_id)
            # send notification to the صاحب الطلب
            if self.employee_id.user_id not in group_id.users:
                self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                                      'message': u'لقد تم إشعار رفض طلب تحوير‬ وظائف',
                                                      'user_id': self.employee_id.user_id.id,
                                                      'show_date': datetime.now().strftime(
                                                          DEFAULT_SERVER_DATETIME_FORMAT),
                                                      'res_id': self.id,
                                                      'res_action': 'smart_hr.action_hr_job_update',
                                                      'notif': True
                                                      })
        self.state = 'refused'

    @api.multi
    def action_job_unreserve(self):
        self.ensure_one()
        for rec in self.job_update_ids:
            rec.job_id.write({'state': 'unoccupied'})
            rec.job_id.name = rec.new_name
            rec.job_id.date_update = datetime.now()
            rec.job_id.type_id = rec.new_type_id
            rec.job_id.creation_source = 'update'
            description = ""
            if rec.new_name:
                description += " تحوير المسمى من " + " " + str(rec.old_name.name) + " " + " الى "+ " " + str(rec.new_name.name)+". \n"
            if rec.new_type_id:
                description += " تحوير نوع السلم من " + " " + str(rec.old_type_id.name) + " " + "الى"+ " " + str(rec.new_type_id.name)+"."
            job_history_vals = {
                'action': 'تحوير‬ الوظيفة',
                'action_date': date.today(),
                'description': description,
                'job_id':rec.job_id.id
                }
            self.env['hr.job.history.actions'].create(job_history_vals)
        self.state = 'done'
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم تحوير‬ الوظائف من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def action_job_reserve(self):
        self.ensure_one()
        for rec in self.job_update_ids:
            rec.job_id.write({'is_occupied': True})

    def check_workflow_state(self, state):
        '''
        @param state: hr.job.workflow.state
        @return Boolean
        '''
        work_obj = self.env.ref('smart_hr.work_job_update_workflow')
        if work_obj:
            return state in work_obj.state_ids
        else:
            return False

    def send_notification_to_group(self, group_id):
        '''
        @param group_id: res.groups
        '''
        for recipient in group_id.users:
            self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                                  'message': u'لقد تم إشعار رفض طلب تحوير‬ وظائف',
                                                  'user_id': recipient.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_job_update',
                                                  'notif': True
                                                  })


class HrJobMoveUpdateLine(models.Model):
    _name = 'hr.job.update.line'
    _description = u'تحوير‬ وظيفة'
    _rec_name = 'job_id'

    job_update_id = fields.Many2one('hr.job.update', string=u'التحوير‬')
    job_id = fields.Many2one('hr.job', string=u'الوظيفة', required=1)
    job_name_code = fields.Char(related="job_id.number", string='الرمز', required=1)
    job_number = fields.Char(related='job_id.number', string=u'رقم الوظيفة', readonly=1)
    old_name = fields.Many2one('hr.job.name', readonly=1, string=u'المسمى', required=1)
    new_name = fields.Many2one('hr.job.name', string=u'المسمى الجديد', required=1)
    old_type_id = fields.Many2one('salary.grid.type', string=u'نوع السلم', readonly=1, required=1)
    new_type_id = fields.Many2one('salary.grid.type', string=u'نوع السلم الجديد', required=1)
    grade_id = fields.Many2one('salary.grid.grade', related='job_id.grade_id', string=u'المرتبة', readonly=1,
                               required=1)
    department_id = fields.Many2one('hr.department', related='job_id.department_id', string=u'الإدارة', readonly=1,
                                    required=1)

    @api.onchange('job_id')
    def onchange_job_id(self):
        if not self.job_id:
            res = {}
            # get jobs that are  updated or created from more than one year
            today = date.today()
            d = today - relativedelta(years=1)
            dt = datetime.today() - relativedelta(years=1)
            all_job_ids = self.env['hr.job'].search(['|', ('update_date', '>=', d), ('create_date', '>=', str(dt))])
            res['domain'] = {'job_id': [('id', 'in', all_job_ids.ids)]}
            return res
        if self.job_id:
            domain = {}
            res = {}
            # fill old value
            self.old_name = self.job_id.name.id
            self.old_type_id = self.job_id.type_id.id
            domain['new_name'] = [('id', '!=', self.job_id.name.id)]
            domain['new_type_id'] = [('id', '!=', self.job_id.type_id.id)]
            res['domain'] = domain
            return res


class HrJobTypeActivity(models.Model):
    _name = 'hr.job.type.activity'
    _description = u'نوع نشاط الوظيفة'

    name = fields.Char(string=u'المسمى')
    code = fields.Char(string=u'الرمز')
