# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp.report import report_sxw
from openerp import fields
from umalqurra.hijri_date import HijriDate
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from openerp.addons.smart_base.util.time_util import days_between
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri import Umalqurra

class ReportHrErrorEmployee(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ReportHrErrorEmployee, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
            'get_all_employees': self._get_all_employees,
            'get_error_employees':self._get_error_employees,
            'get_termination_employees':self._get_termination_employees,

        })

    def get_employee_ids(self,cr, uid, department_level1_id, department_level2_id, department_level3_id, salary_grid_type_id):
        dapartment_obj = self.pool.get('hr.department')
        employee_obj = self.pool.get('hr.employee')

        employee_ids = []
        dapartment_id = False
        if department_level3_id:
            dapartment_id = department_level3_id
        elif department_level2_id:
            dapartment_id = department_level2_id
        elif department_level1_id:
            dapartment_id = department_level1_id
        if dapartment_id:
            dapartment = dapartment_obj.browse(cr, uid, dapartment_id.id)
            employee_ids += [x.id for x in dapartment.member_ids]
            for child in dapartment.all_child_ids:
                employee_ids += [x.id for x in child.member_ids]
        result = {}
        if not employee_ids:
            # get all employee
            employee_ids = employee_obj.search(cr,uid,[('employee_state', '=', 'employee')])
        # filter by type
        if salary_grid_type_id:
            employee_ids = employee_obj.search(cr,uid,[('id', 'in', employee_ids), ('type_id', '=', salary_grid_type_id.id)])
        return employee_ids


    def _get_all_employees(self, month, department_level1_id, department_level2_id, department_level3_id, salary_grid_type_id):
        employee_ids = self.get_employee_ids(self.cr, self.uid, department_level1_id, department_level2_id, department_level3_id, salary_grid_type_id)
        payslip_pbj = self.pool.get('hr.payslip')
        search_ids = payslip_pbj.search(self.cr, self.uid, [('period_id','=',month.id),('salary_net','=',0.0), ('employee_id.id','in',employee_ids)])
        return payslip_pbj.browse(self.cr, self.uid, search_ids)

    def _get_error_employees(self, month, department_level1_id, department_level2_id, department_level3_id, salary_grid_type_id):
        domain = []
        employe_pbj = self.pool.get('hr.employee')
        payslip_pbj = self.pool.get('hr.payslip')
        search_empl_ids = self.get_employee_ids(self.cr, self.uid,department_level1_id, department_level2_id, department_level3_id, salary_grid_type_id)
        search_ids = []
        for rec in search_empl_ids:
            temp = payslip_pbj.search(self.cr, self.uid, [('period_id','=',month.id),('employee_id','=',rec)])
            search_ids += temp
        domain.append(search_ids)
        payslip_pbj= payslip_pbj.browse(self.cr, self.uid, search_ids)
        emp_ids = [rec.employee_id.id for rec in payslip_pbj]
        emp_ids = set(emp_ids)
        result=[]
        result = set(search_empl_ids) - emp_ids
        return employe_pbj.browse(self.cr, self.uid, list(result))


    def _get_termination_employees(self, month,department_level1_id, department_level2_id, department_level3_id, salary_grid_type_id):
        date_from = get_hijri_month_start(HijriDate, Umalqurra,month)
        date_to = get_hijri_month_end(HijriDate, Umalqurra,month)
        emp_pbj = self.pool.get('hr.employee')
        domain = []
        termination_pbj = self.pool.get('hr.termination')
        empl_ids = self.get_employee_ids(self.cr, self.uid,department_level1_id, department_level2_id, department_level3_id, salary_grid_type_id)
        search_empl_ids = termination_pbj.search(self.cr, self.uid, [('state','=','done'),('employee_id', 'in',empl_ids),('date_termination', '>', date_from),('date_termination', '<', date_to)])
        emp_ids = [rec.employee_id.id for rec in search_empl_ids]
        return emp_pbj.browse(self.cr, self.uid, emp_ids)


    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.day)).zfill(2) + separator + str(int(hijri_date.month)).zfill(2) + separator + str(int(hijri_date.year))
        return None


class HrErrorEmployeeReport(osv.AbstractModel):
    _name = 'report.smart_hr.report_hr_error_employee'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_hr_error_employee'
    _wrapped_report_class = ReportHrErrorEmployee