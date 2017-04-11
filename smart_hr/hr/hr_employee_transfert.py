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
    employee_id = fields.Many2one('hr.employee', string=u'صاحب الطلب',  required=1,
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid), ('emp_state', 'not in', ['suspended','terminated'])], limit=1),)
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
    degree_id = fields.Many2one('salary.grid.degree',related='employee_id.degree_id', string=u'الدرجة', readonly=1)
    new_degree_id = fields.Many2one('salary.grid.degree', string=u'الدرجة', readonly=1)
    governmental_entity = fields.Many2one('res.partner', string=u'الجهة الحكومية', domain=[('company_type', '=', 'governmental_entity')], readonly=1, states={'new': [('readonly', 0)]})
    desire_ids = fields.One2many('hr.employee.desire',  'desire_id', store=True,required=1, string=u'رغبات النقل', readonly=1, states={'new': [('readonly', 0)]})
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
    is_paied = fields.Boolean(string='is paied', default=False)
    defferential_is_paied = fields.Boolean(string='defferential is paied', default=False)
    payslip_id = fields.Many2one('hr.payslip')
    done_date = fields.Date(string='تاريخ التفعيل')

    job_allowance_ids = fields.One2many('hr.transfert.allowance', 'job_transfert_id', string=u'بدلات الوظيفة')
    transfert_allowance_ids = fields.One2many('hr.transfert.allowance', 'transfert_id', string=u'بدلات النقل')
    location_allowance_ids = fields.One2many('hr.transfert.allowance', 'location_transfert_id', string=u'بدلات المنطقة')

    @api.multi
    @api.onchange('transfert_nature')
    def onchange_transfert_nature(self):
        #TODO: ???
        res = {}
        if self.transfert_nature == 'internal_transfert' or self.transfert_nature == 'external_transfert_out':
            res['domain'] = {'employee_id': [('employee_state', '=', 'employee')]}
            return res
        else:
            res['domain'] = {'employee_id': [('employee_state', '=', 'done')]}
            self.employee_id = False
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

    @api.one
    @api.constrains('employee_id')
    def check_score(self):
        for rec in self :
            count_trasfert = self.env['hr.employee.transfert'].search_count([('employee_id', '=', rec.employee_id.id),('state','in',['new','waiting','pm','consult'])])
            if count_trasfert > 1:
                raise ValidationError(u"لا  يمكن  تقديم طلب  نقل وهناك أخر قيد الدراسة او في مرحلة الإنتظار")
    
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
                if self.employee_id.promotion_duration < 354:
                    raise ValidationError(u"لايمكن طلب نقل خلال أقل من سنة منذ أخر ترقية")
# #             # check desire_ids length from config
            if hr_config:
                if len(self.desire_ids) > hr_config.desire_number:
                    raise ValidationError(u"لا يمكن إضافة أكثر من " + str(hr_config.desire_number) + u" رغبات.")

        # 2- constraintes for members without special conditions
        if self.transfert_type == 'member' and self.special_conditions is False:
            # ‫التترقية‬ ‫سنة‬ ‫إستلكمال‬
#             if self.employee_id.promotion_duration < 1:
#                             raise ValidationError(u"لايمكن طلب نقل خلال أقل من سنة منذ أخر ترقية أو تعين")
#             # check 3 years constrainte from last transfert
            last_transfert_id = self.env['hr.employee.transfert'].search([('id', '!=', self.id)], order="create_date desc", limit=1)
            today = date.today()
            create_date = fields.Date.from_string(last_transfert_id.create_date)
            if create_date:
                years = relativedelta(today - create_date).years
                if hr_config:
                    if years < hr_config.years_last_transfert:
                        raise ValidationError(u"لم تتم " + str(hr_config.years_last_transfert) + u" سنوات من أخر نقل.")
