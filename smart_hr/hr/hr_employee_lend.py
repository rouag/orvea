# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError


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
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1, readonly=1,
                                  states={'new': [('readonly', 0)]})
    insurance_entity = fields.Many2one('res.partner', string=u'الجهة المعار إليها', domain=[('insurance', '=', True)],
                                       required=1, readonly=1, states={'new': [('readonly', 0)]})
    decision_number = fields.Char(string=u"رقم القرار", readonly=1, states={'new': [('readonly', 0)]})
    decision_date = fields.Date(string=u'تاريخ القرار', readonly=1, states={'new': [('readonly', 0)]})
    decision_file = fields.Binary(string=u'نسخة القرار', readonly=1, states={'new': [('readonly', 0)]}, attachment=True)
    date_from = fields.Date(string=u'التاريخ من ', default=fields.Datetime.now(), readonly=1,
                            states={'new': [('readonly', 0)]})
    date_to = fields.Date(string=u'التاريخ الى', compute='_compute_date_to', store=True)
    duration = fields.Integer(string=u'الأيام', required=1, readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', u'طلب'),
                              ('done', u'اعتمدت'),
                              ('sectioned', u'مقطوعة')
                              ], readonly=1, default='new', string=u'الحالة')
    decision_file_name = fields.Char()
    allowance_ids = fields.One2many('allowance.lend.amount', 'lend_id', string=u'البدلات التي تتحملها الجهة',
                                    readonly=1, states={'new': [('readonly', 0)]})
    salary_proportion = fields.Float(string=u'نسبة الراتب التي تتحملها الجهة', default=100.0, readonly=1,
                                     states={'new': [('readonly', 0)]})
    basic_salary = fields.Float(string=u'الراتب الأساسي', readonly=1)
    lend_salary = fields.Float(string=u'الراتب في الإعارة', readonly=1, states={'new': [('readonly', 0)]})
    pay_retirement = fields.Boolean(string=u'يتحمل  الموظف الحسميات التقاعدية كاملة', readonly=1,
                                    states={'new': [('readonly', 0)]})
    done_date = fields.Date(string='تاريخ التفعيل')
    decission_id = fields.Many2one('hr.decision', string=u'القرارات')
    employee_lend_type = fields.Many2one('hr.employee.lend.ligne', required=1, string=u'نوع الإعارة')
    history_ids = fields.One2many('hr.employee.lend.history', 'lend_history_id', string=u'سجل الإجراءت', readonly=1,
                                  states={'new': [('readonly', 0)]})

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
            salary_grid_id, basic_salary = self.employee_id.get_salary_grid_id(False)
            if basic_salary:
                self.basic_salary = basic_salary
                self.lend_salary = basic_salary

    @api.multi
    @api.constrains('duration')
    def check_constrains(self):
        self.ensure_one()
        hr_config = self.env['hr.setting'].search([], limit=1)
        if self.employee_lend_type:
            # check duration
            if self.duration > self.employee_lend_type.lend_duration:
                raise ValidationError(u"لقد تم تجاوز الحد الأقصى للإعارة في المرة الواحدة.")
            # check maximum lends duration in employee's service
            old_lends = self.env['hr.employee.lend'].search(
                [('state', '=', 'done'), ('employee_id', '=', self.employee_id.id)])
            sum_duration = self.duration
            for lend in old_lends:
                sum_duration += lend.duration
            if sum_duration > 0 and self.employee_lend_type.max_lend_duration_sum <= sum_duration / 354:
                raise ValidationError(u"لقد تم تجاوز الحد الأقصى للإعارة.")
            # check duration bettween accepted lend and new one
            for lend in old_lends:
                date_to = lend.date_to
                diff = relativedelta(fields.Date.from_string(fields.Datetime.now()),
                                     fields.Date.from_string(date_to)).years
                if diff >= self.employee_lend_type.periode_between_lend:
                    raise ValidationError(u"لا يمكن طلب إعارة هذا الموظف قبل إنتهاء الفترة اللازمة بين طلب أخر.")
            # ‫check completion of essay periode‬
            recruitement_decision = self.employee_id.decision_appoint_ids.search(
                [('is_started', '=', True), ('state_appoint', '=', 'active')], limit=1)
            if recruitement_decision and recruitement_decision.depend_on_test_periode:
                testing_date_to = recruitement_decision.testing_date_to
                if fields.Date.from_string(testing_date_to) >= fields.Date.from_string(fields.Datetime.now()):
                    raise ValidationError(u"لايمكن طلب إعارة خلال فترة التجربة")
                    # ‫التترقية‬ ‫سنة‬ ‫إستلكمال‬
                #             if self.employee_id.promotion_duration < 354:
                #                 raise ValidationError(u"لايمكن طلب إعارة خلال أقل من سنة منذ أخر ترقية")

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'new':
                raise ValidationError(u'لا يمكن حذف طلب  إعارة فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(HrEmployeeLend, self).unlink()

    @api.multi
    def open_decission_employee_lend(self):
        decision_obj = self.env['hr.decision']
        if self.decission_id:
            decission_id = self.decission_id.id
        else:
            decision_type_id = 1
            decision_date = fields.Date.today()  # new date
            if self.employee_id:
                decision_type_id = self.env.ref('smart_hr.data_employee_lend').id
            # create decission
            decission_val = {
                'name': self.env['ir.sequence'].get('hr.employee.lend.seq'),
                'decision_type_id': decision_type_id,
                'date': decision_date,
                'employee_id': self.employee_id.id}
            decision = decision_obj.create(decission_val)
            decision.text = decision.replace_text(self.employee_id, decision_date, decision_type_id, 'employee')
            decission_id = decision.id
            self.decission_id = decission_id
        return {
            'name': _(u'قرار  إعارة'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.decision',
            'view_id': self.env.ref('smart_hr.hr_decision_wizard_form').id,
            'type': 'ir.actions.act_window',
            'res_id': decission_id,
            'target': 'new'
        }

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.done_date = fields.Date.today()
        self.state = 'done'
        if self.insurance_entity.company_type != 'inter_reg_org':
            self.employee_id.promotion_duration -= self.duration
            self.employee_id.service_duration -= self.duration

    @api.multi
    def button_extend(self):
        self.ensure_one()
        context = {}
        default_date_to = fields.Date.to_string(fields.Date.from_string(self.date_to))
        context.update({
            u'default_old_date_to': default_date_to,
            #  u'default_new_date_to': default_date_to,

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
        context = {}
        default_date_to = fields.Date.to_string(fields.Date.from_string(self.date_to))
        context.update({
            u'default_old_date_to': default_date_to,
            #  u'default_new_date_to': default_date_to,

        })
        context['hr_employee_lend_id'] = self.id
        return {
            'name': u'قطع إعارة',
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'hr.employee.lend.cancel',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
        }


class AllowanceLendAmount(models.Model):
    _name = 'allowance.lend.amount'
    _description = u'مبالغ البدلات في الإعارة'

    lend_id = fields.Many2one('hr.employee.lend')
    allowance_id = fields.Many2one('hr.allowance.type', string=u'البدل')
    amount = fields.Float(string=u'المبلغ')


class HrEmployeeLendLigne(models.Model):
    _name = 'hr.employee.lend.ligne'
    _description = u'أنواع  الإعارة'

    # الإعارة
    name = fields.Char(string=u'المسمى', required=1)
    lend_duration = fields.Integer(string=u'مدة الإعارة (باليوم)', default=354)
    one_max_lend_duration = fields.Integer(string=u'الحد الأقصى للتمديد في المرة (بالأيام)', default=354)
    max_lend_duration_sum = fields.Integer(string=u'الحد الأقصى لمجموع الاعارات (باليوم)', default=354)
    lend_number = fields.Integer(string=u'عدد مرات التمديد', default=3)
    periode_between_lend = fields.Integer(string=u'المدة بين إعارتين (بالسنة)', default=3)
    extend_lend_duration = fields.Integer(string=u'مدة تمديد الإعارة (باليوم)', default=354)
    grade_ids = fields.Many2many('salary.grid.grade', string='المراتب')

    @api.multi
    def button_setting(self):
        hr_setting = self.env['hr.employee.lend.ligne'].search([], limit=1)
        if hr_setting:
            value = {
                'name': u'‫إعدادات  الإعارة ',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.employee.lend.ligne',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': hr_setting.id,
            }
            return value


class HrEmployeeLendcancel(models.TransientModel):
    _name = 'hr.employee.lend.cancel'
    _description = u'قطع إعارة'
    _rec_name = 'old_date_to'

    old_date_to = fields.Date(string=u'تاريخ إنتهاء الإعارة ', readonly=1)
    new_date_to = fields.Date(string=u'تاريخ قطع الإعارة ', default=fields.Datetime.now())
    employee_lend_id = fields.Many2one('hr.employee.lend')
    employee_lend_type = fields.Many2one('hr.employee.lend.ligne', related='employee_lend_id.employee_lend_type',
                                         string=u'نوع الإعارة')
    decision_number = fields.Char(string=u"رقم القرار", required=1)
    decision_date = fields.Date(string=u'تاريخ القرار', required=1)
    decision_file = fields.Binary(string=u'نسخة القرار')
    decision_file_name = fields.Char(string=u'نسخة القرار')

    @api.multi
    def action_confirm(self):
        lend_line = self._context.get('active_id', False)
        lend_line_obj = self.env['hr.employee.lend']
        lend_id = lend_line_obj.search([('id', '=', lend_line)])
        if self.new_date_to and lend_id:
            if self.old_date_to <= self.new_date_to:
                raise ValidationError(u"تاريخ قطع الإعارة  يجب ان يكون أصغر من تاريخ إنتهاء الإعارة ")
            lend_id.date_to = self.new_date_to
            val = {
                'action': u'قطع إعارة',
                'lend_history_id': lend_id.id,
                'name': self.decision_number,
                'employee_id': lend_id.employee_id.id,
                'decision_date': self.decision_date,
            }
            self.env['hr.employee.lend.history'].create(val)
            lend_id.state = 'sectioned'


class HrEmployeeLendExtend(models.TransientModel):
    _name = 'hr.employee.lend.extend'
    _description = u'تمديد إعارة'
    _rec_name = 'old_date_to'

    old_date_to = fields.Date(string=u'تاريخ إنتهاء الإعارة القديم', readonly=1)
    new_date_to = fields.Date(string=u'تاريخ إنتهاء الإعارة الجديد')
    employee_lend_id = fields.Many2one('hr.employee.lend')
    employee_lend_type = fields.Many2one('hr.employee.lend.ligne', related='employee_lend_id.employee_lend_type',
                                         string=u'نوع الإعارة')
    decision_number = fields.Char(string=u"رقم القرار", required=1)
    decision_date = fields.Date(string=u'تاريخ القرار', required=1)
    decision_file = fields.Binary(string=u'نسخة القرار')
    decision_file_name = fields.Char(string=u'نسخة القرار')

    @api.onchange('new_date_to')
    def onchange_dates(self):
        self.ensure_one()
        if self.old_date_to and self.new_date_to:
            if self.old_date_to >= self.new_date_to:
                raise ValidationError(u"تاريخ إنتهاء الإعارة القديم يجب ان يكون أصغر من تاريخ إنتهاء الإعارة الجديد")

    @api.multi
    def action_confirm(self):
        lend_line = self._context.get('active_id', False)
        lend_line_obj = self.env['hr.employee.lend']
        lend_id = lend_line_obj.search([('id', '=', lend_line)])
        if self.new_date_to and lend_id:
            if self.old_date_to >= self.new_date_to:
                raise ValidationError(u"تاريخ إنتهاء الإعارة القديم يجب ان يكون أصغر من تاريخ إنتهاء الإعارة الجديد")
            days = (fields.Date.from_string(self.new_date_to) - fields.Date.from_string(self.old_date_to)).days
            if days > lend_id.employee_lend_type.extend_lend_duration:
                raise ValidationError(
                    u"." + str(lend_id.employee_lend_type.extend_lend_duration) + u" لايمكن تمديد الإعارة أكثر من ")
            else:
                lend_id.date_to = self.new_date_to
                val = {
                    'action': u'تمديد إعارة',
                    'lend_history_id': lend_id.id,
                    'name': self.decision_number,
                    'employee_id': lend_id.employee_id.id,
                    'decision_date': self.decision_date,
                }
                self.env['hr.employee.lend.history'].create(val)


class hrEmployeeLendHistory(models.Model):
    _name = 'hr.employee.lend.history'

    name = fields.Char(string='رقم القرار')
    lend_history_id = fields.Many2one('hr.employee.lend', string=' الإعارة', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string=' الموظف')
    action = fields.Char(string='الإجراء')
    decision_date = fields.Date(string='تاريخ القرار')
