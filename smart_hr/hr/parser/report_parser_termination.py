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
from dateutil.relativedelta import relativedelta
from datetime import date
from datetime import date, datetime, timedelta

class HrTerminationRetraiteReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(HrTerminationRetraiteReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
            'get_retraite_employees':self._get_retraite_employees,
        })

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

    def _get_retraite_employees(self,date_from, date_to, is_member):
        emp_pbj = self.pool.get('hr.employee')
        data_obj = self.pool.get('ir.model.data')
        age_member = data_obj.get_object(self.cr, self.uid, 'smart_hr', 'data_hr_employee_configuration').age_member
        age_nomember =data_obj.get_object(self.cr, self.uid, 'smart_hr', 'data_hr_employee_configuration').age_nomember
        hr_member_searchs = emp_pbj.search(self.cr, self.uid, [('emp_state', '!=', 'terminated'), ('employee_state', '=', 'employee'),('is_member','=',True)])
        hr_nomember_searchs = emp_pbj.search(self.cr, self.uid, [('emp_state', '!=', 'terminated'), ('employee_state', '=', 'employee'),('is_member','=',False)])
        date_from = fields.Date.from_string(date_from)
        date_to = fields.Date.from_string(date_to)
        domain = []
        if is_member == True:
            for line in hr_member_searchs:
                birthday = emp_pbj.browse(self.cr, self.uid, line).birthday
                birthday = fields.Date.from_string(birthday)
                years_from = (date_from - birthday).days / 365
                years_to = (date_to - birthday).days / 365
                if years_from >= age_member and years_to <= age_member :
                    domain.append(line)
            return emp_pbj.browse(self.cr, self.uid, domain)
        if is_member == False :
            for rec in hr_nomember_searchs:
                birthday = emp_pbj.browse(self.cr, self.uid, rec).birthday
                birthday = fields.Date.from_string(birthday)
                years_from = (date_from - birthday).days / 365
                years_to = (date_to - birthday).days / 365
                if years_from >= age_nomember and years_to <= age_nomember :
                    domain.append(rec)
            return emp_pbj.browse(self.cr, self.uid, domain)

class ReportHrTerminationRetraiteReport(osv.AbstractModel):
    _name = 'report.smart_hr.hr_termination_retraite_reportt'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.hr_termination_retraite_reportt'
    _wrapped_report_class = HrTerminationRetraiteReport
 #  