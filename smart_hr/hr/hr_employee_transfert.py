# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrEmployeeTransfert(models.Model):
    _name = 'hr.employee.transfert'
    _inherit = ['mail.thread']
    _description = u'طلب نقل موظف'
    _rec_name = 'employee_id'

    @api.multi
    def _get_default_employee_job(self):
        return self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1).job_id

    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now(), readonly=1)
    sequence = fields.Integer(string=u'رتبة الطلب')
    employee_id = fields.Many2one('hr.employee', string=u'صاحب الطلب', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), required=1)
    last_evaluation_result = fields.Many2one('hr.employee.evaluation.level', string=u'أخر تقييم إداء')
    job_id = fields.Many2one('hr.job', default=_get_default_employee_job, string=u'الوظيفة', readonly=1, required=1)
    specific_id = fields.Many2one('hr.groupe.job', related='job_id.specific_id', string=u'المجموعة النوعية', readonly=1, required=1)
    occupied_date = fields.Date(related='job_id.occupied_date', string=u'تاريخ شغلها')
    type_id = fields.Many2one('salary.grid.type', related='employee_id.type_id', string=u'الصنف', readonly=1, required=1)
    new_job_id = fields.Many2one('hr.job', domain=[('state', '=', 'unoccupied')], string=u'الوظيفة المنقول إليها')
    new_specific_id = fields.Many2one('hr.groupe.job', related='new_job_id.specific_id', readonly=1, string=u'المجموعة النوعية')
    new_type_id = fields.Many2one('salary.grid.type', related='new_job_id.type_id', readonly=1, string=u'الصنف')
    justification_text = fields.Text(string=u'مبررات النقل', readonly=1, states={'new': [('readonly', 0)]})
    note = fields.Text(string=u'ملاحظات')
    attachments = fields.Many2many('ir.attachment',string=u"المرفقات")
    same_group = fields.Boolean(compute='_compute_same_specific_group', default=False)
    ready_tobe_done = fields.Boolean(default=False)
    decision_number = fields.Char(string=u"رقم القرار")
    decision_date = fields.Date(string=u'تاريخ القرار')
    decision_file = fields.Binary(string=u'نسخة القرار', attachment=True)
    decision_file_name = fields.Char(string=u'نسخة القرار')
    degree_id = fields.Many2one('salary.grid.degree', string=u'الدرجة')
    date_direct_action = fields.Date(string=u'تاريخ مباشرة العمل')
    governmental_entity = fields.Many2one('res.partner', string=u'الجهة الحكومية', domain=[('company_type', '=', 'governmental_entity')])
    desire_ids = fields.One2many('hr.employee.desire', 'employee_id', required=1, string=u'رغبات النقل', readonly=1, states={'new': [('readonly', 0)]})
    refusing_date = fields.Date(string=u'تاريخ الرفض', readonly=1)
    # ‫المدنتية ‫الخدمة‬ ‫موافلقة‬
    speech_number = fields.Char(string=u'رقم الخطاب')
    speech_date = fields.Date(string=u'تاريخ الخطاب')
    speech_file = fields.Binary(string=u'نسخة الخطاب', attachment=True)
    speech_file_name = fields.Char(string=u'نسخة الخطاب')
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'صاحب الصلاحية'),
                               ('consult', u'صاحب الطلب'),
                              ('pm', u'شؤون الموظفين'),
                              ('done', u'اعتمدت'),
                              ('refused', u'رفض'),
                              ('cancelled', u'ملغى'),
                              ], readonly=1, default='new', string=u'الحالة')
    transfert_nature = fields.Selection([('internal_transfert', u'نقل داخلي'),
                                         ('external_transfert_out', u'نقل خارجي (من الهيئة إلى جهة أخرى)'),
                                         ('external_transfert_in', u'نقل خارجي (إلى الهيئة)'),
                                         ], readonly=1, states={'new': [('readonly', 0)]}, default='internal_transfert', required=1, string=u'طبيعة النقل')

    transfert_type = fields.Selection([('employee', u'نقل موظفين'),
                                       ('member', u'نقل أعضاء'),
                                       ], readonly=1, states={'new': [('readonly', 0)]}, default='employee', required=1, string=u'نوع النقل')
    special_conditions = fields.Boolean(string=u'ضروف خاصة', default=False)
    special_justification_text = fields.Text(string=u'مبررات الظروف الخاصة', readonly=1, states={'new': [('readonly', 0)]})

    transfert_periode_id = fields.Many2one('hr.employee.transfert.periode', string=u'فترة النقل', required=1, readonly=1, states={'new': [('readonly', 0)]})
    is_ended = fields.Boolean(string=u'انتهت', compute='_compute_is_ended')
    for_members = fields.Boolean(string=u'للاعضاء')
    tobe_cancelled = fields.Boolean(string=u'سيلغى', default=False)
    is_current_user = fields.Boolean(string='Is Current User', compute='_is_current_user', default=False)
    salary_proportion = fields.Float(string=u'نسبة الراتب التي توفرها الجهة (%)', default=100)
    # fields for ordering
    begin_work_date = fields.Date(string=u'تاريخ بداية العمل الحكومي', readonly=1)
    recruiter_date = fields.Date(string=u'تاريخ التعين بالجهة', readonly=1)
    age = fields.Integer(string=u'السن', readonly=1)


    @api.onchange('transfert_nature')
    def onchange_transfert_nature(self):
        res = {}
        if self.transfert_nature == 'external_transfert_in':
            employee_search_ids = self.env['hr.employee'].search([('employee_state','=','new')])
            print"job_search_ids",employee_search_ids
            employee_ids = [rec.id for rec in employee_search_ids]
            res['domain'] = {'employee_id': [('id', 'in', employee_ids)]}
            return res

    @api.multi
    @api.depends('employee_id')
    def _is_current_user(self):
        for rec in self:
            if rec.employee_id.user_id.id == rec._uid:
                rec.is_current_user = True

    @api.multi
    def _compute_is_ended(self):
        for rec in self:
            # compute is_ended periode
            if rec.transfert_periode_id.date_to < datetime.today().strftime('%Y-%m-%d'):
                rec.is_ended = True
            else:
                rec.is_ended = False

    @api.multi
    @api.depends('new_specific_id', 'specific_id')
    def _compute_same_specific_group(self):
        for rec in self:
            if rec.specific_id and rec.new_specific_id:
                rec.same_group = rec.specific_id == rec.new_specific_id
            else:
                rec.same_group = False

    @api.onchange('transfert_periode_id', 'transfert_type')
    def _onchange_transfert_periode_id(self):
        if not self.transfert_periode_id:
            # do not allow creating tranfert if there is no open periode
            res = {}
            open_periodes = self.env['hr.employee.transfert.periode'].search([('date_to', '>=', datetime.today().strftime('%Y-%m-%d'))])
            if open_periodes:
                open_periodes_ids = [rec.id for rec in open_periodes]
                res['domain'] = {'transfert_periode_id': [('id', 'in', open_periodes_ids), ('for_member', '=', (self.transfert_type == 'member'))]}
                return res
            else:
                res['domain'] = {'transfert_periode_id': [('id', '=', -1)]}
                return res

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        # get last evaluation result
        if self.employee_id:
            previews_year = int(date.today().year) - 1
            last_evaluation_result = self.employee_id.evaluation_level_ids.search([('year', '=', int(previews_year))])
            if last_evaluation_result:
                self.last_evaluation_result = last_evaluation_result
            self.begin_work_date = self.employee_id.begin_work_date
            self.recruiter_date = self.employee_id.recruiter_date
            self.age = self.employee_id.age

    @api.onchange('desire_ids')
    def _onchange_desire_ids(self):
        # check desire_ids length from config
        hr_config = self.env['hr.setting'].search([], limit=1)
        if hr_config:
            if len(self.desire_ids) > hr_config.desire_number:
                raise ValidationError(u"لا يمكن إضافة أكثر من " + str(hr_config.desire_number) + u" رغبات.")

    @api.multi
    @api.constrains('transfert_nature', 'desire_ids')
    def check_constrains(self):
        self.ensure_one()
        hr_config = self.env['hr.setting'].search([], limit=1)
        # 1- constrainte for normal employees without special conditions
        if self.transfert_type == 'employee' and self.special_conditions is False:
            # check if there is a refused transfert demand before 45days
            transferts = self.env['hr.employee.transfert'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'refused')])
            for transfert in transferts:
                today = date.today()
                refusing_date = fields.Date.from_string(transfert.refusing_date)
                if refusing_date:
                    days = (today - refusing_date).days
                    if hr_config:
                        if days < hr_config.needed_days:
                            raise ValidationError(u"لا يمكن تقديم طلب إلى بعد " + str(hr_config.needed_days) + u" يوماً.")
            # ‫التجربة‬ ‫سنة‬ ‫إستلكمال‬
            recruitement_decision = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id), ('is_started', '=', True), ('state_appoint', '=', 'active')], limit=1)
            if recruitement_decision and recruitement_decision.depend_on_test_periode:
                testing_date_to = recruitement_decision.testing_date_to
                if testing_date_to:
                    if fields.Date.from_string(testing_date_to) >= fields.Date.from_string(fields.Datetime.now()):
                        raise ValidationError(u"لايمكن طلب نقل خلال فترة التجربة")
            # ‫التترقية‬ ‫سنة‬ ‫إستلكمال‬
            if self.employee_id.promotion_duration < 1:
                    raise ValidationError(u"لايمكن طلب نقل خلال أقل من سنة منذ أخر ترقية")
