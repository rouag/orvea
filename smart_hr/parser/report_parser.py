# -*- coding: utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.report import report_sxw
from openerp import fields
from dateutil.relativedelta import relativedelta
from umalqurra.hijri_date import HijriDate

class SalaryGridReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(SalaryGridReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
        })

    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.year)) + separator + str(int(hijri_date.month)) + separator + str(int(hijri_date.day))
        return None
    
class ReportSalaryGrid(osv.AbstractModel):
    _name = 'report.smart_hr.report_salary_grid'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_salary_grid'
    _wrapped_report_class = SalaryGridReport
 #  
class MedicalExamReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(MedicalExamReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
        })

    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.year)) + separator + str(int(hijri_date.month)) + separator + str(int(hijri_date.day))
        return None
    
class ReportSalaryGrid(osv.AbstractModel):
    _name = 'report.smart_hr.medical_examination_report_template'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.medical_examination_report_template'
    _wrapped_report_class = MedicalExamReport
    

class LeaveHospitalTransferReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(LeaveHospitalTransferReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
        })

    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.year)) + separator + str(int(hijri_date.month)) + separator + str(int(hijri_date.day))
        return None
    
class ReportLeaveHospitalTransfer(osv.AbstractModel):
    _name = 'report.smart_hr.leave_hospital_transfer_form_report'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.leave_hospital_transfer_form_report'
    _wrapped_report_class = LeaveHospitalTransferReport

class AssessmentProbationReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(AssessmentProbationReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
        })

    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.year)) + separator + str(int(hijri_date.month)) + separator + str(int(hijri_date.day))
        return None
    
class ReportAssessmentProbation(osv.AbstractModel):
    _name = 'report.smart_hr.hr_assessment_probation_report'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.hr_assessment_probation_report'
    _wrapped_report_class = AssessmentProbationReport
    
class HrDecisionReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(HrDecisionReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
        })

    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.year)) + separator + str(int(hijri_date.month)) + separator + str(int(hijri_date.day))
        return None
    
class ReportHrDecision(osv.AbstractModel):
    _name = 'report.smart_hr.report_hr_decision'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_hr_decision'
    _wrapped_report_class = HrDecisionReport 
    
class HrDirectAppointReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(HrDirectAppointReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
        })

    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.year)) + separator + str(int(hijri_date.month)) + separator + str(int(hijri_date.day))
        return None
    
class ReportHrDirectAppoint(osv.AbstractModel):
    _name = 'report.smart_hr.report_hr_direct_appoint'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_hr_direct_appoint'
    _wrapped_report_class = HrDirectAppointReport 
    
    
class HrEmployeeFunctionnalCardReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(HrEmployeeFunctionnalCardReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
        })

    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.year)) + separator + str(int(hijri_date.month)) + separator + str(int(hijri_date.day))
        return None
    
class ReportHrEmployeeFunctionnalCard(osv.AbstractModel):
    _name = 'report.smart_hr.hr_employee_functionnal_card_report'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.hr_employee_functionnal_card_report'
    _wrapped_report_class = HrEmployeeFunctionnalCardReport 
    
class HrEmployeeSituationOrderReport(report_sxw.rml_parse):
 
    def __init__(self, cr, uid, name, context):
        super(HrEmployeeSituationOrderReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
        })
 
    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.year)) + separator + str(int(hijri_date.month)) + separator + str(int(hijri_date.day))
        return None
     
class ReportHrEmployeeSituationOrderReportReport(osv.AbstractModel):
    _name = 'report.smart_hr.report_hr_employee_situation_order'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_hr_employee_situation_order'
    _wrapped_report_class = HrEmployeeSituationOrderReport 


class HrEmployeeCardReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(HrEmployeeCardReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
        })

    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.year)) + separator + str(int(hijri_date.month)) + separator + str(int(hijri_date.day))
        return None
    
class ReportHrEmployeeCard(osv.AbstractModel):
    _name = 'report.smart_hr.hr_employee_card_report'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.hr_employee_card_report'
    _wrapped_report_class = HrEmployeeCardReport 
    
    
    
