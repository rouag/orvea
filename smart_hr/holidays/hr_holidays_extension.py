# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime, timedelta

class HrHolidaysExtension(models.Model):
    _name = 'hr.holidays.extension'
    _description = 'Holidays Extension'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'

    def _default_employee_id(self):
        return self.env['hr.employee'].search([('user_id','=',self.env.uid)]).id

    name = fields.Char(string=u'المسمى')
    date = fields.Date(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee',  string=u'الموظف', domain=[('employee_state','=','employee')], default=_default_employee_id)
    is_the_creator = fields.Boolean(string='Is Current User', compute='_employee_is_the_creator')
    entitlement_id = fields.Many2one('hr.holidays.status.entitlement', string=u'نوع الاستحقاق')
    holiday_status_id = fields.Many2one('hr.holidays.status','نوع الاجازة', domain="[('entitlements.extension_period', '!=', '0')]")
    state = fields.Selection([
        ('draft', u'طلب'),
        ('audit', u'مراجعة'),
        ('done', u'إعتمد'),
        ('refuse', u'رفض'),
    ], string=u'حالة', default='draft', )
    note = fields.Text(string = u'الملاحظات')
    duration = fields.Integer(string=u'الأيام')
    open_period = fields.Many2one('hr.holidays.periode', string=u'periode')
    num_decision = fields.Char(string=u'رقم الخطاب', required=True)
    date_decision = fields.Date(string=u'تاريخ الخطاب', required=True)
    decision_file = fields.Binary(string=u'الخطاب', attachment=True, required=True)
    decision_file_name = fields.Char(string=u'file name')
    decission_id = fields.Many2one('hr.decision', string=u'القرارات')

    @api.multi
    def open_decission_holidays_extension(self):
        decision_obj= self.env['hr.decision']
        if self.decission_id:
            decission_id = self.decission_id.id
        else :
            decision_type_id = 1
            decision_date = fields.Date.today() # new date
            if self.employee_id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type45').id
            # create decission
            decission_val={
                'name': self.env['ir.sequence'].get('hr.holidays.cancellation.seq'),
                'decision_type_id':decision_type_id,
                'date':decision_date,
                'employee_id' :self.employee_id.id }
            decision = decision_obj.create(decission_val)
            decision.text = decision.replace_text(self.employee_id,decision_date,decision_type_id,'employee')
            decission_id = decision.id
            self.decission_id =  decission_id
        return {
            'name': _(u'قرار تمديد رصيد الاجازات'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.decision',
            'view_id': self.env.ref('smart_hr.hr_decision_wizard_form').id,
            'type': 'ir.actions.act_window',
            'res_id': decission_id,
            'target': 'new'
            }





    @api.depends('employee_id')
    def _employee_is_the_creator(self):
        for rec in self:
            if rec.employee_id.user_id.id == rec.create_uid.id:
                rec.is_the_creator = True

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.holidays.extension') or 'New'
        result = super(HrHolidaysExtension, self).create(vals)
        return result
 
    @api.constrains('holiday_status_id')
    def check_constrains(self):
        current_holiday_status_stock = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', self.employee_id.id),('holiday_status_id', '=', self.holiday_status_id.id)])

        right_entitlement=False
        for en in self.holiday_status_id.entitlements:
            if en.entitlment_category.id == self.env.ref('smart_hr.data_hr_holiday_entitlement_all').id:
                right_entitlement = en
                break
        if right_entitlement:
            if current_holiday_status_stock:
                if current_holiday_status_stock.holidays_available_stock>0 :
                    if current_holiday_status_stock.token_holidays_sum<right_entitlement.extension_period*354:
                        raise ValidationError(u'لا يمكن تمديد  رصيد إجازة قبل إنتهاء رصيدها')
            else:
                raise ValidationError(u'لا يمكن تمديد  رصيد إجازة قبل إنتهاء رصيدها')

            extension_period =  right_entitlement.extension_period
            today = datetime.today()
            periodes = self.env['hr.holidays.periode'].search([('employee_id', '=', self.employee_id.id),
                                                           ('holiday_status_id', '=', self.holiday_status_id.id),
                                                           ('entitlement_id', '=', right_entitlement.id),
                                                           ('active', '=', True),
                                                           ])
            open_period = False
            for periode in periodes:
                if fields.Datetime.from_string(periode.date_to) > fields.Datetime.from_string(fields.Date.today()):
                    open_period = periode
                    break
            if open_period:
                self.open_period=open_period.id
                old_extensions = self.search([('holiday_status_id','=',self.holiday_status_id.id),('state', '=', 'done'),
                                               ('employee_id', '=', self.employee_id.id),
                                                ('date', '>=', fields.Datetime.from_string(open_period.date_from))])
                sum_days = 0
                for extension in old_extensions:
                    sum_days += extension.duration
                if extension_period*354 < sum_days+self.duration:
                    raise ValidationError(u'ليس لديك الرصيد الكافي للتمديد')
        else:
            raise ValidationError(u'لا يمكن تمديد  استحقاق هذه الاجازة')
    @api.one
    def button_send(self):

        user = self.env['res.users'].browse(self._uid)
        for extension in self:
            extension.check_constrains()
            extension.state = 'audit'
                # send notification for requested the DM
            if self.is_the_creator: 
                self.env['base.notification'].create({'title': u'إشعار بتمديد إجازة',
                                                      'message': u'الرجاء مراجعة طلب اتمديد',
                                                      'user_id': self.employee_id.parent_id.user_id.id,
                                                      'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                      'notif': True,
                                                      'res_id': self.id,
                                                      'res_action':' smart_hr.action_hr_holidays_extension_form',
                                                  })
            else:
                # send notification for requested employee
                res_model = 'smart_hr.action_hr_holidays_extension_employees'
                self.env['base.notification'].create({'title':  u'إشعار بتمديد إجازة',
                                                  'message': u'الرجاء مراجعة طلب اتمديد',
                                                  'user_id': self.employee_id.user_id.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'notif': True,
                                                  'res_id': self.id,
                                                  'res_action':' smart_hr.action_hr_holidays_extension_form',
                                                  })
                
            extension.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"'")

    @api.one
    def button_done(self):
        self.ensure_one()
        for extension in self:
            holidays_available_stock_line = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', self.employee_id.id),
                                                           ('holiday_status_id', '=', self.holiday_status_id.id)])
            if holidays_available_stock_line:
                holidays_available_stock_line.holidays_available_stock+=extension.duration
                extension.open_period.holiday_stock += extension.duration
            extension.state = 'done'

    @api.one
    def button_refuse(self):
        for extension in self:
            extension.state = 'refuse'
                # send notification for requested the DM
            self.env['base.notification'].create({'title': u'إشعار برفض تمديد إجازة',
                                                  'message': u' '+self.employee_id.name +u'لقد تم الرفض من قبل ',
                                                  'user_id': self.employee_id.user_id.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'notif': True,
                                                  'res_id': self.id,
                                                  'res_action':' smart_hr.action_hr_holidays_extension_form',

                                                  })

    @api.model
    def _needaction_domain_get(self):
        return [
            ('state', 'in', ['audit']),
        ]
