# -*- coding: utf-8 -*-


from openerp import models, fields, api, tools, _
import openerp.addons.decimal_precision as dp
from datetime import datetime
from datetime import timedelta
MONTHS = [('1', 'محرّم'),
          ('2', 'صفر'),
          ('3', 'ربيع الأول'),
          ('4', 'ربيع الثاني'),
          ('5', 'جمادي الأولى'),
          ('6', 'جمادي الآخرة'),
          ('7', 'رجب'),
          ('8', 'شعبان'),
          ('9', 'رمضان'),
          ('10', 'شوال'),
          ('11', 'ذو القعدة'),
          ('12', 'ذو الحجة')]


class HrPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _inherit = ['hr.payslip.run', 'mail.thread']

    state = fields.Selection([('draft', 'مسودة'),
                              ('verify', 'في إنتظار الإعتماد'),
                              ('done', 'تم'),
                              ('cancel', 'ملغى'),
                              ('close', 'مغلق'),
                              ], 'الحالة', select=1, readonly=1, copy=False)

    @api.one
    def action_verify(self):
        self.state = 'verify'
        for slip in self.slip_ids:
            if slip.state == 'draft':
                slip.state = 'verify'

    @api.one
    def action_done(self):
        self.state = 'done'
        for slip in self.slip_ids:
            slip.state = 'done'

    @api.one
    def action_cancel(self):
        self.state = 'cancel'
        for slip in self.slip_ids:
            slip.state = 'cancel'


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    month = fields.Selection(MONTHS, string='الشهر', required=1)
    days_off_line_ids = fields.One2many('hr.payslip.days_off', 'payslip_id', 'الإجازات والغيابات', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'مسودة'),
                              ('verify', 'في إنتظار الإعتماد'),
                              ('done', 'تم'),
                              ('cancel', 'ملغى'),
                              ], 'الحالة', select=1, readonly=1, copy=False)

    @api.one
    def action_verify(self):
        self.state = 'verify'

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.onchange('employee_id', 'date_from', 'date_to', 'month')
    def onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return
        if not self.employee_id.payroll_structure_id:
            warning = {'title': _('تحذير!'), 'message': _(u'يجب تحديد هيكل الراتب للموظف %s' % self.employee_id.name)}
            self.employee_id = False
            return {'warning': warning}
        employee_id = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        # get name fo month
        # ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
        # tools.ustr(ttyme.strftime('%B-%Y')
        self.name = _('راتب الموظف %s للفترة : %s - %s') % (employee_id.name, date_from, date_to)
        self.company_id = employee_id.company_id
        self.struct_id = self.employee_id.payroll_structure_id
        # computation of أيام العمل
        worked_days_line_ids, leaves = self.get_worked_day_lines_without_contract(self.employee_id.id, self.employee_id.calendar_id, self.date_from, self.date_to)
        deductions = self.get_all_deduction(self.employee_id.id, self.month)
        # TODO : remove nb days deducation absence from nb worked_days
        print '-----leaves-----', leaves
        print '-----attendances-----', worked_days_line_ids
        print '-----deductions-----', deductions
        self.worked_days_line_ids = worked_days_line_ids
        self.days_off_line_ids = leaves + deductions

    def get_worked_day_lines_without_contract(self, employee_id, working_hours, date_from, date_to):
        '''
        احتساب عدد الأيام المدفوعة الأجر
        احتساب عدد أيام الإجازات
        :param employee_id:
        :param working_hours: وردية الموظف
        :param date_from:
        :param date_to:
        '''
        def employee_was_on_leave(employee_id, datetime_day, context=None):
            res = False
            day = datetime_day.strftime("%Y-%m-%d")
            # TODO: get correct state
            holiday_ids = self.env['hr.holidays'].search([('state', 'in', ('validate', 'done')),
                                                          ('employee_id', '=', employee_id),
                                                          ('type', '=', 'remove'),
                                                          ('date_from', '<=', day),
                                                          ('date_to', '>=', day)])
            if holiday_ids:
                res = holiday_ids[0].holiday_status_id.name
            return res

        leaves = {}
        attendances = {'name': _(u"عدد أيام العمل المدفوعة الأجر 100%"),
                       'sequence': 1,
                       'code': 'WORK100',
                       'number_of_days': 0.0,
                       'number_of_hours': 0.0,
                       'contract_id': False}
        day_from = datetime.strptime(date_from, "%Y-%m-%d")
        day_to = datetime.strptime(date_to, "%Y-%m-%d")
        nb_of_days = (day_to - day_from).days + 1
        for day in range(0, nb_of_days):
            working_hours_on_day = self.env['resource.calendar'].working_hours_on_day(working_hours, day_from + timedelta(days=day))
            if working_hours_on_day:
                # the employee had to work
                leave_type = employee_was_on_leave(employee_id, day_from + timedelta(days=day))
                if leave_type:
                    # if he was on leave, fill the leaves dict
                    if leave_type in leaves:
                        leaves[leave_type]['number_of_days'] += 1.0
                        leaves[leave_type]['number_of_hours'] += working_hours_on_day
                    else:
                        leaves[leave_type] = {
                            'name': leave_type,
                            'sequence': 5,
                            'code': leave_type,
                            'number_of_days': 1.0,
                            'number_of_hours': working_hours_on_day,
                            'contract_id': False,
                        }
                else:
                    # add the input vals to tmp (increment if existing)
                    attendances['number_of_days'] += 1.0
                    attendances['number_of_hours'] += working_hours_on_day
        leaves = [value for key, value in leaves.items()]
        return [attendances], leaves

    def get_all_deduction(self, employee_id, month):
        '''
        احتساب عدد الأيام الحسميات
        :param employee_id:
        :param month:
        '''
        deduction_ids = self.env['hr.deduction.line'].search([('state', '=', 'waiting'),
                                                              ('employee_id', '=', employee_id),
                                                              ('month', '=', month)])
        # deduction_type
        deductions = {}
        for deduction in deduction_ids:
            if deduction.deduction_type_id.id in deductions:
                deductions[deduction.deduction_type_id.id]['number_of_days'] += deduction.amount
            else:
                deductions[deduction.deduction_type_id.id] = {'name': deduction.deduction_type_id.name,
                                                              'sequence': 5,
                                                              'code': deduction.deduction_type_id.id,
                                                              'number_of_days': deduction.amount,
                                                              # 'number_of_hours': working_hours_on_day,you can get the working_hours_on_day only for day
                                                              }
        deductions = [value for key, value in deductions.items()]
        return deductions

    def get_all_structures_for_payslip(self, cr, uid, structure_id, context):
        structure_ids = [structure_id]
        if not structure_ids:
            return []
        return list(set(self.pool.get('hr.payroll.structure')._get_parent_structure(cr, uid, structure_ids, context=context)))

    # rewrite this function just to get a correct rules id == dont use a contract_ids
    # you find the modified lines marked by #UPDATE
    def get_payslip_lines(self, cr, uid, contract_ids, payslip_id, context):

        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
            return localdict

        class BrowsableObject(object):
            def __init__(self, pool, cr, uid, employee_id, dict):
                self.pool = pool
                self.cr = cr
                self.uid = uid
                self.employee_id = employee_id
                self.dict = dict

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                result = 0.0
                self.cr.execute("SELECT sum(amount) as sum\
                            FROM hr_payslip as hp, hr_payslip_input as pi \
                            WHERE hp.employee_id = %s AND hp.state = 'done' \
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
                           (self.employee_id, from_date, to_date, code))
                res = self.cr.fetchone()[0]
                return res or 0.0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                result = 0.0
                self.cr.execute("SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours\
                            FROM hr_payslip as hp, hr_payslip_worked_days as pi \
                            WHERE hp.employee_id = %s AND hp.state = 'done'\
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
                           (self.employee_id, from_date, to_date, code))
                return self.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                self.cr.execute("SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)\
                            FROM hr_payslip as hp, hr_payslip_line as pl \
                            WHERE hp.employee_id = %s AND hp.state = 'done' \
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s",
                            (self.employee_id, from_date, to_date, code))
                res = self.cr.fetchone()
                return res and res[0] or 0.0

        # we keep a dict with the result because a value can be overwritten by another rule with the same code
        result_dict = {}
        rules = {}
        categories_dict = {}
        blacklist = []
        payslip_obj = self.pool.get('hr.payslip')
        inputs_obj = self.pool.get('hr.payslip.worked_days')
        obj_rule = self.pool.get('hr.salary.rule')
        payslip = payslip_obj.browse(cr, uid, payslip_id, context=context)
        worked_days = {}
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days[worked_days_line.code] = worked_days_line
        inputs = {}
        for input_line in payslip.input_line_ids:
            inputs[input_line.code] = input_line

        categories_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, categories_dict)
        input_obj = InputLine(self.pool, cr, uid, payslip.employee_id.id, inputs)
        worked_days_obj = WorkedDays(self.pool, cr, uid, payslip.employee_id.id, worked_days)
        payslip_obj = Payslips(self.pool, cr, uid, payslip.employee_id.id, payslip)
        rules_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, rules)

        baselocaldict = {'categories': categories_obj, 'rules': rules_obj, 'payslip': payslip_obj, 'worked_days': worked_days_obj, 'inputs': input_obj}
        # get the ids of the structures on the contracts and their parent id as well
        # structure_ids = self.pool.get('hr.contract').get_all_structures(cr, uid, contract_ids, context=context)
        structure_ids = self.get_all_structures_for_payslip(cr, uid, payslip.struct_id.id, context=context)
        # get the rules of the structure and thier children
        rule_ids = self.pool.get('hr.payroll.structure').get_all_rules(cr, uid, structure_ids, context=context)
        # run the rules by sequence
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
        # for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context): #UPDATED
        employee = payslip.employee_id  # UPDATED contract.employee_id
        localdict = dict(baselocaldict, employee=employee, contract=False)  # UPDATED contract=contract
        for rule in obj_rule.browse(cr, uid, sorted_rule_ids, context=context):
            key = rule.code + '-' + str(payslip.employee_id.id)  # UPDATED str(contract.id)
            localdict['result'] = None
            localdict['result_qty'] = 1.0
            localdict['result_rate'] = 100
            # check if the rule can be applied
            if obj_rule.satisfy_condition(cr, uid, rule.id, localdict, context=context) and rule.id not in blacklist:
                print '---rule-----', rule.code
                # compute the amount of the rule
                amount, qty, rate = obj_rule.compute_rule(cr, uid, rule.id, localdict, context=context)
                # check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                # set/overwrite the amount computed for this rule in the localdict
                tot_rule = amount * qty * rate / 100.0
                localdict[rule.code] = tot_rule
                rules[rule.code] = rule
                # sum the amount for its salary category
                localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                # create/overwrite the rule in the temporary results
                result_dict[key] = {
                    'salary_rule_id': rule.id,
                    'contract_id': False,  # UPDATED contract.id
                    'name': rule.name,
                    'code': rule.code,
                    'category_id': rule.category_id.id,
                    'sequence': rule.sequence,
                    'appears_on_payslip': rule.appears_on_payslip,
                    'condition_select': rule.condition_select,
                    'condition_python': rule.condition_python,
                    'condition_range': rule.condition_range,
                    'condition_range_min': rule.condition_range_min,
                    'condition_range_max': rule.condition_range_max,
                    'amount_select': rule.amount_select,
                    'amount_fix': rule.amount_fix,
                    'amount_python_compute': rule.amount_python_compute,
                    'amount_percentage': rule.amount_percentage,
                    'amount_percentage_base': rule.amount_percentage_base,
                    'register_id': rule.register_id.id,
                    'amount': amount,
                    'employee_id': payslip.employee_id.id,
                    'quantity': qty,
                    'rate': rate,
                }
            else:
                # blacklist this rule and its children
                blacklist += [id for id, seq in self.pool.get('hr.salary.rule')._recursive_search_of_rules(cr, uid, [rule], context=context)]

        result = [value for code, value in result_dict.items()]
        return result


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    # make contract_id not required
    contract_id = fields.Many2one('hr.contract', 'Contract', required=False)


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    # make contract_id not required
    contract_id = fields.Many2one('hr.contract', 'Contract', required=False)


class HrPayslipDaysOff(models.Model):
    _name = 'hr.payslip.days_off'
    _description = u'أيام الإجازات والغيابات'

    name = fields.Char('الوصف', required=1)
    payslip_id = fields.Many2one('hr.payslip', 'Pay Slip', required=1, ondelete='cascade', select=1)
    code = fields.Char('الرمز', required=0)
    number_of_days = fields.Float('عدد الأيام')
    number_of_hours = fields.Float('عدد الساعات')


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    _order = 'sequence'
