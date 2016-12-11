# -*- coding: utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.report import report_sxw

class MedicalExaminationReportParser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context): 
        super(MedicalExaminationReportParser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_exams_by_category': self._get_exams_by_category,
            'get_exams_category_right': self._get_exams_category_right,
            'get_exams_category_left': self._get_exams_category_left,
            'get_exams_category_bottom': self._get_exams_category_bottom,
            'get_current_date': self._get_current_date,
        })
    def _get_current_date(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")
    def _get_exams_category_right(self, exams):
        listecategories = []
        for e in exams:
            if e.exam.category not in listecategories and e.exam.category.position =='right':
                listecategories.append(e.exam.category)
        return listecategories
    def _get_exams_category_left(self, exams):
        listecategories = []
        for e in exams:
            if e.exam.category not in listecategories and e.exam.category.position =='left':
                listecategories.append(e.exam.category)
        return listecategories
    
    def _get_exams_category_bottom(self, exams):
        listecategories = []
        for e in exams:
            if e.exam.category not in listecategories and e.exam.category.position =='bottom':
                listecategories.append(e.exam.category)
        return listecategories
    
        
    def _get_exams_by_category(self, exams, category):
        res = []
        for e in exams:
            if e.exam.category == category:
                res.append(e)
        return res

class MedicalExaminationObjectReport(osv.AbstractModel):
    _name = 'report.smart_hr.medical_examination_report_template'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.medical_examination_report_template'
    _wrapped_report_class = MedicalExaminationReportParser