#             # check desire_ids length from config
            if hr_config:
                if len(self.desire_ids) > hr_config.desire_number:
                    raise ValidationError(u"لا يمكن إضافة أكثر من " + str(hr_config.desire_number) + u" رغبات.")

        # 2- constraintes for members without special conditions
        if self.transfert_type == 'member' and self.special_conditions is False:
            # ‫التترقية‬ ‫سنة‬ ‫إستلكمال‬
            if self.employee_id.promotion_duration < 1:
                            raise ValidationError(u"لايمكن طلب نقل خلال أقل من سنة منذ أخر ترقية أو تعين")
            # check 3 years constrainte from last transfert
            last_transfert_id = self.env['hr.employee.transfert'].search([('id', '!=', self.id)], order="create_date desc", limit=1)
            today = date.today()
            create_date = fields.Date.from_string(last_transfert_id.create_date)
            if create_date:
                years = relativedelta(today - create_date).years
                if hr_config:
                    if years < hr_config.years_last_transfert:
                        raise ValidationError(u"لم تتم " + str(hr_config.years_last_transfert) + u" سنوات من أخر نقل.")
            # chek if there is any sanction for the emmployee
            if len(self.employee_id.sanction_ids) > 0:
                raise ValidationError(u"لدى الموظف عقوبات.")

    @api.multi
    def action_waiting(self):
        self.ensure_one()
        self.state = 'waiting'

    @api.multi
    def action_consultation(self):
        self.ensure_one()
        self.state = 'pm'

  

    @api.multi
    def action_cancelled(self):
        self.ensure_one()
        self.state = 'cancelled'

    @api.multi
    def action_tobe_cancelled_confirm(self):
        self.ensure_one()
        self.tobe_cancelled = True

    @api.multi
    def action_notif(self):
        self.ensure_one()
        # send notification for the employee
        self.env['base.notification'].create({'title': u'إشعار بعدم وجود وظيفة مناسبة',
                                              'message': u'لا يوجد وظيفة مناسبة لطلبك حالياً.',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'res_id': self.id,
                                              'res_action': 'smart_hr.action_hr_employee_transfert',
                                              'notif': True
                                              })

    @api.multi
    def action_pm(self):
        self.ensure_one()
        if self.transfert_type == 'external_transfert_out':
                if self.check_judicial_precedent(self.employee_id):
                    self.note = u'الموظف لديه سوابق عدلية'
                    self.action_refused()
                    return

        self.state = 'consult'

    @api.multi
    def button_refuse(self):
        self.ensure_one()
        self.refusing_date = datetime.now()
        self.state = 'refused'
        # send notification for the employee
        msg = u', '
        if self.note:
            msg += self.note
        self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                              'message': u'لقد تم رفض طلب نقل ' + str(msg),
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'res_id': self.id,
                                              'res_action': 'smart_hr.action_hr_employee_transfert',
                                              'notif': True
                                              })

    @api.multi
    def action_done(self):
        for rec in self:
            if not rec.new_job_id:
                        raise ValidationError(u"الرجاء التثبت من حقل الوظيفة المنقول إليها.")
            if not rec.degree_id:
                        raise ValidationError(u"الرجاء التثبت من حقل الدرجة.")
            # create hr.decision.appoint object
            # with decision file
            if rec.new_specific_id == rec.specific_id:
                if not rec.decision_number:
                    raise ValidationError(u"لم يتم إصدار قرار بشأن النقل.")
                vals = {
                    'type_appointment': self.env.ref('smart_hr.data_hr_recrute_from_transfert').id,
                    'date_direct_action': rec.date_direct_action,
                    'employee_id': rec.employee_id.id,
                    'job_id': rec.new_job_id.id,
                    'degree_id': rec.degree_id.id,
                    'name': rec.decision_number,
                    'order_date': rec.decision_date,
                    'order_picture': rec.decision_file
                }
            else:
                if not rec.speech_number:
                    raise ValidationError(u"لم يتم خطاب قرار بشأن النقل.")
                # with speech file
                vals = {
                    'type_appointment': self.env.ref('smart_hr.data_hr_recrute_from_transfert').id,
                    'date_direct_action': rec.date_direct_action,
                    'employee_id': rec.employee_id.id,
                    'job_id': rec.new_job_id.id,
                    'degree_id': rec.degree_id.id,
                    'name': rec.speech_number,
                    'order_date': rec.speech_date,
                    'order_picture': rec.speech_file
                }
            recruiter_id = self.env['hr.decision.appoint'].create(vals)
            recruiter_id._onchange_employee_id()
            recruiter_id._onchange_job_id()
            recruiter_id._onchange_degree_id()
            recruiter_id.action_done()
            rec.state = 'done'
            # create history_line
