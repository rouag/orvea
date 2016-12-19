# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import SUPERUSER_ID
from lxml import etree

class hrHolidaysCancellation(models.Model):
    _name = 'hr.holidays.cancellation'
    _description = 'Holidays Cancellation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'

    name = fields.Char(string=u'رقم القرار', advanced_search=True)
    date = fields.Date(string=u'تاريخ الطلب', default=fields.Datetime.now())
    leave_id = fields.Many2one('hr.holidays', string=u'الإجازة الملغاة', advanced_search=True)
    employee_id = fields.Many2one('hr.employee', related='leave_id.employee_id', string=u'الموظف', advanced_search=True)
    is_current_user = fields.Boolean(string='Is Current User', related='leave_id.is_current_user')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('audit', u'تدقيق'),
        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
    ], string=u'حالة', default='audit', advanced_search=True)

    @api.model
    def create(self, vals):
        res = super(hrHolidaysCancellation, self).create(vals)
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.holidays.cancellation.seq')
        res.write(vals)
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft' and self._uid != SUPERUSER_ID:
                raise ValidationError(u'لا يمكن حذف طلب إلغاء الإجازة فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(hrHolidaysCancellation, self).unlink()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        # Objects
        user_obj = self.env['res.users']
        employee_obj = self.env['hr.employee']
        # Variables
        uid = self._uid
        user = user_obj.browse(uid)
        emp_ids = employee_obj.search(['|', ('parent_id.user_id', 'child_of', uid), ('user_id', '=', uid)])
        #
        res = super(hrHolidaysCancellation, self).fields_view_get(view_id=view_id, view_type=view_type,  toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            # Make fields readonly for all employees except admin
            arch = etree.XML(res['arch'])
            # Get current user group
            is_admin = user.has_group('smart_hr.group_sys_manager')
            is_hr = user.has_group('smart_hr.group_hr')
            is_hr_payroll = user.has_group('smart_hr.group_hr_payroll')
            is_ade = user.has_group('smart_hr.group_ade')
            is_followup = user.has_group('smart_hr.group_followup')
            if not (is_admin or is_hr or is_hr_payroll or is_ade or is_followup):
                # Fields
                employee_id = arch.xpath("//field[@name='employee_id']")[0]
                # Updated attributes
                employee_id.set('domain', "['|',('id','in',%s),('user_id','=',%s)]" % (emp_ids.ids, uid))
            res['arch'] = etree.tostring(arch, encoding="utf-8")
        return res

    @api.one
    def button_audit(self):
        user = self.env['res.users'].browse(self._uid)
        for cancellation in self:
            cancellation.state = 'audit'
            cancellation.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"'")

    @api.one
    def button_done(self):
        user = self.env['res.users'].browse(self._uid)
        for cancellation in self:
            cancellation.state = 'done'
            # Update the leave state
            cancellation.leave_id.state = 'cancel'
            # Update leave stock
            # Normal, Statement and Accompaniment
            if cancellation.leave_id.leave_type_id in [self.env.ref('smart_hr.data_hr_leave_type_01'),
                                                       self.env.ref('smart_hr.data_hr_leave_type_11'),
                                                       self.env.ref('smart_hr.data_hr_leave_type_16')]:
                cancellation.leave_id.employee_id.leave_normal += cancellation.leave_id.duration
            # Emergency
            elif cancellation.leave_id.leave_type_id == self.env.ref('smart_hr.data_hr_leave_type_02'):
                cancellation.leave_id.employee_id.leave_emergency += cancellation.leave_id.duration
            # Compensation
            elif cancellation.leave_id.leave_type_id == self.env.ref('smart_hr.data_hr_leave_type_10'):
                cancellation.leave_id.employee_id.leave_compensation += cancellation.leave_id.duration
            cancellation.message_post(u"تم التدقيق من قبل '" + unicode(user.name) + u"'")

    @api.one
    def button_refuse(self):
        for cancellation in self:
            cancellation.state = 'refuse'

    @api.model
    def _needaction_domain_get(self):
        return [
            ('state', 'in', ['audit']),
        ]