#             # chek if there is any sanction for the emmployee
#             if len(self.employee_id.sanction_ids) > 0:
#                 raise ValidationError(u"لدى الموظف عقوبات.")

    @api.multi
    def action_waiting(self):
        for rec in self :
            count_trasfert = self.env['hr.employee.transfert'].search_count([('employee_id', '=', rec.employee_id.id),('state', '=', 'new')])
            print"count_trasfert",count_trasfert
            if count_trasfert > 1:
                raise ValidationError(u"لا يمكن تعين عضو دون الدرجة المطلوبة")
        self.state = 'waiting'

    @api.multi
    def action_consultation(self):
        for rec in self :
            if rec.state == 'consult' :
                employ_trasfert = self.env['hr.transfert.sorting.line2'].search([('hr_employee_transfert_id', '=', rec.employee_id.id)])
                if employ_trasfert:
                    employ_trasfert.state = 'pm'
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

        self.state = 'pm'

    @api.multi
    def button_refuse(self):
        for rec in self :
            if rec.state == 'consult' :
                employ_trasfert = self.env['hr.transfert.sorting.line2'].search([('hr_employee_transfert_id', '=', rec.employee_id.id)])
                if employ_trasfert:
                    employ_trasfert.state = 'refused'
        # send notification for the employee
            if rec.state == 'pm' :
                msg = u', '
                if rec.note:
                    msg += self.note
                    self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                              'message': u'لقد تم رفض طلب نقل ' + str(msg),
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'res_id': self.id,
                                              'res_action': 'smart_hr.action_hr_employee_transfert',
                                              'notif': True
                                              })
        self.refusing_date = datetime.now()
        self.state = 'refused'

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
#                 if not rec.decision_number:
#                     raise ValidationError(u"لم يتم إصدار قرار بشأن النقل.")
                vals = {
                    'type_appointment': self.env.ref('smart_hr.data_hr_recrute_from_transfert').id,
                    'employee_id': rec.employee_id.id,
                    'job_id': rec.new_job_id.id,
                    'degree_id': rec.degree_id.id,
                    'transfer_id': rec.id,
                    'name': rec.speech_number,
                    'order_date': rec.speech_date,}
            else:
#                 if not rec.speech_number:
#                     raise ValidationError(u"لم يتم خطاب قرار بشأن النقل.")
                # with speech file
                vals = {
                    'type_appointment': self.env.ref('smart_hr.data_hr_recrute_from_transfert').id,
                    'employee_id': rec.employee_id.id,
                    'job_id': rec.new_job_id.id,
                    'degree_id': rec.degree_id.id,
                    'transfer_id': rec.id,
                    'name': rec.speech_number,
                    'order_date': rec.speech_date,
                }
            recruiter_id = self.env['hr.decision.appoint'].create(vals)
            if recruiter_id:
                recruiter_id._onchange_employee_id()
                recruiter_id._onchange_job_id()
                recruiter_id._onchange_degree_id()
                # copy allowances from transfert to the decision_appoint
                # بدلات الوظيفة
                job_allowance_ids = []
                for allowance in rec.job_allowance_ids:
                    job_allowance_ids.append({'job_decision_appoint_id': recruiter_id.id,
                                              'allowance_id': allowance.allowance_id.id,
                                              'compute_method': allowance.compute_method,
                                              'amount': allowance.amount
                                              })
                recruiter_id.job_allowance_ids = job_allowance_ids
                # بدلات التعين
                transfert_allowance_ids = []
                for allowance in rec.transfert_allowance_ids:
                    job_allowance_ids.append({'decision_decision_appoint_id': recruiter_id.id,
                                              'allowance_id': allowance.allowance_id.id,
                                              'compute_method': allowance.compute_method,
                                              'amount': allowance.amount
                                              })
                recruiter_id.decision_apoint_allowance_ids = transfert_allowance_ids
                # بدلات المنطقة
                location_allowance_ids = []
                for allowance in rec.location_allowance_ids:
                    location_allowance_ids.append({'location_decision_appoint_id': recruiter_id.id,
                                                   'allowance_id': allowance.allowance_id.id,
                                                   'compute_method': allowance.compute_method,
                                                   'amount': allowance.amount
                                                   })
                recruiter_id.location_allowance_ids = location_allowance_ids
                # change state of the decision to done
                recruiter_id.action_done()
                rec.done_date = fields.Date.today()

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


