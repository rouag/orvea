# -*- coding: utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.report import report_sxw
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class OrderEnquiryReportParser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context): 
        super(OrderEnquiryReportParser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_current_date': self._get_current_date,
            'get_order_sequence': self._get_order_sequence,
            'reverse_identification_id':self.get_reverse_identification_id,
            'is_governmental_employee': self._is_governmental_employee,
            'get_employee_jurdicial_precedents': self._get_employee_jurdicial_precedents,
        })
        
    def _get_employee_jurdicial_precedents(self, employee):
        jurdicial_precedents_ids = self.pool.get('employee.judicial.precedents').search(self.cr, self.uid, [('employee','=',employee.id)], limit=1)
        if jurdicial_precedents_ids:
            jurdicial_precedents_obj = self.pool.get('employee.judicial.precedents').browse(self.cr, self.uid,jurdicial_precedents_ids)
            print jurdicial_precedents_obj.judicial_precedents
            return jurdicial_precedents_obj.judicial_precedents
    
    def _get_current_date(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")
    
    def _is_governmental_employee(self, emprecruiter):
        governmentalrecruiter = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'smart_hr', 'governmental')[1]
        return emprecruiter.id == governmentalrecruiter
    
    def get_reverse_identification_id(self,identification_id):
        return identification_id[::-1]
    
    def _get_order_sequence(self):
        sequence = self.pool.get('ir.sequence').next_by_code(self.cr, self.uid, 'seq.employee.judicial.precedents.ordre')
        return sequence
class OrderEnquiryObjectReport(models.AbstractModel):
    _name = 'report.smart_hr.order_enquiry_report_template'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.order_enquiry_report_template'
    _wrapped_report_class = OrderEnquiryReportParser