#             self.env['hr.employee.history'].sudo().add_action_line(self.employee_id, False, False, "نقل")
            if rec.transfert_type == 'internal_transfert':
                # send notification for the employee
                self.env['base.notification'].create({'title': u'إشعار بموافقة طلب',
                                                      'message': u'لقد تمت الموافقة على طلب النقل',
                                                      'user_id': rec.employee_id.user_id.id,
                                                      'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                      'res_id': rec.id,
                                                      'res_action': 'smart_hr.action_hr_employee_transfert',
                                                      'notif': True
                                                      })
            if rec.transfert_nature == 'external_transfert_out':
                # send notification for the employee
                self.env['base.notification'].create({'title': u'إشعار بموافقة طلب',
                                                      'message': u'لقد تمت الموافقة على طلب النقل - الرجاء جلب طلب النقل من الجهة.',
                                                      'user_id': rec.employee_id.user_id.id,
                                                      'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                      'res_id': rec.id,
                                                      'res_action': 'smart_hr.action_hr_employee_transfert',
                                                      'notif': True
                                                      })

    def check_judicial_precedent(self, employee_id):
        emp_jud_prec_ids = self.env['employee.judicial.precedent.order'].search([('employee', '=', employee_id.id)])
        if emp_jud_prec_ids:
            return True
        else:
            return False