class HrTransfertAllowance(models.Model):
    _name = 'hr.transfert.allowance'
    _description = u'those allowances will be transmitted to the decision appointment'
    _description = u'بدلات'

    job_transfert_id = fields.Many2one('hr.employee.transfert', string='النقل', ondelete='cascade')
    transfert_id = fields.Many2one('hr.employee.transfert', string='النقل', ondelete='cascade')
    location_transfert_id = fields.Many2one('hr.employee.transfert', string='النقل', ondelete='cascade')
    allowance_id = fields.Many2one('hr.allowance.type', string='البدل', required=1)
    compute_method = fields.Selection([('amount', 'مبلغ'),
                                       ('percentage', 'نسبة من الراتب الأساسي'),
                                       ('formula_1', 'نسبة‬ البدل‬ * راتب‬  الدرجة‬ الاولى‬  من‬ المرتبة‬  التي‬ يشغلها‬ الموظف‬'),
                                       ('formula_2', 'نسبة‬ البدل‬ * راتب‬  الدرجة‬ التي ‬ يشغلها‬ الموظف‬'),
                                       ('job_location', 'تحتسب  حسب مكان العمل')], required=1, string='طريقة الإحتساب')
    amount = fields.Float(string='المبلغ')
    min_amount = fields.Float(string='الحد الأدنى')
    percentage = fields.Float(string='النسبة')
    line_ids = fields.One2many('salary.grid.detail.allowance.city', 'allowance_id', string='النسب حسب المدينة')


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
    speech_number = fields.Char(string=u'رقم الخطاب')
    speech_date = fields.Date(string=u'تاريخ الخطاب')
    speech_file = fields.Binary(string=u'نسخة الخطاب', attachment=True)
    speech_file_name = fields.Char(string=u'نسخة الخطاب')
    line_ids = fields.One2many('hr.transfert.sorting.line', 'hr_transfert_sorting_id', string=u'طلبات النقل', readonly=0, states={'done': [('readonly', 1)]})
    line_ids2 = fields.One2many('hr.transfert.sorting.line2', 'hr_transfert_sorting_id2', string=u'طلبات النقل',)
    line_ids3 = fields.One2many('hr.transfert.sorting.line3', 'hr_transfert_sorting_id3', string=u'طلبات النقل',)
    line_ids4 = fields.One2many('hr.transfert.sorting.line4', 'hr_transfert_sorting_id4', string=u'طلبات النقل',)
    line_ids5 = fields.One2many('hr.transfert.sorting.line5', 'hr_transfert_sorting_id5', string=u'طلبات النقل',)
    is_ended = fields.Boolean(string=u'انتهت',default = False)
    is_commission_third = fields.Boolean(string=u'الخدمة المدنية',default = False)

    state = fields.Selection([('new', u'ترتيب الطلبات'),
                               ('draft', u'إسناد الوظائف'),
                              ('waiting', u'إعتماد الموظفين'),
                              ('commission_president', u'رئيس الجهة'),
                              ('commission_third', u'الخدمة المدنية'),
                              ('benefits', u'إسناد المزايا'),
                              ('issuing_decision', u'استصدار قرار'),
                              ('done', u'اعتمدت'),
                              ('refused', u'مرفوضة')
                              ], readonly=1, default='new', string=u'الحالة')
    decision_id = fields.Many2one('hr.decision')

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
        self.is_ended = True



    @api.multi
    def action_draft(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(u"لايوجد طلبات حالياً.")
            line_ids = []
            for line in rec.line_ids:
                if line.hr_employee_transfert_id:
                    vals = {'hr_employee_transfert_id': line.hr_employee_transfert_id.id,
                            'hr_employee_transfert_id.state':'pm',
                            'state': line.state ,
                            }
                    line_ids.append(vals)
            rec.line_ids2 = line_ids
            rec.state = 'draft'

    @api.multi
    def action_waiting(self):
        for rec in self :
            line_ids = []
            line_ids1 = []
            result = []
            result1 = []
            for line in rec.line_ids2 :
                if   line.new_job_id.id != 0  :
#                 if line.is_conflected:
#                     raise ValidationError(u"الرجاء حل الخلاف في الوظائف المختارة.")
                    vals = {'hr_employee_transfert_id': line.hr_employee_transfert_id.id,
                                  # 'hr_employee_transfert_id.state':'consult',
                                    'new_job_id': line.new_job_id.id,
                                    'new_type_id': line.new_type_id.id,
                                    'res_city': line.res_city.id,
                                    'new_degree_id': line.new_degree_id.id,
                                    'specific_group': line.specific_group,
                                   }
                    line.hr_employee_transfert_id.ready_tobe_done =True
                    line.hr_employee_transfert_id.new_job_id =line.new_job_id.id,
                    line.hr_employee_transfert_id.new_type_id =line.new_type_id.id,
                    line.hr_employee_transfert_id.new_degree_id =line.new_degree_id.id,
                    self.env['base.notification'].create({'title': u'إشعار  بخفض درجة',
                                                   'message': u'لقد تم خفض درجة',
                                                   'user_id': line.hr_employee_transfert_id.employee_id.user_id.id,
                                                   'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                   'notif': True,
                                                     'res_id': self.id,
                                                       })
                    if int(line.degree_id.code) > int(line.new_degree_id.code):
                        line.hr_employee_transfert_id.state ='consult'
                        line_ids.append(vals)
                        print"line_ids",line_ids
                        result = line_ids
                    else :
                        line.hr_employee_transfert_id.state ='pm'
                        line_ids1.append(vals)
                        print"line_ids1",line_ids1
                        result1 = line_ids1

                if  line.new_job_id.id == 0 :
                    line.hr_employee_transfert_id.state ='new'
                    self.env['base.notification'].create({'title': u'إشعار  بعدم وجود وظيفة شاغرة',
                                                   'message': u'إشعار  بعدم وجود وظيفة شاغرة',
                                                   'user_id': line.hr_employee_transfert_id.employee_id.user_id.id,
                                                   'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                   'notif': True,
                                                     'res_id': self.id,
                                                     }) 
        if len(result) > 0:
            self.line_ids3 = result + result1
            self.state = 'waiting'
        else :
            self.line_ids4 = result1
            self.state = 'commission_president'

    @api.multi
    def action_commissioning(self):
        for rec in self:
            line_ids = []
            print '--rec.line_ids3---', rec.line_ids3
            for line in rec.line_ids3 :
                if line.hr_employee_transfert_id.state =='consult' :
                    raise ValidationError(u"يوجد طلبات في قائمة الانتظار.")
                vals = {'hr_employee_transfert_id': line.hr_employee_transfert_id.id,
                        'hr_employee_transfert_id.state':'pm',
                        'new_job_id': line.new_job_id.id,
                        'new_type_id': line.new_type_id.id,
                        'res_city': line.res_city.id,
                        'new_degree_id': line.new_degree_id.id,
                        'specific_group': line.specific_group, }
                line_ids.append(vals)
            rec.line_ids4 = line_ids
            rec.state = 'commission_president'
 


    @api.multi
    def button_refuse(self):
        self.ensure_one()
        self.state = 'refused'
    
    @api.multi
    def action_commission_president(self):
        for rec in self :
            line_ids = []
            line_ids1 = []
            result = []
            for line in rec.line_ids4:
                if line.specific_group =='other_specific' and line.accept_trasfert == True :
                        vals = {'hr_employee_transfert_id': line.hr_employee_transfert_id.id,
                                'state': line.hr_employee_transfert_id.state,
                                'new_job_id': line.new_job_id.id,
                                'new_type_id': line.new_type_id.id,
                                'res_city': line.res_city.id,
                                'new_degree_id': line.new_degree_id.id,
                                'specific_group': line.specific_group,

                                }
                        line.hr_employee_transfert_id.state ='done'
                        line_ids.append(vals)
                result = line_ids
                if line.specific_group =='other_specific' and line.accept_trasfert == False :
                        self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                                      'message': u'لقد تمت رفض  الطلب من الجهة.',
                                                      'user_id': line.hr_employee_transfert_id.employee_id.user_id.id,
                                                      'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                      'res_id': rec.id,
                                                      'notif': True
                                                      })

                        line.hr_employee_transfert_id.state ='refused'
                if line.specific_group =='same_specific' :
                    if line.accept_trasfert == True :
                        line.hr_employee_transfert_id.state ='done'
                        line.hr_employee_transfert_id.employee_id.job_id = line.new_job_id.id
                        line.hr_employee_transfert_id.new_job_id.state='occupied'
                        #line_ids1.append(vals)
                        self.env['base.notification'].create({'title': u'إشعار بموافقة طلب',
                                                      'message': u'لقد تمت الموافقة على طلب النقل.',
                                                      'user_id': line.hr_employee_transfert_id.employee_id.user_id.id,
                                                      'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                      'res_id': rec.id,
                                                      'notif': True
                                                      })
                        if line.accept_trasfert == False :
                            self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                                      'message': u'لقد تمت رفض  الطلب من الجهة.',
                                                      'user_id': line.hr_employee_transfert_id.employee_id.user_id.id,
                                                      'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                      'res_id': rec.id,
                                                      'notif': True
                                                      })
 
                        line.hr_employee_transfert_id.state ='refused'

            if len(result) > 0:
                rec.line_ids5 = result
                rec.state = 'commission_third'
            else:
                rec.state = 'benefits'


    @api.multi
    def action_commission_third(self):
        for rec in self :
            line_ids = []
            for line in rec.line_ids5:
                if line.accept_trasfert == True :
                    vals = {'hr_employee_transfert_id': line.hr_employee_transfert_id.id,
                                'state': line.state,
                                'new_job_id': line.new_job_id.id,
                                'new_type_id': line.new_type_id.id,
                                'res_city': line.res_city.id,
                                'new_degree_id': line.new_degree_id.id,
                                'specific_group': line.specific_group,
                                }
                    self.env['base.notification'].create({'title': u'إشعار بموافقة طلب',
                                                      'message': u'لقد تمت الموافقة على طلب النقل .',
                                                      'user_id': line.hr_employee_transfert_id.employee_id.user_id.id,
                                                      'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                      'res_id': rec.id,
                                                      'notif': True
                                                      })
                   # line.hr_employee_transfert_id.accept_trasfert = True
                   # line_ids.append(vals)
                    line.hr_employee_transfert_id.employee_id.job_id = line.new_job_id.id
                    line.hr_employee_transfert_id.new_job_id.state = 'occupied'
                if line.accept_trasfert == False :
                    self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                                      'message': u'لقد تمت رفض  الطلب من الجهة.',
                                                      'user_id': line.hr_employee_transfert_id.employee_id.user_id.id,
                                                      'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                      'res_id': rec.id,
                                                      'notif': True
                                                      })
                    #line.hr_employee_transfert_id.accept_trasfert = False
                    line.hr_employee_transfert_id.state ='refused'
            rec.line_ids4 = line_ids
            rec.state = 'benefits'

    @api.multi
    def action_issuing_decision(self):
        self.state='issuing_decision'   

    @api.multi
    def action_done(self):
        for rec in self:
            for line in rec.line_ids4:
                line.hr_employee_transfert_id.speech_number = rec.decision_id.name
                line.hr_employee_transfert_id.speech_date = rec.decision_id.date
                line.hr_employee_transfert_id.action_done()
            rec.state = 'done'


