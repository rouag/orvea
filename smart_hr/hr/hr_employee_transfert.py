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
    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), required=1, readonly=1)
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', string=u'الوظيفة', readonly=1, required=1)
    specific_id = fields.Many2one('hr.groupe.job', related='job_id.specific_id', string=u'المجموعة النوعية', readonly=1, required=1)
    type_id = fields.Many2one('salary.grid.type', related='employee_id.type_id', string=u'الصنف', readonly=1, required=1)
    new_job_id = fields.Many2one('hr.job', domain=[('state', '=', 'unoccupied')], string=u'الوظيفة المنقول إليها')
    new_specific_id = fields.Many2one('hr.groupe.job', related='new_job_id.specific_id', readonly=1, string=u'المجموعة النوعية')
    new_type_id = fields.Many2one('salary.grid.type', related='new_job_id.type_id', readonly=1, string=u'الصنف')
    justification_text = fields.Text(string=u'مبررات النقل', readonly=1, required=1, states={'new': [('readonly', 0)]})
    same_group = fields.Boolean(compute='_compute_same_specific_group', default=False)
    decision_number = fields.Char(string=u"رقم القرار")
    decision_date = fields.Date(string=u'تاريخ القرار')
    decision_file = fields.Binary(string=u'نسخة القرار')
    degree_id = fields.Many2one('salary.grid.degree', string=u'الدرجة')
    date_direct_action = fields.Date(string=u'تاريخ مباشرة العمل') 
    # ‫المدنتية ‫الخدمة‬ ‫موافلقة‬
    speech_number = fields.Char(string=u'رقم الخطاب')
    speech_date = fields.Date(string=u'تاريخ الخطاب')
    speech_file = fields.Binary(string=u'نسخة الخطاب')
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'صاحب الصلاحية'),
                              ('pm', u'شؤون الموظفين'),
                              ('pending', u'في الإنتظار'),
                              ('done', u'اعتمدت'),
                              ('refused', u'رفض')
                              ], readonly=1, default='new', string=u'الحالة')
    transfert_type = fields.Selection([('internal_transfert', u'نقل داخلي'),
                                       ('external_transfert_out', u'نقل خارجي (من الهيئة إلى جهة أخرى)'),
                                       ('external_transfert_in', u'نقل خارجي (إلى الهيئة)'),
                                       ], readonly=1, states={'new': [('readonly', 0)]}, default='internal_transfert', string=u'طبيعة النقل')

    @api.multi
    @api.depends('new_specific_id', 'specific_id')
    def _compute_same_specific_group(self):
        self.ensure_one()
        if self.specific_id and self.new_specific_id:
            self.same_group = self.specific_id == self.new_specific_id
        else:
            self.same_group = False

    @api.multi
    @api.constrains('transfert_type')
    def check_constrains(self):
        self.ensure_one()
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

    @api.multi
    def action_waiting(self):
        self.ensure_one()
        self.state = 'waiting'

    @api.multi
    def action_notif(self):
        self.ensure_one()
        self.state = 'pending'
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

    @api.multi
    def action_pending(self):
        self.ensure_one()
        self.state = 'pending'

    @api.multi
    def action_refused(self):
        self.ensure_one()
        self.state = 'refused'
        # send notification for the employee
        self.env['base.notification'].create({'title': u'إشعار برفض طلب',
                                              'message': u'لقد تم رفض طلب نقل',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'res_id': self.id,
                                              'res_action': 'smart_hr.action_hr_employee_transfert',
                                              'notif': True
                                              })

    @api.multi
    def action_done(self):
        self.ensure_one()
        if not self.new_job_id:
                    raise ValidationError(u"الرجاء التثبت من حقل الوظيفة المنقول إليها.")
        if not self.degree_id:
                    raise ValidationError(u"الرجاء التثبت من حقل الدرجة.")

        # create hr.decision.appoint object
        # with decision file
        if self.new_specific_id == self.specific_id:
            vals = {
                'type_appointment': self.env.ref('smart_hr.data_hr_recrute_from_transfert').id,
                'date_direct_action': self.date_direct_action,
                'employee_id': self.employee_id.id,
                'job_id': self.new_job_id.id,
                'degree_id': self.degree_id.id,
                'name': self.decision_number,
                'order_date': self.decision_date,
                'order_picture': self.decision_file
            }
        else:
            # with speech file
            vals = {
                'type_appointment': self.env.ref('smart_hr.data_hr_recrute_from_transfert').id,
                'date_direct_action': self.date_direct_action,
                'employee_id': self.employee_id.id,
                'job_id': self.new_job_id.id,
                'degree_id': self.degree_id.id,
                'name': self.speech_number,
                'order_date': self.speech_date,
                'order_picture': self.speech_file
            }
        recruiter_id = self.env['hr.decision.appoint'].create(vals)
        print recruiter_id
        recruiter_id.action_done()
        self.state = 'done'
