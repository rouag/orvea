# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, tools 
from openerp import api, fields, models, _
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrEmployeeTransfertWizard(models.TransientModel):
    _name = 'wizard.employee.transfert'



    new_job_id = fields.Many2one('hr.job', domain=[('state','=', 'unoccupied')], string=u'الوظيفة المنقول إليها')
    degree_id = fields.Many2one('salary.grid.degree', related='employee_id.degree_id', string=u'الدرجة' ,readonly=1) 
    hr_employee_transfert_id = fields.Many2one('hr.employee.transfert', string=u'طلب نقل موظف')
    new_degree_id = fields.Many2one('salary.grid.degree', string=u'الدرجة') 
    new_department_id = fields.Many2one('hr.department', related='new_job_id.department_id', string='مقر الوظيفة',readonly=1)
    department_id = fields.Many2one('hr.department', related='employee_id.job_id.department_id', string='مقر الوظيفة', readonly=1)
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', string=u'الوظيفة', readonly=1)
    specific_id = fields.Many2one('hr.groupe.job', related='employee_id.job_id.specific_id', string=u'المجموعة النوعية', readonly=1)
    type_id = fields.Many2one('salary.grid.type', related='employee_id.type_id', string=u'الصنف', readonly=1)
    new_type_id = fields.Many2one('salary.grid.type', related='new_job_id.type_id', string=u'الصنف', readonly=1)
    dep_city = fields.Many2one('res.city',  related='employee_id.job_id.department_id.dep_city', string=u'المدينة',readonly=1)
    new_specific_id = fields.Many2one('hr.groupe.job', related='new_job_id.specific_id', string=u'المجموعة النوعية', readonly=1)
    employee_id = fields.Many2one('hr.employee', readonly=1, string=u'  الموظف')
    res_city = fields.Many2one('res.city',  string=u'المدينة')
    specific_group = fields.Selection([('same_specific', 'في نفس المجموعة النوعية'), ('other_specific', 'في مجموعة أخرى') ],  string=u'نوع المجموعة')
    employee_desire_ids = fields.Many2many('hr.employee.desire', string=u'رغبات النقل', readonly=1)


    @api.model
    def default_get(self, fields):
        res = super(HrEmployeeTransfertWizard, self).default_get(fields)
        transfert_line = self._context.get('active_id', False)
        transfert_line_obj = self.env['hr.transfert.sorting.line2']
        transfert = transfert_line_obj.search([('id', '=', transfert_line)])
        if transfert:
            res.update({'employee_id': transfert[0].hr_employee_transfert_id.employee_id.id,
                        'employee_desire_ids': transfert[0].hr_employee_transfert_id.desire_ids.ids
                        })
        return res

    @api.multi
    @api.onchange('res_city', 'specific_group')
    def _onchange_res_city(self):
        # get list of job depend on type_appointment
        res = {}
        if self.res_city and self.specific_group == 'other_specific':
            job_ids = self.env['hr.job'].search([('department_id.dep_city', '=', self.res_city.id), ('state', '=', 'unoccupied'), ('specific_id', '!=', self.specific_id.id)])
            res['domain'] = {'new_job_id': [('id', 'in', job_ids.ids)]}
            return res
        if self.res_city and self.specific_group == 'same_specific':
            job_ids = self.env['hr.job'].search([('department_id.dep_city', '=', self.res_city.id), ('state', '=', 'unoccupied'), ('specific_id', '=', self.specific_id.id)])
            res['domain'] = {'new_job_id': [('id', 'in', job_ids.ids)]}
            return res


    @api.multi
    def action_transfert(self):
        #res = super(HrEmployeeTransfertWizard, self).default_get(fields)
        active_model = self._context.get('active_model', False)
        active_id = self._context.get('active_id', False)
        if active_model == 'hr.transfert.sorting.line2' and active_id:
            transfert_line_obj = self.env['hr.transfert.sorting.line2']
            transfert_line = transfert_line_obj.search([('id', '=', active_id)])
            if transfert_line:
                transfert_line.new_job_id = self.new_job_id.id,
                transfert_line.new_type_id = self.new_type_id.id,
                transfert_line.new_department_id = self.new_department_id.id,
                transfert_line.new_degree_id = self.new_degree_id.id,
                transfert_line.res_city = self.res_city.id,

            if self.specific_group == 'same_specific':
                transfert_line.specific_group = 'same_specific'
            if self.specific_group == 'other_specific':
                transfert_line.specific_group = 'other_specific'
            if self.specific_group == False :
                transfert_line.specific_group = False