class HrTransfertSortingLine(models.Model):
    _name = 'hr.transfert.sorting.line'
    _description = u'‫طلبات النقل‬‬'

    hr_transfert_sorting_id = fields.Many2one('hr.transfert.sorting', string=u'إجراء الترتيب')
    hr_employee_transfert_id = fields.Many2one('hr.employee.transfert', string=u'طلب نقل موظف')
    state = fields.Selection(related='hr_employee_transfert_id.state' ,string=u'الحالة')
    accept_trasfert = fields.Boolean(string='قبول')
    cancel_trasfert = fields.Boolean(string='رفض')
   
    sequence = fields.Integer(string=u'رتبة الطلب', related='hr_employee_transfert_id.sequence', readonly=1)
    recruiter_date = fields.Date(string=u'تاريخ التعين بالجهة', related='hr_employee_transfert_id.employee_id.recruiter_date', readonly=1)
    age = fields.Integer(string=u'السن', related='hr_employee_transfert_id.employee_id.age', readonly=1)
    job_id = fields.Many2one('hr.job', related='hr_employee_transfert_id.job_id', string=u'الوظيفة', readonly=1)
    begin_work_date = fields.Date(related='hr_employee_transfert_id.employee_id.begin_work_date', string=u'تاريخ بداية العمل الحكومي', readonly=1)
    transfert_create_date = fields.Datetime(string=u'تاريخ الطلب', related="hr_employee_transfert_id.create_date", readonly=1)
    last_evaluation_result = fields.Many2one('hr.employee.evaluation.level', related="hr_employee_transfert_id.last_evaluation_result", string=u'أخر تقييم إداء')
    new_job_id = fields.Many2one('hr.job', domain=[('state', '=', 'unoccupied')], string=u'الوظيفة المنقول إليها')
    is_conflected = fields.Boolean(compute='_compute_is_conflected')
    res_city = fields.Many2one('res.city', string=u'المدينة')
    specific_group = fields.Selection([('same_specific', 'في نفس المجموعة النوعية'), ('other_specific', 'في مجموعة أخرى'), ], string=u'نوع المجموعة')
    new_type_id = fields.Many2one('salary.grid.type', string=u'الصنف', readonly=1)
    new_degree_id = fields.Many2one('salary.grid.degree', string=u'الدرجة') 
    new_department_id = fields.Many2one('hr.department', related='new_job_id.department_id', string='مقر الوظيفة')
    degree_id = fields.Many2one('salary.grid.degree',related='hr_employee_transfert_id.employee_id.degree_id', string=u'الدرجة', readonly=1)
   # desire_ids = fields.One2many(related='hr_employee_transfert_id.desire_ids', string=u'رغبات النقل',)

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



