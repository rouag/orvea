# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import time as time_date
from datetime import datetime
from openerp.addons.smart_base.util.time_util import days_between
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra


class HrDifferential(models.Model):
    _name = 'hr.differential'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'الفروقات'

    @api.multi
    def get_default_period_id(self):
        month = get_current_month_hijri(HijriDate)
        date = get_hijri_month_start(HijriDate, Umalqurra, int(month))
        period_id = self.env['hr.period'].search([('date_start', '<=', date),
                                                  ('date_stop', '>=', date),
                                                  ]
                                                 )
        return period_id

    name = fields.Char(default="الفروقات")
    period_id = fields.Many2one('hr.period', string=u'الفترة', domain=[('is_open', '=', True)], default=get_default_period_id, required=1, readonly=1, states={'new': [('readonly', 0)]})
    date = fields.Date(string='تاريخ الإنشاء', required=1, default=fields.Datetime.now(), readonly=1)
    state = fields.Selection([('new', 'إعداد'),
                              ('waiting', 'في إنتظار الإعتماد'),
                              ('cancel', 'مرفوض'),
                              ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')
    action_type = fields.Selection([('promotion', 'ترقية'),
                                    ('decision_appoint', 'تعيين'),
                                    ('tranfert', 'نقل'),
                                    ('improve_condition', 'تحسين وضع')
                                    ], string=' نوع الإجراء', readonly=1, required=1, default='promotion', states={'new': [('readonly', 0)]})
    line_ids = fields.One2many('hr.differential.line', 'difference_id', string='الفروقات', readonly=1, states={'new': [('readonly', 0)]})
    department_level1_id = fields.Many2one('hr.department', string='الفرع', readonly=1, states={'new': [('readonly', 0)]})
    department_level2_id = fields.Many2one('hr.department', string='القسم', readonly=1, states={'new': [('readonly', 0)]})
    department_level3_id = fields.Many2one('hr.department', string='الشعبة', readonly=1, states={'new': [('readonly', 0)]})
    salary_grid_type_id = fields.Many2one('salary.grid.type', string='الصنف', readonly=1, states={'new': [('readonly', 0)]},)
    employee_ids = fields.Many2many('hr.employee', string='الموظفين', readonly=1, states={'new': [('readonly', 0)]})

    @api.onchange('department_level1_id', 'department_level2_id', 'department_level3_id', 'salary_grid_type_id')
    def onchange_department_level(self):
        dapartment_obj = self.env['hr.department']
        employee_obj = self.env['hr.employee']
        department_level1_id = self.department_level1_id and self.department_level1_id.id or False
        department_level2_id = self.department_level2_id and self.department_level2_id.id or False
        department_level3_id = self.department_level3_id and self.department_level3_id.id or False
        employee_ids = []
        dapartment_id = False
        if department_level3_id:
            dapartment_id = department_level3_id
        elif department_level2_id:
            dapartment_id = department_level2_id
        elif department_level1_id:
            dapartment_id = department_level1_id
        if dapartment_id:
            dapartment = dapartment_obj.browse(dapartment_id)
            employee_ids += [x.id for x in dapartment.member_ids]
            for child in dapartment.all_child_ids:
                employee_ids += [x.id for x in child.member_ids]
        result = {}
        if not employee_ids:
            # get all employee
            employee_ids = employee_obj.search([('employee_state', '=', 'employee')]).ids
        # filter by type
        if self.salary_grid_type_id:
            employee_ids = employee_obj.search([('id', 'in', employee_ids), ('type_id', '=', self.salary_grid_type_id.id)]).ids
        result.update({'domain': {'employee_ids': [('id', 'in', list(set(employee_ids)))]}})
        return result

    @api.multi
    def compute_differences(self):
        self.line_ids.unlink()
        line_ids = []
        decision_appoint_obj = self.env['hr.decision.appoint']
        # تقسيم فترة الفرق الفترات شهرية
        for employee_id in self.employee_ids:
            # check  if there is a promotion demand for current employee
            # الترقية
            if self.action_type == 'promotion':
                record_id = self.env['hr.promotion.employee.job'].search([('employee_id', '=', employee_id.id),
                                                                          ('defferential_is_paied', '=', False),
                                                                          ('state', '=', 'done')], limit=1)
                if record_id:
                    # must search the  linked appoint for this promotion
                    appoint_promotion = decision_appoint_obj.search([('promotion_id', '=', record_id.id)], limit=1)
                    if appoint_promotion:
                        date_start = appoint_promotion.date_hiring
                        date_stop = appoint_promotion.date_direct_action
                    else:
                        record_id = False

            # التعيين
            if self.action_type == 'decision_appoint':
                record_id = decision_appoint_obj.search([('is_started', '=', True),
                                                                    ('state_appoint', '=', 'active'),
                                                                    ('employee_id', '=', employee_id.id),
                                                                    ('defferential_is_paied', '=', False),
                                                                    ], order="date_direct_action desc", limit=1)
                if record_id:
                    date_start = record_id.date_hiring
                    date_stop = record_id.date_direct_action
            # النقل
            if self.action_type == 'transfert':
                record_id = self.env['hr.employee.transfert'].search([('state', '=', 'done'),
                                                                      ('employee_id', '=', employee_id.id),
                                                                      ('defferential_is_paied', '=', False),
                                                                      ], limit=1)
                if record_id:
                    # must search the  linked appoint for this transfert
                    appoint_transfert = decision_appoint_obj.search([('transfer_id', '=', record_id.id)], limit=1)
                    if appoint_transfert:
                        date_start = appoint_transfert.date_hiring
                        date_stop = appoint_transfert.date_direct_action
                    else:
                        record_id = False

            # تحسين وضع
            if self.action_type == 'improve_condition':
                record_id = self.env['hr.improve.situation'].search([('state', '=', 'done'),
                                                                     ('employee_id', '=', employee_id.id),
                                                                     ('defferential_is_paied', '=', False),
                                                                     ], limit=1)
                if record_id:
                    # must search the  linked appoint for this improve_condition
                    appoint_improve = decision_appoint_obj.search([('improve_id', '=', record_id.id)], limit=1)
                    if appoint_improve:
                        date_start = appoint_improve.date_hiring
                        date_stop = appoint_improve.date_direct_action
                    else:
                        record_id = False

            if record_id and date_stop > date_start:
                vals = {'difference_id': self.id,
                        'employee_id': employee_id.id,
                        'date_start': date_start,
                        'date_stop': date_stop,
                        'model_name': record_id._name,
                        'object_id': record_id.id,
                        }
                line_ids.append(vals)
            self.line_ids = line_ids
        # generate periodes for each line
        for rec in self.line_ids:
            rec.generate_periodes()

    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.multi
    def action_done(self):
        self.state = 'done'
        for line in self.line_ids:
            self.env[line.model_name].search([('id', '=', line.object_id)], limit=1).write({'defferential_is_paied': True})

    @api.one
    def button_refuse(self):
        self.state = 'cancel'

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'new':
                raise ValidationError(u"لا يمكن حذف الفروقات إلا في حالة مسودة أو ملغاه! ")
            super(HrDifferential, rec).unlink()


class HrDifferentialLine(models.Model):
    _name = 'hr.differential.line'
    
    difference_id = fields.Many2one('hr.differential', string=' الفروقات', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='الموظف')
    date_start = fields.Date('تاريخ من')
    date_stop = fields.Date('إلى')
    basic_salary_amount = fields.Float(string='فرق الراتب  الأساسي')
    retirement_amount = fields.Float(string='فرق التقاعد')
    allowance_amount = fields.Float(string='فرق البدلات')
    total_amount = fields.Float(string='المجموع')
    defferential_detail_ids = fields.One2many('hr.differential.detail', 'difference_line_id')
    line_allowance_ids = fields.One2many('hr.differential.line.allowance', 'line_id', string='البدلات')
    model_name = fields.Char('model name')
    object_id = fields.Integer('Object name')

    @api.multi
    def generate_periodes(self):
        for rec in self:
            line_ids = []
            period_id = False
            ds = datetime.strptime(rec.date_start, '%Y-%m-%d')
            while ds.strftime('%Y-%m-%d') < rec.date_stop:
                hijri_month = get_hijri_month_by_date(HijriDate, Umalqurra, ds)
                hijri_year = get_hijri_year_by_date(HijriDate, Umalqurra, ds)
                date_start = get_hijri_month_start_by_year(HijriDate, Umalqurra, hijri_year, hijri_month)
                date_stop = get_hijri_month_end__by_year(HijriDate, Umalqurra, hijri_year, hijri_month)
                period_id = self.env['hr.period'].search([('date_start', '=', date_start),
                                                          ('date_stop', '=', date_stop)])

                d_start, d_stop = self.env['hr.smart.utils'].get_overlapped_periode(date_start, date_stop, rec.date_start, rec.date_stop)

                number_of_days = (d_stop - d_start).days + 1

                ds = ds + relativedelta(days=number_of_days)
                # get difference of basic salary for all periode
                basic_salary_amount, retirement_amount, allowance_amount = self.get_differences(number_of_days)
                total_amount = basic_salary_amount + retirement_amount + allowance_amount
                if total_amount != 0:
                    vals = {'difference_line_id': rec.id,
                            'period_id': period_id.id,
                            'number_of_days': number_of_days,
                            'basic_salary_amount': basic_salary_amount,
                            'retirement_amount': retirement_amount,
                            'allowance_amount': allowance_amount,
                            'total_amount': total_amount,
                            }
                    line_ids.append(vals)
                # calculate total_amout, basic_salary_amount + retirement_amount + allowance_amount for this hr.differential.line
                self.basic_salary_amount += basic_salary_amount
                self.retirement_amount += retirement_amount
                self.allowance_amount += allowance_amount
                self.total_amount += total_amount
            rec.defferential_detail_ids = line_ids

    @api.multi
    def get_differences(self, number_of_days):
        """
        @param: number of days to calculate the differences
        @return: differences for basic_salary, retirement, allowances
        """
        self.ensure_one()
        line_allowance_ids = []
        # get salary_grid_id the day of the acceptation of the promotion
        new_salary_grid_id, new_basic_salary = self.employee_id.get_salary_grid_id(self.date_stop)
        # get salary_grid_id before the acceptation of the promotion
        old_salary_grid_id, old_basic_salary = self.employee_id.get_salary_grid_id(self.date_start)
        basic_salary_amount = (new_basic_salary - old_basic_salary) / 30.0 * number_of_days
        # calculate the difference of retirement
        new_retirement_amount = (new_basic_salary * new_salary_grid_id.retirement) / 100.0
        old_retirement_amount = (old_basic_salary * old_salary_grid_id.retirement) / 100.0
        retirement_amount = (new_retirement_amount - old_retirement_amount) / 30.0 * number_of_days * -1.0
        # calculate the difference of allowances
        # step 1: job + aride zones allowances
        new_hr_employee_allowance_ids = self.employee_id.get_employee_allowances(new_salary_grid_id.date)
        old_hr_employee_allowance_ids = self.employee_id.get_employee_allowances(old_salary_grid_id.date)
        allowance_amount = 0.0
        for new_elt in new_hr_employee_allowance_ids:
            find = False
            for old_elt in old_hr_employee_allowance_ids:
                if new_elt['allowance_id'] == old_elt['allowance_id']:
                    #  it's a old allowance
                    amount = (new_elt['amount'] - old_elt['amount']) / 30.0 * number_of_days
                    allowance_amount += amount
                    line_allowance_ids.append({'line_id': self.id,
                                               'allowance_id': new_elt['allowance_id'],
                                               'amount': amount
                                               })
                    find = True
                    break
            if not find:
                #  it's a new allowance
                amount = new_elt['amount'] / 30.0 * number_of_days
                line_allowance_ids.append({'line_id': self.id,
                                           'allowance_id': new_elt['allowance_id'],
                                           'amount': amount
                                           })
                allowance_amount += amount
        self.line_allowance_ids = line_allowance_ids
        return basic_salary_amount, retirement_amount, allowance_amount


class HrDifferentialLineAllowance(models.Model):
    _name = 'hr.differential.line.allowance'

    line_id = fields.Many2one('hr.differential.line', ondelete='cascade')
    allowance_id = fields.Many2one('hr.allowance.type', string='البدل', required=1)
    amount = fields.Float(string='المبلغ')


class HrDifferentialDetail(models.Model):
    _name = 'hr.differential.detail'
    _description = 'فترات الفرق'

    difference_line_id = fields.Many2one('hr.differential.line', string='الفرق', ondelete='cascade')
    period_id = fields.Many2one('hr.period', string=u'الفترة')
    number_of_days = fields.Integer(string='عدد الأيام')
    basic_salary_amount = fields.Float(string='فرق الراتب  الأساسي')
    retirement_amount = fields.Float(string='فرق التقاعد')
    allowance_amount = fields.Float(string='فرق البدلات')
    total_amount = fields.Float(string='المجموع')

