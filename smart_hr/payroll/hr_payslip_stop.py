# -*- coding: utf-8 -*-


from openerp import models, fields, api, tools, _
import openerp.addons.decimal_precision as dp
from datetime import datetime
from datetime import timedelta
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra
from tempfile import TemporaryFile
import base64
from openerp.exceptions import UserError
from openerp.exceptions import ValidationError
from pychart.arrow import default


class HrPayslipStop(models.Model):
    _name = 'hr.payslip.stop'
    _inherit = ['mail.thread']

    name = fields.Char(string='رقم القرار', required=1, readonly=1, states={'draft': [('readonly', 0)]})
    order_date = fields.Date(string='تاريخ القرار',required=1, default=fields.Datetime.now(), readonly=1, states={'draft': [('readonly', 0)]})
    date = fields.Date(string='التاريخ' , default=fields.Datetime.now(), readonly=1, states={'draft': [('readonly', 0)]})
    payslip_file = fields.Binary(string = 'صورة القرار' , readonly=1, states={'draft': [('readonly', 0)]})
    payslip_file_name = fields.Char(string = 'صورة القرار' ,  readonly=1, states={'draft': [('readonly', 0)]})
    period_ids = fields.One2many('hr.payslip.stop.line','payslip_id',  string='الفترات' ,readonly=1, states={'draft': [('readonly', 0)]})
    employee_id = fields.Many2one('hr.employee', string='الموظف',required=1, readonly=1, states={'draft': [('readonly', 0)]})
    state = fields.Selection([('draft', '  إعداد'),
                              ('waiting', u'في إنتظار الاعتماد'),
                              ('done', u'اعتمدت'),
                              ('refused', u'ملغى'),
                              ], string='الحالة', readonly=1, default='draft')
    @api.multi
    def action_draft(self):
        for rec in self:
            rec.state = 'waiting'

    @api.multi
    def button_refuse(self):
        for rec in self:
            for line in rec.period_ids:
                line.period_ids.stop_period = False
            rec.state = 'refused'

    @api.multi
    def action_waiting(self):
        for rec in self:
            rec.state = 'done'




class HrPayslipStopLine(models.Model):
    _name = 'hr.payslip.stop.line'
   
    @api.multi
    def get_default_period_id(self):
        month = get_current_month_hijri(HijriDate)
        date = get_hijri_month_start(HijriDate, Umalqurra, int(month))
        period_id = self.env['hr.period'].search([('date_start', '<=', date),
                                                       ('date_stop', '>=', date),
                                                       ]
                                                      )
        return period_id

    payslip_id = fields.Many2one('hr.payslip.stop', string=u'الفترات',)
    stop_period = fields.Boolean(string='إيقاف', default=True)
    period_id = fields.Many2one('hr.period', string=u'الفترات')
    state = fields.Selection(related='payslip_id.state')

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.stop_period = False


class HrPayslipStopRun(models.Model):
    _name = 'hr.payslip.stop.run'
    _inherit = ['mail.thread']

    name = fields.Char(string='رقم القرار', required=1, readonly=1, states={'draft': [('readonly', 0)]})
    order_date = fields.Date(string='تاريخ القرار', default=fields.Datetime.now())
    payslip_file = fields.Binary(string='صورة القرار', states={'draft': [('readonly', 0)]})
    payslip_file_name = fields.Char(string = 'صورة القرار' , states={'draft': [('readonly', 0)]})
    date = fields.Date(string='التاريخ' , default=fields.Datetime.now(), states={'draft': [('readonly', 0)]})
    period_ids = fields.Many2many('hr.period',  domain=[('is_open', '=', True)],string='الفترات',  states={'draft': [('readonly', 0)]})
    employee_ids = fields.Many2many('hr.employee', string='الموظفين', readonly=1, states={'draft': [('readonly', 0)]})
    department_level1_id = fields.Many2one('hr.department', string='الفرع', readonly=1, states={'draft': [('readonly', 0)]})
    department_level2_id = fields.Many2one('hr.department', string='القسم', readonly=1, states={'draft': [('readonly', 0)]})
    department_level3_id = fields.Many2one('hr.department', string='الشعبة', readonly=1, states={'draft': [('readonly', 0)]})
    salary_grid_type_id = fields.Many2one('salary.grid.type', string='الصنف', readonly=1, states={'draft': [('readonly', 0)]},)
    state = fields.Selection([('draft', '  إعداد'),
                              ('waiting', u'في إنتظار الاعتماد'),
                              ('done', u'اعتمدت'),
                              ('refused', u'ملغى'),
                              ], string='الحالة', readonly=1, default='draft')
    @api.multi
    def action_waiting(self):
        for rec in self:
            payslip_stop_obj = self.env['hr.payslip.stop']
            for employee in rec.employee_ids:
                payslip_stop_val = {'employee_id': employee.id,
                                    'name':rec.name,
                                    'period_ids':rec.period_ids,
                                    'state':'done',
                           }
                lines = []
                payslip = payslip_stop_obj.create(payslip_stop_val)
                for  temp in rec.period_ids :
                    period_ids = {
                              'period_id': temp.id,
                              'stop_period':True,
                              }
                    lines.append(period_ids)
                payslip.period_ids = lines
            rec.state = 'done'

    @api.multi
    def button_refuse(self):
        for rec in self:
            
            for employee in rec.employee_ids:
                payslip_stop_obj = self.env['hr.payslip.stop']
                payslip_stop = payslip_stop_obj.search([('employee_id', '=', employee.id), ('name', '=', rec.name),('order_date','=',rec.order_date)])
                if payslip_stop :
                    for line in payslip_stop.period_ids:
                        print"eee"
                        line.stop_period =False,
                    payslip_stop.state ='refused'
            rec.state = 'refused'

    @api.multi
    def action_draft(self):
        for rec in self:
            rec.state = 'waiting'
    
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
  