class HrTransfertSortingLine2(models.Model):
    _name = 'hr.transfert.sorting.line2'
    _inherit = 'hr.transfert.sorting.line'

    specific_group = fields.Selection([('same_specific', 'في نفس المجموعة النوعية'), ('other_specific', 'في مجموعة أخرى')],string=u'نوع المجموعة')
    hr_transfert_sorting_id2 = fields.Many2one('hr.transfert.sorting', string=u'إجراء الترتيب')
    accept_trasfert = fields.Boolean(string='قبول')
    cancel_trasfert = fields.Boolean(string='رفض')
   # desire_ids = fields.One2many('hr.employee.desire',  'desire_id', store=True,  string=u'رغبات النقل', readonly=1,
                              #    related='hr_employee_transfert_id.desire_ids')


class HrTransfertSortingLine3(models.Model):
    _name = 'hr.transfert.sorting.line3'
    _inherit = 'hr.transfert.sorting.line'
    
    specific_group = fields.Selection([('same_specific', 'في نفس المجموعة النوعية'), ('other_specific', 'في مجموعة أخرى'), ],  string=u'نوع المجموعة')
    hr_transfert_sorting_id3 = fields.Many2one('hr.transfert.sorting', string=u'إجراء الترتيب')
    accept_trasfert = fields.Boolean(string='قبول')
    cancel_trasfert = fields.Boolean(string='رفض')

