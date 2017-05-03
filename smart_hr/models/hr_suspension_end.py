# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import SUPERUSER_ID
from umalqurra.hijri_date import HijriDate


class hr_suspension_end(models.Model):
    _name = 'hr.suspension.end'
    _inherit = ['ir.needaction_mixin', 'mail.thread']
    _description = 'Suspension Ending'
    _order = 'name desc'

    name = fields.Char(string=u'رقم  إجراء إنهاء كف اليد',readonly=1, related='decission_id.name', store=True)
    date = fields.Date(string=u'التاريخ',readonly=1, related='decission_id.date')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف',  domain=[('emp_state', '=', 'suspended')])
    letter_sender = fields.Char(string=u'جهة الخطاب', )
    letter_no = fields.Char(string=u'رقم الخطاب', )
    letter_date = fields.Date(string=u'تاريخ الخطاب', default=fields.Datetime.now())
    release_date = fields.Date(string=u'تاريخ إطلاق السراح', default=fields.Datetime.now())
    release_reason = fields.Text(string=u'سبب إطلاق السراح')
    suspension_id = fields.Many2one('hr.suspension', string=u'قرار كف اليد')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('hrm', u'مدير شؤون الموظفين'),
        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
    ], string=u'الحالة', default='draft', )
    condemned = fields.Boolean(string=u'‫صدر‬ في حقه‬ عقوبة‬', default=False)
    sentence = fields.Integer(string=u'مدة العقوبة (بالأيام)')
    suspension_attachment = fields.Binary(string=u'الصورة الضوئية للخطاب', attachment=True)
    decission_id  = fields.Many2one('hr.decision', string=u'القرارات',)

    @api.model
    def create(self, vals):
        ret = super(hr_suspension_end, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.suspension.end.seq')
        ret.write(vals)
        return ret
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'new' :
                raise ValidationError(u'لا يمكن حذف  إجراء إنهاء كف اليد فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(hr_suspension_end, self).unlink()
 
    @api.one
    def button_hrm(self):
        for rec in self:
            rec.state = 'hrm'

    @api.multi
    def button_done(self):
        self.ensure_one()
        self.employee_id.employee_state = 'employee'
        self.employee_id.emp_state = 'working'
        if self.condemned:
            release_date = fields.Date.from_string(self.release_date)
            suspension_date = fields.Date.from_string(self.suspension_id.suspension_date)
            duration = (release_date - suspension_date).days
            self.employee_id.promotion_duration -= self.sentence
            self.employee_id.service_duration -= self.sentence
            holiday_balance = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', self.employee_id.id),
                                                                             ('holiday_status_id', '=', self.env.ref(
                                                                                 'smart_hr.data_hr_holiday_status_normal').id),
                                                                             ])
            holidays_available_stock = holiday_balance.holidays_available_stock - duration
            holiday_balance.write({'holidays_available_stock': holidays_available_stock})
        self.suspension_id.write({'suspension_end_id': self.id})
        self.suspension_id.is_end = True
        self.state = 'done'

    @api.multi
    def open_decission_suspension(self):
        self.ensure_one()
        decision_obj= self.env['hr.decision']
        if self.decission_id:
            decission_id = self.decission_id.id
        else :
            decision_type_id = 1
            decision_date = fields.Date.today() # new date
            if self.employee_id.type_id.id != self.env.ref('smart_hr.data_salary_grid_type').id and self.condemned == False:
                decision_type_id = self.env.ref('smart_hr.data_decision_type28').id
            if self.employee_id.type_id.id != self.env.ref('smart_hr.data_salary_grid_type').id and self.condemned == True:
                decision_type_id = self.env.ref('smart_hr.data_decision_type27').id
            if self.employee_id.type_id.id == self.env.ref('smart_hr.data_salary_grid_type7').id and self.condemned == True :
                decision_type_id = self.env.ref('smart_hr.data_decision_type_suspension_end_member').id
            if self.employee_id.type_id.id == self.env.ref('smart_hr.data_salary_grid_type7').id and self.condemned == False :
                decision_type_id = self.env.ref('smart_hr.data_decision_type30').id
#             if self.employee_id.type_id.id != self.env.ref('smart_hr.data_salary_grid_type7').id or self.employee_id.type_id.id != self.env.ref('smart_hr.data_salary_grid_type').id:
#                  decision_type_id = self.env.ref('smart_hr.data_decision_type28').id
            # create decission
            decission_val={
                #'name': self.name,
                'decision_type_id':decision_type_id,
                'date':decision_date,
                'employee_id' :self.employee_id.id }
            decision = decision_obj.create(decission_val)
            decision.text = decision.replace_text(self.employee_id,decision_date,decision_type_id,'suspension')
            decission_id = decision.id
            self.decission_id =  decission_id
        return {
            'name': _(u'قرار إنهاء كف اليد'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.decision',
            'view_id': self.env.ref('smart_hr.hr_decision_wizard_form').id,
            'type': 'ir.actions.act_window',
            'res_id': decission_id,
            'target': 'new'
            }



    @api.one
    def button_refuse(self):
        for rec in self:
            rec.state = 'refuse'

    ''' Report Functions '''

    def get_ummqura(self, g_date):
        try:
            g_date = fields.Date.from_string(g_date)
            hijri_date = HijriDate(g_date.year, g_date.month, g_date.day, gr=True)
            hijri_date_str = "{0}/{1}/{2}".format(int(hijri_date.year), int(hijri_date.month), int(hijri_date.day))
            return hijri_date_str
        except Exception:
            return False

    def get_hindi_nums(self, string_number):
        return string_number


