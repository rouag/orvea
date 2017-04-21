# -*- coding: utf-8 -*-


from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import SUPERUSER_ID
from umalqurra.hijri_date import HijriDate


class hr_suspension(models.Model):
    _name = 'hr.suspension'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'
    _description = 'Suspension Decision'

    name = fields.Char(string=u' رقم إجراء كف اليد', )
    date = fields.Date(string=u'التاريخ', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', domain=[('emp_state', 'not in', ['suspended', 'terminated']), ('employee_state', '=', 'employee')])
    employee_state = fields.Selection([('new', u'جديد'),
                                       ('waiting', u'في إنتظار الموافقة'),
                                       ('update', u'إستكمال البيانات'),
                                       ('done', u'اعتمدت'),
                                       ('refused', u'رفض'),
                                       ('employee', u'موظف')], string=u'الحالة', related='employee_id.employee_state')
    letter_sender = fields.Char(string=u'جهة الخطاب', )
    letter_number = fields.Integer(string=u'رقم الخطاب', )
    letter_date = fields.Date(string=u'تاريخ الخطاب')
    suspension_date = fields.Date(string=u'تاريخ بدء الإيقاف')
    suspension_attachment = fields.Binary(string=u'الصورة الضوئية للخطاب', attachment=True)
    suspension_attachment_name = fields.Char(string=u'file name')
    raison = fields.Text(string=u'سبب كف اليد')
    suspension_end_id = fields.Many2one('hr.suspension.end', string=u'قرار إنهاء كف اليد')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('hrm', u'مدير شؤون الموظفين'),

        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
    ], string=u'الحالة', default='draft')
    done_date = fields.Date(string='تاريخ التفعيل')
    decission_id  = fields.Many2one('hr.decision', string=u'القرارات',)
    decision_number = fields.Char(string='رقم القرار', readonly=1, related='decission_id.name')
    decision_date = fields.Date(string='تاريخ القرار ', readonly=1, related='decission_id.date')
    display_decision_info = fields.Boolean(compute='_compute_display_decision_info')
    history_line_id = fields.Many2one('hr.employee.history')

    def _compute_display_decision_info(self):
        for rec in self:
            if rec.state in ['make_decision', 'done'] and rec.decission_id.state == 'done':
                self.display_decision_info = True
            else:
                self.display_decision_info = False

    def num2hindi(self, string_number):
        if string_number:
            hindi_numbers = {'0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤', '5': '٥', '6': '٦', '7': '٧', '8': '٨',
                             '9': '٩', '.': ','}
            if isinstance(string_number, unicode):
                hindi_string = string_number.encode('utf-8', 'replace')
            else:
                hindi_string = str(string_number)
            for number in hindi_numbers:
                hindi_string = hindi_string.replace(str(number), hindi_numbers[number])
            return hindi_string

    @api.model
    def create(self, vals):
        ret = super(hr_suspension, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.suspension.seq')
        ret.write(vals)
        return ret


    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'new' :
                raise ValidationError(u'لا يمكن حذف قرار كف اليد فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(hr_suspension, self).unlink()
  
    #     @api.constrains('employee_id')
    #     def check_employee_id(self):
    #         for rec in self:
    #             if rec.employee_id.emp_state != 'working':
    #                 raise ValidationError(u"هذا الموظف ليس على رأس العمل حتى يكف يده")

    @api.one
    def button_hrm(self):
        user = self.env['res.users'].browse(self._uid)
        for rec in self:
            rec.state = 'hrm'
            rec.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"'")

   

    @api.one
    def button_done(self):
        user = self.env['res.users'].browse(self._uid)
        for rec in self:
            rec.employee_id.emp_state = 'suspended'
            rec.done_date = fields.Date.today()
            history_line_id = self.env['hr.employee.history'].sudo().add_action_line(rec.employee_id, rec.decission_id.name, rec.decission_id.date, "كف اليد")
            rec.history_line_id = history_line_id
            rec.state = 'done'
            rec.message_post(u"تم الإعتماد من قبل '" + unicode(user.name) + u"'")
          #  rec.create_report_attachment()

    @api.one
    def button_refuse(self):
        for rec in self:
            rec.state = 'refuse'

    @api.multi
    def button_suspension_end(self):
        suspension_end_obj = self.env['hr.suspension.end']
        vals = {
                'employee_id': self.employee_id.id,
                'suspension_id': self.id,
            }
        suspension_end_id = suspension_end_obj.create(vals)
        if suspension_end_id :
            value = {
                    'name': u'إنهاء كف اليد',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'hr.suspension.end',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                   'res_id': suspension_end_id.id,
                   }
        return value

    @api.multi
    def button_suspension(self):
        decision_obj= self.env['hr.decision']
        if self.decission_id:
            decission_id = self.decission_id.id
        else :
            decision_type_id = 1
            decision_date = fields.Date.today() # new date
            if self.employee_id.id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type29').id
            # create decission
            decission_val={
                'name': self.name,
                'decision_type_id':decision_type_id,
                'date':decision_date,
                'employee_id' :self.employee_id.id }
            decision = decision_obj.create(decission_val)
            decision.text = decision.replace_text(self.employee_id,decision_date,decision_type_id,'employee')
            decission_id = decision.id
            self.decission_id =  decission_id
        self.history_line_id.num_decision = self.decission_id.name
        self.history_line_id.date_decision = self.decission_id.date
        return {
            'name': _(u'قرار كف اليد'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.decision',
            'view_id': self.env.ref('smart_hr.hr_decision_wizard_form').id,
            'type': 'ir.actions.act_window',
            'res_id': decission_id,
            'target': 'new'
            }

    @api.model
    def _needaction_domain_get(self):
        return [
            ('state', '=', 'hrm'),
        ]

    """
        Report Functions
    """

    def get_ummqura(self, g_date):
        try:
            g_date = fields.Date.from_string(g_date)
            hijri_date = HijriDate(g_date.year, g_date.month, g_date.day, gr=True)
            hijri_date_str = "{0}/{1}/{2}".format(int(hijri_date.year), int(hijri_date.month), int(hijri_date.day))
            return self.num2hindi(hijri_date_str)
        except Exception:
            return False

    def get_hindi_nums(self, string_number):
        return self.num2hindi(string_number)

    def reverse_string(self, string):
        if string:
            return str(string)[::-1]

