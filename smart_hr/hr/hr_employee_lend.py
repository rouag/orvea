# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrEmployeeLend(models.Model):
    _name = 'hr.employee.lend'
    _description = u'طلب إعارة موظف'
    _rec_name = 'employee_id'

    @api.multi
    def get_basic_salary(self):
        for rec in self:
            if rec.basic_salary:
                return rec.basic_salary

    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now(), readonly=1)
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1, readonly=1, states={'new': [('readonly', 0)]})
    insurance_entity = fields.Many2one('res.partner', string=u'الجهة المعار إليها', domain=[('insurance', '=', True)], required=1, readonly=1, states={'new': [('readonly', 0)]})
    decision_number = fields.Char(string=u"رقم القرار", required=1, readonly=1, states={'new': [('readonly', 0)]})
    decision_date = fields.Date(string=u'تاريخ القرار', required=1, readonly=1, states={'new': [('readonly', 0)]})
    decision_file = fields.Binary(string=u'نسخة القرار', required=1, readonly=1, states={'new': [('readonly', 0)]}, attachment=True)
    date_from = fields.Date(string=u'التاريخ من ', default=fields.Datetime.now(), readonly=1, states={'new': [('readonly', 0)]})
    date_to = fields.Date(string=u'التاريخ الى', compute='_compute_date_to', store=True)
    duration = fields.Integer(string=u'الأيام', required=1, readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', u'طلب'),
                              ('done', u'اعتمدت'),
                              ('sectioned', u'مقطوعة')
                              ], readonly=1, default='new', string=u'الحالة')
    decision_file_name = fields.Char()
    allowance_ids = fields.One2many('allowance.lend.amount', 'lend_id', string=u'البدلات التي تتحملها الجهة', readonly=1, states={'new': [('readonly', 0)]})
    salary_proportion = fields.Float(string=u'نسبة الراتب التي تتحملها الجهة', default=100.0, readonly=1, states={'new': [('readonly', 0)]})
    basic_salary = fields.Float(string=u'الراتب الأساسي', readonly=1)
    lend_salary = fields.Float(string=u'الراتب في الإعارة', readonly=1, states={'new': [('readonly', 0)]})
    pay_retirement = fields.Boolean(string=u'يدفع له نسبة التقاعد', readonly=1, states={'new': [('readonly', 0)]})

    @api.multi
    @api.depends('date_from', 'duration')
    def _compute_date_to(self):
        self.ensure_one()
        if self.date_from and self.duration:
            new_date_to = self.env['hr.smart.utils'].compute_date_to(self.date_from, self.duration)
            self.date_to = new_date_to
        elif self.date_from:
                self.date_to = self.date_from

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.ensure_one()
        if self.employee_id:
            if self.employee_id.get_salary_grid_id(False):
                self.basic_salary = self.employee_id.get_salary_grid_id(False).basic_salary
                self.lend_salary = self.basic_salary

    @api.multi
    @api.constrains('duration')
    def check_constrains(self):
        self.ensure_one()
        hr_config = self.env['hr.setting'].search([], limit=1)
        if hr_config:
            # check duration
            if self.duration > hr_config.lend_duration:
                raise ValidationError(u"لقد تم تجاوز الحد الأقصى للإعارة في المرة الواحدة.")
            # check maximum lends duration in employee's service
            old_lends = self.env['hr.employee.lend'].search([('state', '=', 'done'), ('employee_id', '=', self.employee_id.id)])
            sum_duration = self.duration
            for lend in old_lends:
                sum_duration += lend.duration
            if sum_duration > 0 and hr_config.max_lend_duration_sum <= sum_duration / 365:
                raise ValidationError(u"لقد تم تجاوز الحد الأقصى للإعارة.")
            # check duration bettween accepted lend and new one
            for lend in old_lends:
                date_to = lend.date_to
                diff = relativedelta(fields.Date.from_string(fields.Datetime.now()), fields.Date.from_string(date_to)).years
                if diff >= hr_config.periode_between_lend:
                    raise ValidationError(u"لا يمكن طلب إعارة هذا الموظف قبل إنتهاء الفترة اللازمة بين طلب أخر.")
            # ‫check completion of essay periode‬
            recruitement_decision = self.employee_id.decision_appoint_ids.search([('is_started', '=', True), ('state_appoint', '=', 'active')], limit=1)
            if recruitement_decision and recruitement_decision.depend_on_test_periode:
                testing_date_to = recruitement_decision.testing_date_to
                if fields.Date.from_string(testing_date_to) >= fields.Date.from_string(fields.Datetime.now()):
                    raise ValidationError(u"لايمكن طلب إعارة خلال فترة التجربة")
            # ‫التترقية‬ ‫سنة‬ ‫إستلكمال‬
            if self.employee_id.promotion_duration < 1:
                        raise ValidationError(u"لايمكن طلب إعارة خلال أقل من سنة منذ أخر ترقية")

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.state = 'done'
        # create history_line
        self.env['hr.employee.history'].sudo().add_action_line(self.employee_id, False, False, self._description)

    @api.multi
    def button_extend(self):
        self.ensure_one()
        context = {}
        default_date_to = fields.Date.to_string(fields.Date.from_string(self.date_to))
        context.update({
            u'default_old_date_to': default_date_to,
            u'default_new_date_to': default_date_to,

        })
        context['hr_employee_lend_id'] = self.id
        return {
            'name': u'تمديد إعارة',
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'hr.employee.lend.extend',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
        }

    @api.multi
    def action_sectioned(self):
        self.ensure_one()
        self.state = 'sectioned'


class AllowanceLendAmount(models.Model):
    _name = 'allowance.lend.amount'
    _description = u'مبالغ البدلات في الإعارة'

    lend_id = fields.Many2one('hr.employee.lend')
    allowance_id = fields.Many2one('hr.allowance.type', string=u'البدل')
    amount = fields.Float(string=u'المبلغ')


class HrEmployeeLendExtend(models.TransientModel):
    _name = 'hr.employee.lend.extend'
    _description = u'تمديد إعارة'
    _rec_name = 'old_date_to'

    old_date_to = fields.Date(string=u'تاريخ إنتهاء الإعارة القديم', readonly=1)
    new_date_to = fields.Date(string=u'تاريخ إنتهاء الإعارة الجديد')

    @api.onchange('old_date_to', 'new_date_to')
    def onchange_dates(self):
        self.ensure_one()
        if self.old_date_to and self.new_date_to:
            if self.old_date_to >= self.new_date_to:
                raise ValidationError(u"تاريخ إنتهاء الإعارة القديم يجب ان يكون أصغر من تاريخ إنتهاء الإعارة الجديد")

    @api.multi
    def action_confirm(self):
        if self.old_date_to and self.new_date_to:
            days = (fields.Date.from_string(self.new_date_to) - fields.Date.from_string(self.old_date_to)).days
            hr_config = self.env['hr.setting'].search([], limit=1)
            if hr_config:
                if days > hr_config.extend_lend_duration:
                    raise ValidationError(u"." + str(hr_config.extend_lend_duration) + u" لايمكن تمديد الإعارة أكثر من ")
                else:
                    self.env['hr.employee.lend'].search([('id', '=', self._context['hr_employee_lend_id'])]).write({'date_to': self.new_date_to})
