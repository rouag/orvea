# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class HrScholarshipDecision(models.Model):
    _name = 'hr.scholarship.decision'
    _rec_name = 'employee_id'
    
    name = fields.Char(string='المسمى')
    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', required=1)
    number = fields.Char(related='employee_id.number', store=True, readonly=True, string=' الرقم الوظيفي')
    job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True, string=' الوظيفة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True, string=' الادارة')
    date = fields.Date(string=u'تاريخ المباشرة', default=fields.Datetime.now(), required=1)
    state = fields.Selection([('new', ' ارسال طلب'),
                             ('hrm', 'في إنتظار الإعتماد'),
                             ('done', 'اعتمدت'),
                             ('cancel', 'رفض'),], string='الحالة', readonly=1, default='new')

    scholarship_ids = fields.Many2many('hr.scholarship', string=u'الابتعاث', required=True)
    order_number = fields.Char(string=u'رقم الخطاب', required=1)
    order_date = fields.Date(string=u'تاريخ الخطاب', required=1) 
    file_decision = fields.Binary(string=u'الخطاب', required=1, attachment=True)
    file_decision_name = fields.Char(string=u'اسم الخطاب')
    order_source = fields.Char(string=u'مصدر الخطاب' , required=1)
    note = fields.Text(string='ملاحظات')
    
    @api.one
    def action_hrm(self):
        self.state = 'hrm'

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.one
    def action_done(self):
        for scholarship in self.scholarship_ids:
            type = " مباشرة بعد"+" " +scholarship.scholarship_type.name.encode('utf-8')
            self.env['hr.employee.history'].sudo().add_action_line(self.employee_id, self.name, self.date, type)
        self.state = 'done'

    @api.one
    def action_refuse(self):
        self.state = 'new'
        
    @api.model
    def create(self, vals):
        res = super(HrScholarshipDecision, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.scholarship.deciision.seq')
        res.write(vals)
        return res
    
    @api.multi
    def unlink(self):
        # Validation
        for rec in self:
            if rec.state != 'new':
                raise ValidationError(u'لا يمكن حذف ابتعاث فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(HrScholarshipDecision, self).unlink()
