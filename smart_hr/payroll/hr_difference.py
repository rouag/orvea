# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from dateutil import relativedelta
import time as time_date
from datetime import datetime
from openerp.addons.smart_base.util.time_util import days_between
from docutils.nodes import line

MONTHS = [('01', 'محرّم'),
          ('02', 'صفر'),
          ('03', 'ربيع الأول'),
          ('04', 'ربيع الثاني'),
          ('05', 'جمادي الأولى'),
          ('06', 'جمادي الآخرة'),
          ('07', 'رجب'),
          ('08', 'شعبان'),
          ('09', 'رمضان'),
          ('10', 'شوال'),
          ('11', 'ذو القعدة'),
          ('12', 'ذو الحجة')]


class hrDifference(models.Model):
    _name = 'hr.difference'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'الفروقات'

    name = fields.Char(string=' المسمى', required=1, readonly=1, states={'new': [('readonly', 0)]})
    # TODO: get default MONTH
    month = fields.Selection(MONTHS, string='الشهر', required=1, readonly=1, states={'new': [('readonly', 0)]})
    date = fields.Date(string='تاريخ الإنشاء', required=1, default=fields.Datetime.now(), readonly=1, states={'new': [('readonly', 0)]})
    date_from = fields.Date('تاريخ من', default=lambda *a: time_date.strftime('%Y-%m-01'),
                            readonly=1, states={'new': [('readonly', 0)]})
    date_to = fields.Date('إلى', default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
                          readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', 'مسودة'),
                              ('waiting', 'في إنتظار الإعتماد'),
                              ('cancel', 'مرفوض'),
                              ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')
    line_ids = fields.One2many('hr.difference.line', 'difference_id', string='الفروقات', readonly=1, states={'new': [('readonly', 0)]})

    @api.onchange('month')
    def onchange_month(self):
        if self.month:
            self.name = u'فروقات شهر %s' % self.month
            line_ids = []
            # TODO: must update date_from and date_to
            # obj
            overtime_line_obj = self.env['hr.overtime.ligne']
            deputation_obj = self.env['hr.deputation']
            # delete current line
            self.line_ids.unlink()

            # 1- overtime
            overtime_setting = self.env['hr.overtime.setting'].search([], limit=1)
            # over time start in this month end finish in this month or after
            overtime_lines1 = overtime_line_obj.search([('date_from', '>=', self.date_from),
                                                       ('date_from', '<=', self.date_to),
                                                       ('overtime_id.state', '=', 'finish')])
            # over time start in last month end finish in this month  or after
            overtime_lines2 = overtime_line_obj.search([('date_from', '<', self.date_from),
                                                        ('date_to', '>=', self.date_from),
                                                       ('overtime_id.state', '=', 'finish')])
            overtime_lines = list(set(overtime_lines1 + overtime_lines2))
            print '-----overtime_lines-----------', overtime_lines
            # TODO: dont compute not work days
            for overtime in overtime_lines:
                date_from = overtime.date_from
                date_to = overtime.date_to
                if overtime.date_from < self.date_from:
                    date_from = self.date_from
                if overtime.date_to > self.date_to:
                    date_to = self.date_to
                print '----date_from, date_to-------', date_from, date_to
                number_of_days = days_between(date_from, date_to)
                number_of_hours = 0.0
                if overtime.date_from >= self.date_from and overtime.date_to <= self.date_to:
                    number_of_hours = overtime.heure_number
                # TODO: how compute amount for friday_saturday,holidays,normal_days
                employee = overtime.employee_id
                overtime_val = {'difference_id': self.id,
                                'name': overtime_setting.allowance_overtime_id.name,
                                'employee_id': employee.id,
                                'number_of_days': number_of_days,
                                'number_of_hours': number_of_hours,
                                'amount': 0.0,
                                'type': 'overtime'}
                line_ids.append(overtime_val)
                # add allowance transport
                if number_of_days:
                    # TODO:  compute amount النقل الأساسي ?
                    allowance_transport_val = {'difference_id': self.id,
                                               'name': overtime_setting.allowance_transport_id.name,
                                               'employee_id': employee.id,
                                               'number_of_days': number_of_days,
                                               'number_of_hours': 0.0,
                                               'amount': 0.0,
                                               'type': 'overtime'}
                    line_ids.append(allowance_transport_val)

            # 2- deputation
            # deputation start in this month end finish in this month or after
            deputations1 = deputation_obj.search([('date_from', '>=', self.date_from),
                                                  ('date_from', '<=', self.date_to),
                                                  ('state', '=', 'finish')])
            # deputation start in last month end finish in this month  or after
            deputations2 = deputation_obj.search([('date_from', '<', self.date_from),
                                                  ('date_to', '>=', self.date_from),
                                                  ('state', '=', 'finish')])
            deputations = list(set(deputations1 + deputations2))
            for deputation in deputations:
                date_from = deputation.date_from
                date_to = deputation.date_to
                if deputation.date_from < self.date_from:
                    date_from = self.date_from
                if deputation.date_to > self.date_to:
                    date_to = self.date_to
                number_of_days = days_between(date_from, date_to)
                # TODO: how compute amount
                employee = deputation.employee_id
                deputation_val = {'difference_id': self.id,
                                  'name': u'بدل إنتداب',
                                  'employee_id': employee.id,
                                  'number_of_days': number_of_days,
                                  'number_of_hours': 0.0,
                                  'amount': 0.0,
                                  'type': 'deputation'}
                line_ids.append(deputation_val)

            # فروقات النقل
            line_ids += self.get_difference_transfert()
            # فروقات التعين
            line_ids += self.get_difference_decision_appoint()
            # فروقات التكليف
            line_ids += self.get_difference_assign()
            # فروقات الإبتعاث
            line_ids += self.get_difference_scholarship()
            # فروقات الإعارة
            line_ids += self.get_difference_lend()
            self.line_ids = line_ids

    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_refuse(self):
        self.state = 'cancel'

    @api.multi
    def get_difference_transfert(self):
        self.ensure_one()
        line_ids = []
        hr_setting = self.env['hr.setting'].search([], limit=1)
        if hr_setting:
            transfert_ids = self.env['hr.employee.transfert'].search([('create_date', '>=', self.date_from),
                                                                      ('create_date', '<=', self.date_to),
                                                                      ('state', '=', 'done')])
            for transfert in transfert_ids:
                # get تفاصيل سلم الرواتب
                grid_id = transfert.employee_id.salary_grid_id
                if grid_id:
                    # 1- بدل طبيعة العمل
                    amount = (hr_setting.allowance_proportion * grid_id.basic_salary)
                    if amount > 0:
                        amount = amount / 100
                    vals = {'difference_id': self.id,
                            'name': hr_setting.allowance_job_nature.name,
                            'employee_id': transfert.employee_id.id,
                            'number_of_days': 0,
                            'number_of_hours': 0.0,
                            'amount': amount,
                            'type': 'transfert'}
                    line_ids.append(vals)
                    # 2- بدل إنتداب
                    amount = (hr_setting.deputation_days * (grid_id.basic_salary / 22))
                    if amount > 0:
                        amount = amount / 100
                    vals = {'difference_id': self.id,
                            'name': hr_setting.allowance_deputation.name,
                            'employee_id': transfert.employee_id.id,
                            'number_of_days': hr_setting.deputation_days,
                            'number_of_hours': 0.0,
                            'amount': amount,
                            'type': 'transfert'}
                    line_ids.append(vals)
                    # 3- بدل ترحيل
                    amount = (hr_setting.deportation_amount)
                    vals = {'difference_id': self.id,
                            'name': hr_setting.allowance_deportation.name,
                            'employee_id': transfert.employee_id.id,
                            'number_of_days': 0,
                            'number_of_hours': 0.0,
                            'amount': amount,
                            'type': 'transfert'}
                    line_ids.append(vals)
    #                 # 4- نسبة الراتب
    #                 amount = (((100 - hr_setting.salary_proportion) * grid_id.basic_salary) / 100) * -1
    #                 vals = {'difference_id': self.id,
    #                         'name': u'نسبة الراتب',
    #                         'employee_id': transfert.employee_id.id,
    #                         'number_of_days': 0,
    #                         'number_of_hours': 0.0,
    #                         'amount': amount,
    #                         'type': 'transfert'}
                    line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_decision_appoint(self):
        self.ensure_one()
        line_ids = []
        last_decision_appoint_ids = self.env['hr.decision.appoint'].search([('is_started', '=', True),
                                                                            ('state_appoint', '=', 'active'),
                                                                            ], order="date_direct_action desc")
        for last_decision_appoint_id in last_decision_appoint_ids:
            for allowance in last_decision_appoint_id.type_appointment.hr_allowance_appoint_id:
                amount = allowance.salary_number
                vals = {'difference_id': self.id,
                        'name': allowance.hr_allowance_type_id.name,
                        'employee_id': last_decision_appoint_id.employee_id.id,
                        'number_of_days': 0,
                        'number_of_hours': 0.0,
                        'amount': amount,
                        'type': 'appoint'}
                line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_assign(self):
        self.ensure_one()
        line_ids = []
        assign_ids = self.env['hr.employee.commissioning'].search([('date_to', '>=', self.date_from),
                                                                   ('date_to', '<=', self.date_to),
                                                                   ('state', '=', 'done')])
        for assign_id in assign_ids:
            # get تفاصيل سلم الرواتب
            grid_id = assign_id.employee_id.salary_grid_id
            if grid_id:
                # تفاصيل سلم الرواتب
                allowance_ids = grid_id.allowance_ids
                reward_ids = grid_id.reward_ids
                indemnity_ids = grid_id.indemnity_ids
                print 'indemnity_ids', indemnity_ids
                # راتب
                if assign_id.give_salary:
                    amount = grid_id.basic_salary
                    if amount:
                            vals = {'difference_id': self.id,
                                    'name': 'راتب',
                                    'employee_id': assign_id.employee_id.id,
                                    'number_of_days': 0,
                                    'number_of_hours': 0.0,
                                    'amount': amount * -1,
                                    'type': 'commissioning'}
                            line_ids.append(vals)
                # بدل النقل
                if assign_id.give_allowance_transport:
                    allowance_transport_id = self.env.ref('smart_hr.hr_allowance_type_01')
                    if allowance_transport_id:
                        amount = 0.0
                        for allow in allowance_ids:
                            if allow.allowance_id == allowance_transport_id:
                                amount = allow.get_value(assign_id.employee_id.id)
                                break
                        if amount:
                            vals = {'difference_id': self.id,
                                    'name': allowance_transport_id.name,
                                    'employee_id': assign_id.employee_id.id,
                                    'number_of_days': 0,
                                    'number_of_hours': 0.0,
                                    'amount': amount * -1,
                                    'type': 'commissioning'}
                            line_ids.append(vals)
                # بدلات، مكافأة أو تعويضات
                if assign_id.give_allow:
                    # بدلات
                    for allow in allowance_ids:
                        amount = allow.get_value(assign_id.employee_id.id)
                        if amount:
                            vals = {'difference_id': self.id,
                                    'name': allow.allowance_id.name,
                                    'employee_id': assign_id.employee_id.id,
                                    'number_of_days': 0,
                                    'number_of_hours': 0.0,
                                    'amount': amount * -1,
                                    'type': 'commissioning'}
                            line_ids.append(vals)
                    # مكافأة
                    for reward in reward_ids:
                        amount = reward.get_value(assign_id.employee_id.id)
                        if amount:
                            vals = {'difference_id': self.id,
                                    'name': reward.reward_id.name,
                                    'employee_id': assign_id.employee_id.id,
                                    'number_of_days': 0,
                                    'number_of_hours': 0.0,
                                    'amount': amount * -1,
                                    'type': 'commissioning'}
                            line_ids.append(vals)
                    # تعويضات
                    for indemnity in indemnity_ids:
                        amount = indemnity.get_value(assign_id.employee_id.id)
                        if amount:
                            vals = {'difference_id': self.id,
                                    'name': indemnity.indemnity_id.name,
                                    'employee_id': assign_id.employee_id.id,
                                    'number_of_days': 0,
                                    'number_of_hours': 0.0,
                                    'amount': amount * -1,
                                    'type': 'commissioning'}
                            line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_scholarship(self):
        self.ensure_one()
        line_ids = []
        scholarship_ids = self.env['hr.scholarship'].search([('date_to', '>=', self.date_from),
                                                             ('date_to', '<=', self.date_to),
                                                             ('state', '=', 'done')
                                                             ])
        for scholarship_id in scholarship_ids:
            # ابتعاث داخلي
            if scholarship_id.scholarship_type == self.env.ref('smart_hr.data_hr_shcolaship_internal'):
                # get تفاصيل سلم الرواتب
                grid_id = scholarship_id.employee_id.salary_grid_id
                if grid_id:
                    # تفاصيل سلم الرواتب
                    allowance_ids = grid_id.allowance_ids
                    # بدل النقل
                    allowance_transport_id = self.env.ref('smart_hr.hr_allowance_type_01')
                    if allowance_transport_id:
                        amount = 0.0
                        for allow in allowance_ids:
                            if allow.allowance_id == allowance_transport_id:
                                amount = allow.get_value(scholarship_id.employee_id.id)
                                break
                        if amount:
                            vals = {'difference_id': self.id,
                                    'name': allowance_transport_id.name,
                                    'employee_id': scholarship_id.employee_id.id,
                                    'number_of_days': 0,
                                    'number_of_hours': 0.0,
                                    'amount': amount * -1,
                                    'type': 'scholarship'}
                            line_ids.append(vals)
            # ابتعاث خارجي
            if scholarship_id.scholarship_type == self.env.ref('smart_hr.data_hr_shcolaship_external') and scholarship_id.duration > 365:
                grid_id = scholarship_id.employee_id.salary_grid_id
                if grid_id:
                    amount = grid_id.basic_salary
                    if amount > 0:
                        vals = {'difference_id': self.id,
                                'name': 'راتب',
                                'employee_id': scholarship_id.employee_id.id,
                                'number_of_days': 0,
                                'number_of_hours': 0.0,
                                'amount': (amount / 2) * -1,
                                'type': 'scholarship'}
                        line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_lend(self):
        self.ensure_one()
        line_ids = []
        lend_ids = self.env['hr.employee.lend'].search([('date_to', '>=', self.date_from),
                                                        ('date_to', '<=', self.date_to),
                                                        ('state', '=', 'done')
                                                        ])
        for lend_id in lend_ids:
            grid_id = lend_id.employee_id.salary_grid_id
            if grid_id:
                amount = grid_id.basic_salary
                if amount > 0:
                    vals = {'difference_id': self.id,
                            'name': 'راتب',
                            'employee_id': lend_id.employee_id.id,
                            'number_of_days': 0,
                            'number_of_hours': 0.0,
                            'amount': (amount) * -1,
                            'type': 'lend'}
                    line_ids.append(vals)
        return line_ids


class hrDifferenceLine(models.Model):
    _name = 'hr.difference.line'

    difference_id = fields.Many2one('hr.difference', string=' الفروقات', ondelete='cascade')
    name = fields.Char(string=' المسمى', required=1)
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1)
    job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True, string=' الوظيفة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True, string=' الادارة')
    amount = fields.Float(string='المبلغ')
    number_of_days = fields.Float(string='عدد الأيام')
    number_of_hours = fields.Float(string='عدد الساعات')
    month = fields.Selection(MONTHS, related='difference_id.month', store=True, readonly=True, string='الشهر')
    # TODO: do the store for state
    state = fields.Selection(related='difference_id.state', string='الحالة')
    # TODO: , النقل توظيف
    type = fields.Selection([('increase', 'علاوة'),
                             ('promotion', 'ترقية'),
                             ('scholarship', 'ابتعاث'),
                             ('appoint', 'تعيين'),
                             ('lend', 'إعارة'),
                             ('commissioning', 'تكليف'),
                             ('deputation', 'إنتداب'),
                             ('overtime', 'خارج الدوام'),
                             ('transfert', 'نقل'),
                             ('training', 'تدريب')], string='النوع', readonly=1)
