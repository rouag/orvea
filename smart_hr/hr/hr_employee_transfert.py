# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrEmployeeTransfert(models.Model):
    _name = 'hr.employee.transfert'
    _description = u'طلب نقل موظف'
    _rec_name = 'employee_id'

    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now(), readonly=1)
    sequence = fields.Integer(string=u'رتبة الطلب')
    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), required=1, readonly=1)
    last_evaluation_result = fields.Many2one('hr.employee.evaluation.level', string=u'أخر تقييم إداء')
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', string=u'الوظيفة', readonly=1, required=1)
    specific_id = fields.Many2one('hr.groupe.job', related='job_id.specific_id', string=u'المجموعة النوعية', readonly=1, required=1)
    occupied_date = fields.Date(related='job_id.occupied_date', string=u'تاريخ الشغول')
    type_id = fields.Many2one('salary.grid.type', related='employee_id.type_id', string=u'الصنف', readonly=1, required=1)
    new_job_id = fields.Many2one('hr.job', domain=[('state', '=', 'unoccupied')], string=u'الوظيفة المنقول إليها')
    new_specific_id = fields.Many2one('hr.groupe.job', related='new_job_id.specific_id', readonly=1, string=u'المجموعة النوعية')
    new_type_id = fields.Many2one('salary.grid.type', related='new_job_id.type_id', readonly=1, string=u'الصنف')
    justification_text = fields.Text(string=u'مبررات النقل', readonly=1, required=1, states={'new': [('readonly', 0)]})
    note = fields.Text(string=u'ملاحظات')
    comm_president_accept = fields.Boolean(string=u'موافقة رئيس الجهة', default=False)
    same_group = fields.Boolean(compute='_compute_same_specific_group', default=False)
    decision_number = fields.Char(string=u"رقم القرار")
    decision_date = fields.Date(string=u'تاريخ القرار')
    decision_file = fields.Binary(string=u'نسخة القرار')
    degree_id = fields.Many2one('salary.grid.degree', string=u'الدرجة')
    date_direct_action = fields.Date(string=u'تاريخ مباشرة العمل')
    governmental_entity = fields.Many2one('res.partner', string=u'الجهة الحكومية', domain=[('company_type', '=', 'governmental_entity')])
    desire_ids = fields.Many2many('hr.employee.desire', required=1, readonly=1, states={'new': [('readonly', 0)]})
    refusing_date = fields.Date(string=u'تاريخ الرفض', readonly=1)
    # conflicted with
    conflicted_emp_trans_id = fields.Many2one('hr.employee.transfert', domain=[('state', '=', 'pm')], string=u'الطلب المتعارض معه')
    # ‫المدنتية ‫الخدمة‬ ‫موافلقة‬
    speech_number = fields.Char(string=u'رقم الخطاب')
    speech_date = fields.Date(string=u'تاريخ الخطاب')
    speech_file = fields.Binary(string=u'نسخة الخطاب')
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'صاحب الصلاحية'),
                              ('pm', u'شؤون الموظفين'),
                              ('commission_president', u'رئيس الجهة'),
                              ('done', u'اعتمدت'),
                              ('refused', u'رفض'),
                              ('cancelled', u'ملغى')
                              ], readonly=1, default='new', string=u'الحالة')
    transfert_type = fields.Selection([('internal_transfert', u'نقل داخلي'),
                                       ('external_transfert_out', u'نقل خارجي (من الهيئة إلى جهة أخرى)'),
                                       ('external_transfert_in', u'نقل خارجي (إلى الهيئة)'),
                                       ], readonly=1, states={'new': [('readonly', 0)]}, default='internal_transfert', string=u'طبيعة النقل')

    @api.multi
    @api.depends('new_specific_id', 'specific_id')
    def _compute_same_specific_group(self):
        for rec in self:
            if rec.specific_id and rec.new_specific_id:
                rec.same_group = rec.specific_id == rec.new_specific_id
            else:
                rec.same_group = False

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        # get last evaluation result
        print self.conflicted_emp_trans_id
        if self.employee_id:
            previews_year = int(date.today().year) - 1
            last_evaluation_result = self.employee_id.evaluation_level_ids.search([('year', '=', int(previews_year))])
            if last_evaluation_result:
                self.last_evaluation_result = last_evaluation_result

    @api.onchange('desire_ids')
    def _onchange_desire_ids(self):
        # check desire_ids length from config
        hr_config = self.env['hr.setting'].search([], limit=1)
        if hr_config:
            if len(self.desire_ids) > hr_config.desire_number:
                raise ValidationError(u"لا يمكن إضافة أكثر من " + str(hr_config.desire_number) + u" رغبات.")

    @api.multi
    @api.constrains('transfert_type', 'desire_ids')
    def check_constrains(self):
        self.ensure_one()
        hr_config = self.env['hr.setting'].search([], limit=1)
        # do not allow creating tranfert if there is no open periode
        open_periodes = self.env['hr.employee.transfert.periode'].search([('date_to', '>=', datetime.today().strftime('%Y-%m-%d'))])
        if not open_periodes and self.state == 'new':
            raise ValidationError(u"لا يوجة فترة مفتوحة لإستقبال الطلبات.")
        # check if there is a refused transfert demand before 45days
        transferts = self.env['hr.employee.transfert'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'refused')])
        for transfert in transferts:
            today = date.today()
            days = (today - fields.Date.from_string(transfert.refusing_date)).days
            if hr_config:
                if days < hr_config.needed_days:
                    raise ValidationError(u"لا يمكن تقديم طلب إلى بعد " + str(hr_config.needed_days) + u" يوماً.")
        # ‫التجربة‬ ‫سنة‬ ‫إستلكمال‬
        recruitement_decision = self.employee_id.decision_appoint_ids.search([('is_started', '=', True)], limit=1)
        if recruitement_decision and recruitement_decision.depend_on_test_periode:
            testing_date_to = recruitement_decision.testing_date_to
            if fields.Date.from_string(testing_date_to) >= fields.Date.from_string(fields.Datetime.now()):
                raise ValidationError(u"لايمكن طلب نقل خلال فترة التجربة")
        # ‫التترقية‬ ‫سنة‬ ‫إستلكمال‬
        if self.employee_id.promotions_history:
            # get last promotion
            last_promotion_ids = self.employee_id.promotions_history.search([('date_to', '!=', False)])
            if last_promotion_ids:
                promotion_id = last_promotion_ids[0]
                for rec in last_promotion_ids:
                    if fields.Date.from_string(promotion_id.date_to) < fields.Date.from_string(rec.date_to):
                        promotion_id = rec
                date_to = promotion_id.date_to
                diff = relativedelta(fields.Date.from_string(fields.Datetime.now()), fields.Date.from_string(date_to)).years
                if diff < 1:
                    raise ValidationError(u"لايمكن طلب نقل خلال أقل من سنة منذ أخر ترقية")
        # check desire_ids length from config
        if hr_config:
            if len(self.desire_ids) > hr_config.desire_number:
                raise ValidationError(u"لا يمكن إضافة أكثر من " + str(hr_config.desire_number) + u" رغبات.")

    @api.multi
    def action_waiting(self):
        self.ensure_one()
        self.state = 'waiting'

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
        self.state = 'pm'
        if not self.new_job_id:
            # add this demand to hr.transfert.sorting for the first time
            trans_sort_obj = self.env['hr.transfert.sorting'].search([], limit=1)
            if trans_sort_obj:
                trans_sort_obj.hr_transfert_ids = [(4, self.id)]

    @api.multi
    def action_com_president(self):
        self.ensure_one()
        self.state = 'commission_president'

    @api.multi
    def action_refused(self):
        self.ensure_one()
        self.refusing_date = datetime.now()
        self.state = 'refused'
        # send notification for the employee
        self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                              'message': u'لقد تم رفض طلب نقل, ' + str(self.note),
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
            if rec.transfert_type == 'external_transfert_out':
                if rec.check_judicial_precedent(self.employee_id):
                    rec.note = u'الموظف لديه سوابق عدلية'
                    rec.action_refused()
                    return

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
            recruiter_id.action_done()
            rec.state = 'done'
            # remove this demand from hr.transfert.sorting
            trans_sort_obj = self.env['hr.transfert.sorting'].search([], limit=1)
            if trans_sort_obj:
                trans_sort_obj.hr_transfert_ids = [(3, rec.id)]
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
            if rec.transfert_type == 'external_transfert_out':
                # send notification for the employee
                self.env['base.notification'].create({'title': u'إشعار بموافقة طلب',
                                                      'message': u'لقد تمت الموافقة على طلب النقل - الرجاء جلب طلب النقل من الجهة.',
                                                      'user_id': rec.employee_id.user_id.id,
                                                      'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                      'res_id': rec.id,
                                                      'res_action': 'smart_hr.action_hr_employee_transfert',
                                                      'notif': True
                                                      })

    @api.multi
    def action_pick_job(self):
        self.ensure_one()
        hr_emp_tran_obj = self.env['hr.employee.transfert'].search([('id', '=', int(self._context['rec_id']))])
        if hr_emp_tran_obj:
            hr_emp_tran_obj.write({'new_job_id': int(self._context['new_job_id']), 'conflicted_emp_trans_id': int(self._context['conflicted_emp_trans_id'])})

    @api.multi
    def action_choose(self):
        self.comm_president_accept = True
        self.conflicted_emp_trans_id.comm_president_accept = False
        self.conflicted_emp_trans_id.conflicted_emp_trans_id = False
        self.conflicted_emp_trans_id.new_job_id = False
        self.conflicted_emp_trans_id.action_notif()
        self.conflicted_emp_trans_id = False
        self.action_pm()

    def check_judicial_precedent(self, employee_id):
        emp_jud_prec_ids = self.env['employee.judicial.precedent.order'].search([('employee', '=', employee_id.id)])
        if emp_jud_prec_ids:
            return True
        else:
            return False


class HrEmployeeTransfertPeriode(models.Model):
    _name = 'hr.employee.transfert.periode'
    _description = u'فترات النقل'
    _rec_name = "date_from"

    date_from = fields.Date(string=u'التاريخ من ', default=fields.Datetime.now())
    date_to = fields.Date(string=u'التاريخ الى')


class HrTransfertSorting(models.Model):
    _name = 'hr.transfert.sorting'
    _description = u'‫ترتيب طلبات النقل مع الوظائف المناسبة‬‬'

    name = fields.Char(string='name')
    hr_transfert_ids = fields.Many2many('hr.employee.transfert', string=u'طلبات النقل')

    @api.multi
    def button_transfert_sorting(self):
        hr_transfert_sorting = self.env['hr.transfert.sorting'].search([], limit=1)
        if hr_transfert_sorting:
            value = {
                'name': u'ترتيب طلبات النقل مع الوظائف المناسبة',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.transfert.sorting',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': hr_transfert_sorting.id,
            }
            return value

    @api.multi
    def write(self, vals):
        # hr_transfert_ids = vals['hr_transfert_ids'][0][2]
        """
        TODO: recalculate the right sequence for each hr_transfert_id
        """
        return models.Model.write(self, vals)