class HrEmployeeTransfertPeriode(models.Model):
    _name = 'hr.employee.transfert.periode'
    _description = u'فترات النقل'
    _rec_name = "name"

    name = fields.Char(string=u'المسمى', required=1)
    date_from = fields.Date(string=u'التاريخ من ', default=fields.Datetime.now())
    date_to = fields.Date(string=u'التاريخ الى')
    for_member = fields.Boolean(string=u'للأعضاء', default=False)
    is_ended_compute = fields.Boolean(string=u'انتهت', compute='_compute_is_ended')
    is_ended = fields.Boolean(string=u'انتهت')
    for_members = fields.Boolean(string=u'للاعضاء')

    @api.multi
    @api.depends('date_from')
    def _compute_is_ended(self):
        for rec in self:
            if rec.date_to < datetime.today().strftime('%Y-%m-%d'):
                rec.is_ended = True
            else:
                rec.is_ended = False


class HrTransfertSorting(models.Model):
    _name = 'hr.transfert.sorting'
    _inherit = ['mail.thread']
    _description = u'‫ترتيب طلبات النقل مع الوظائف المناسبة‬‬'

    name = fields.Char(string=u'المسمى', required=1, readonly=1, states={'new': [('readonly', 0)]})
    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now(), readonly=1)
    line_ids = fields.One2many('hr.transfert.sorting.line', 'hr_transfert_sorting_id', string=u'طلبات النقل', readonly=0, states={'done': [('readonly', 1)]})
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'إعتماد الموظفين'),
                              ('commission_president', u'رئيس الجهة'),
                              ('done', u'اعتمدت'),
                              ('refused', u'مرفوضة')
                              ], readonly=1, default='new', string=u'الحالة')

    @api.multi
    def action_generate_lines(self):
        self.ensure_one()
        self.line_ids.unlink()
        line_ids = []
        transfert_ids = self.env['hr.employee.transfert'].search([('state', '=', 'pm'), ('ready_tobe_done', '=', False)], order=("begin_work_date, create_date, recruiter_date, age desc"))
        if not transfert_ids:
            raise ValidationError(u"لايوجد طلبات حالياً.")
        sequence = 1
        for transfert_id in transfert_ids:
            transfert_id.sequence = sequence
            vals = {'hr_transfert_sorting_id': self.id,
                    'hr_employee_transfert_id': transfert_id.id,
                    }
            line_ids.append(vals)
            sequence += 1
        self.line_ids = line_ids


    @api.multi
    def action_waiting(self):
        self.ensure_one()
        self.state = 'commission_president'

    @api.multi
    def button_refuse(self):
        self.ensure_one()
        self.state = 'refused'

    @api.multi
    def action_commission_president(self):
        self.ensure_one()
        self.state = 'commission_president'

    @api.multi
    def action_done(self):
        self.ensure_one()
        for rec in self.line_ids:
            if rec.is_conflected:
                raise ValidationError(u"الرجاء حل الخلاف في الوظائف المختارة.")
        for rec in self.line_ids:
            rec.hr_employee_transfert_id.write({'new_job_id': rec.new_job_id.id, 'ready_tobe_done': True})
        self.state = 'done'