class HrTransfertSortingLine4(models.Model):
    _name = 'hr.transfert.sorting.line4'
    _inherit = 'hr.transfert.sorting.line'

    hr_transfert_sorting_id4 = fields.Many2one('hr.transfert.sorting', string=u'إجراء الترتيب')
    accept_trasfert = fields.Boolean(string='قبول')
    cancel_trasfert = fields.Boolean(string='رفض')


class HrTransfertSortingLine5(models.Model):
    _name = 'hr.transfert.sorting.line5'
    _inherit = 'hr.transfert.sorting.line'

    hr_transfert_sorting_id5 = fields.Many2one('hr.transfert.sorting', string=u'إجراء الترتيب')
    accept_trasfert = fields.Boolean(string='قبول')
    cancel_trasfert = fields.Boolean(string='رفض')


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

#     @api.multi
#     def action_commission_president(self):
#         self.ensure_one()
#         self.state = 'commission_president'

    @api.multi
    def action_done(self):
        self.ensure_one()
        for rec in self.line_ids:
            if rec.is_conflected:
                raise ValidationError(u"الرجاء حل الخلاف في الوظائف المختارة.")
        for rec in self.line_ids:
            rec.hr_employee_transfert_id.write({'new_job_id': rec.new_job_id.id, 'ready_tobe_done': True})
        self.state = 'done'