class HrTransfertSortingLine(models.Model):
    _name = 'hr.transfert.sorting.line'
    _description = u'‫طلبات النقل‬‬'

    hr_transfert_sorting_id = fields.Many2one('hr.transfert.sorting', string=u'إجراء الترتيب')
    hr_employee_transfert_id = fields.Many2one('hr.employee.transfert', string=u'طلب نقل موظف')
    state = fields.Selection(related='hr_employee_transfert_id.state' ,string=u'الحالة')
    sequence = fields.Integer(string=u'رتبة الطلب', related='hr_employee_transfert_id.sequence', readonly=1)
    recruiter_date = fields.Date(string=u'تاريخ التعين بالجهة', related='hr_employee_transfert_id.employee_id.recruiter_date', readonly=1)
    age = fields.Integer(string=u'السن', related='hr_employee_transfert_id.employee_id.age', readonly=1)
    job_id = fields.Many2one('hr.job', related='hr_employee_transfert_id.job_id', string=u'الوظيفة', readonly=1)
    begin_work_date = fields.Date(related='hr_employee_transfert_id.employee_id.begin_work_date', string=u'تاريخ بداية العمل الحكومي', readonly=1)
    transfert_create_date = fields.Datetime(string=u'تاريخ الطلب', related="hr_employee_transfert_id.create_date", readonly=1)
    last_evaluation_result = fields.Many2one('hr.employee.evaluation.level', related="hr_employee_transfert_id.last_evaluation_result", string=u'أخر تقييم إداء')
    new_job_id = fields.Many2one('hr.job', domain=[('state', '=', 'unoccupied')], string=u'الوظيفة المنقول إليها')
    is_conflected = fields.Boolean(compute='_compute_is_conflected')

    @api.multi
    def _compute_is_conflected(self):
        for rec in self:
            for line in rec.hr_transfert_sorting_id.line_ids:
                count = rec.hr_transfert_sorting_id.line_ids.search_count([('new_job_id', '=', line.new_job_id.id),
                                                                           ('hr_transfert_sorting_id', '=', line.hr_transfert_sorting_id.id)
                                                                           ])
                if count > 1:
                    line.is_conflected = True
                else:
                    line.is_conflected = False

    @api.onchange('hr_employee_transfert_id')
    def _onchange_hr_employee_transfert_id(self):
        # get all pending transfert demands in closed_periodes
        res = {}
        closed_periodes = self.env['hr.employee.transfert.periode'].search([('date_to', '<', datetime.today().strftime('%Y-%m-%d'))])
        closed_periodes_ids = [rec.id for rec in closed_periodes]
        hr_transferts = self.env['hr.employee.transfert'].search([('transfert_periode_id', 'in', closed_periodes_ids), ('state', '=', 'pm'), ('new_job_id', '=', False)])
        hr_transfert_ids = [rec.id for rec in hr_transferts]
        res['domain'] = {'hr_employee_transfert_id': [('id', 'in', hr_transfert_ids)]}
        return res


class HrTransfertCancel(models.Model):
    _name = 'hr.transfert.cancel'
    _description = u'‫إلغاء نقل أعضاء‬‬'

    name = fields.Char(string=u'المسمى', required=1, readonly=1, states={'new': [('readonly', 0)]})
    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now(), readonly=1)
    line_ids = fields.One2many('hr.transfert.sorting.line', 'hr_transfert_sorting_id', string=u'طلبات النقل', readonly=0, states={'done': [('readonly', 1)]})
    state = fields.Selection([('new', u'طلب'),
                              ('commission_president', u'رئيس الجهة'),
                              ('done', u'اعتمدت'),
                              ], readonly=1, default='new', string=u'الحالة')

    @api.multi
    def action_commission_president(self):
        self.ensure_one()
        self.state = 'commission_president'

    @api.multi
    def action_done(self):
        self.ensure_one()
        for rec in self.line_ids:
            if rec.is_conflected:
                raise ValidationError(u"الرجاء حل الخلاف في الوظائف المختارة.")
        for rec in self.line_ids:
            rec.hr_employee_transfert_id.write({'new_job_id': rec.new_job_id.id, 'ready_tobe_done': True})
        self.state = 'done'
