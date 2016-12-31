# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.tools import SUPERUSER_ID
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'
    _description = 'hr holidays Request'
    _order = 'id desc'
    
    def _check_date(self, cr, uid, ids, context=None):
        for holiday in self.browse(cr, uid, ids, context=context):
            domain = [
                ('date_from', '<=', holiday.date_to),
                ('date_to', '>=', holiday.date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            nholidays = self.search_count(cr, uid, domain, context=context)
            if holiday.compensation_type=='money':
                return True
            if nholidays:
                return False
        return True
    
    @api.depends('holiday_status_id.entitlements.extension_period')
    def _check_is_extensible(self):
        # Check if the holiday have a pending or completed extension leave
        for rec in self:
            is_extensible = False
            if rec.holiday_status_id.entitlements:
                for en in rec.holiday_status_id.entitlements:
                    if rec.env.ref('smart_hr.data_hr_holiday_entitlement_all') == en.entitlment_category:
                        if en.extension_period!=0:
                            is_extensible = True
                            rec.extension_period=en.extension_period
                            break
            rec.is_extensible = is_extensible
            
    @api.multi
    def _set_external_autoritie(self):
        search_external_authoritie = self.env["external.authorities"].search([('holiday_status.id','=',self.holiday_status_id.id)])
        if search_external_authoritie:
            self.external_authoritie = search_external_authoritie[0] 
                      
    name = fields.Char(string=u'رقم القرار', advanced_search=True)
    date = fields.Date(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), advanced_search=True)
    raison = fields.Selection([
        ('other', u'سبب أخر'),
        ('husband', u'مرافقة الزوج'),
        ('wife', u'مرافقة الزوجة'),
        ('legit', u'مرافقة كمحرم شرعي'),
        ], default="other", string=u'السبب ')
    date_from = fields.Date(string=u'التاريخ من', default=fields.Datetime.now())
    date_to = fields.Date(string=u'التاريخ الى', default=fields.Datetime.now())
    duration = fields.Integer(string=u'الأيام', compute='_compute_duration')
    holiday_status_id = fields.Many2one('hr.holidays.status', string=u'نوع الأجازة', default=lambda self: self.env.ref('smart_hr.data_hr_holiday_status_normal'), advanced_search=True)
    state = fields.Selection(selection_add=[
        ('draft', u'طلب'),
        ('dm', u'مدير المباشر'),
        ('audit', u'تدقيق'),
        ('hrm', u'مدير شؤون الموظفين'),
        ('external_audit', u'جهة خارجية'),
        ('revision', u'مراجعة الخطاب'),
        ('revision_response', u'تسجيل رد الجهة'),
        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
        ('cancel', u'ملغاة'),
        ('cutoff', u'مقطوعة')], string=u'حالة', default='draft', advanced_search=True)
    is_current_user = fields.Boolean(string='Is Current User', compute='_is_current_user')
    is_direct_manager = fields.Boolean(string='Is Direct Manager', compute='_is_direct_manager')
    is_delayed = fields.Boolean(string='is_delayed', default=False)
    num_outspeech = fields.Char(string=u'رقم الخطاب الصادر')
    date_outspeech = fields.Date(string=u'تاريخ الخطاب الصادر')
    outspeech_file = fields.Binary(string=u'الخطاب الصادر')
    num_inspeech = fields.Char(string=u'رقم الخطاب الوارد')
    date_inspeech = fields.Date(string=u'تاريخ الخطاب الوارد')
    inspeech_file = fields.Binary(string=u'الخطاب الوارد')

    # Cancellation
    is_cancelled = fields.Boolean(string=u'ملغاة', compute='_is_cancelled')
    is_started = fields.Boolean(string=u'بدأت', compute='_compute_is_started')
    holiday_cancellation = fields.Many2one('hr.holidays.cancellation')    
    # Extension
    is_extension = fields.Boolean(string=u'تمديد إجازة')
    is_extended = fields.Boolean(string=u'ممددة', compute='_is_extended')
    extended_holiday_id = fields.Many2one('hr.holidays', string=u'الإجازة الممددة')
    parent_id = fields.Many2one('hr.holidays', string=u'Parent')
    extension_holidays_ids = fields.One2many('hr.holidays', 'parent_id', string=u'التمديدات')
    is_extensible = fields.Boolean(string=u'يمكن تمديدها',default=False,compute='_check_is_extensible',store=True)
    # decision
    need_decision = fields.Boolean('status_id need decision', related='holiday_status_id.need_decision')
    num_decision = fields.Char(string=u'رقم القرار')
    date_decision = fields.Date(string=u'تاريخ القرار')
    childbirth_date = fields.Date(string=u'تاريخ ولادة الطفل')
    medical_certificate = fields.Binary(string=u'شهادة طبية')
    birth_certificate = fields.Binary(string=u'شهادة الميلاد')
    extension_period = fields.Integer(string=u'مدة التمديد', default=0)
    external_authoritie = fields.Many2one('external.authorities', string=u'الجهة الخارجية',compute="_set_external_autoritie")
    entitlement_type = fields.Many2one('hr.holidays.entitlement.config', string=u'الصنف')
    death_person = fields.Char(string=u'المتوفي')
    compensation_type = fields.Selection([
        ('holiday', u'إجازة'),
        ('money', u' مقابل ‫مادي‬ ‬ ')], string=u'نوع التعويض')
    compensation_stock = fields.Integer(string=u'رصيد إجازات التعويض',related='employee_id.compensation_stock')
    accompaniment_type = fields.Selection([
        ('Relatives', u'أحد الأقارب '),
        ('child', u' ‫طفل‬‬')], string=u'نوع المرافقة')
    accompanied_child_age = fields.Integer(string=u'عمر الطفل')
    _constraints = [
        (_check_date, 'You can not have 2 leaves that overlaps on same day!', ['date_from', 'date_to'])]
    
    @api.depends('date_from')
    def _compute_is_started(self):
        for rec in self:
            if rec.date_from <= datetime.today().strftime('%Y-%m-%d'):
                rec.is_started = True

    @api.onchange('holiday_status_id')
    def onchange_holiday_status_id(self):
        res = {}
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_illness'):
            res['domain'] = {'entitlement_type': [('code', '=', 'illness')]}
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_death'):
            res['domain'] = {'entitlement_type': [('code', '=', 'death')]}
        return res

    @api.multi
    def _compute_balance(self, employee_id):
        holiday_obj = self.env['hr.holidays']
        holidays_status = self.env['hr.holidays.status'].search([])

        #compute solde of holidays
        for holiday_status_id in holidays_status:
            if holiday_status_id not in [self.env.ref('smart_hr.data_hr_holiday_status_illness')]:
                # recompute balance of the holiday_status_id
                # check if there is entitlements in holiday_status_id
                if holiday_status_id.entitlements:
                    right_entitlement = False
                    # loop under entitlements and get the right one
                    for en in holiday_status_id.entitlements:
                        if self.entitlement_type == en.entitlment_category:
                            right_entitlement = en
                            break
                        if self.env.ref('smart_hr.data_hr_holiday_entitlement_all') == en.entitlment_category:
                            right_entitlement = en
                            break

                    # calculate the balance of he employee for current holiday status
                    if right_entitlement:
                        periode = right_entitlement.periode
                        # check if the type existe in holidays_balance of the employee
                        balance_line = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', employee_id.id), ('holiday_status_id', '=', holiday_status_id.id)])
                        if not balance_line:
                            # create balance line in holidays_balance of the employee
                            balance_line = self.env['hr.employee.holidays.stock'].create({'holidays_available_stock': 0,
                                                                                      'employee_id': employee_id.id,
                                                                                      'holiday_status_id': holiday_status_id.id,
                                                                                      'token_holidays_sum': 0,
                                                                                      'periode': periode})
                        #employee_id.holidays_balance += balance_line
                        employee_solde = right_entitlement.holiday_stock_default 
                        if employee_solde > 0:
                            # calculate the number of worked month in current year
                            months = relativedelta(date.today(), date(date.today().year, 1, 1)).months
                            # balance per month
                            if months > 0:
                                balance = employee_solde / (periode * 12) * months
                                # get the sum of holidays given in from the start of current year
                                given_holidays_count = 0
                                for rec in holiday_obj.search([('state', '=', 'done'), ('employee_id', '=', employee_id.id), ('holiday_status_id', '=', holiday_status_id.id), ('date_from', '>=', date(date.today().year, 1, 1))]):
                                    given_holidays_count += rec.duration
                                balance -= given_holidays_count
                                balance_line.write({'holidays_available_stock': balance, 'token_holidays_sum': given_holidays_count})
    @api.multi
    def button_extend(self):
        # check if its possible to extend this holiday
        extensions_number = self.env['hr.holidays'].search_count([('extended_holiday_id', '=', self.extended_holiday_id.id)])
        extensions = self.env['hr.holidays'].search([('extended_holiday_id', '!=', False),('extended_holiday_id', '=', self.extended_holiday_id.id),('state', '=', 'done')])
        sum_periods = 0
        for extension in extensions:
            sum_periods += extension.duration
        for en in self.holiday_status_id.entitlements:
            if self.env.ref('smart_hr.data_hr_holiday_entitlement_all') == en.entitlment_category:
                extension_period = en.extension_period * 365
                if sum_periods >= extension_period:
                    raise ValidationError(u"لا يمكن تمديد هذا النوع من الاجازة أكثر من%s عام"%str(extension_period/365))
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_exceptional'):
            holiday_status_exceptional_stock = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', self.employee_id.id),('holiday_status_id', '=', self.env.ref('smart_hr.data_hr_holiday_status_exceptional').id)]).holidays_available_stock
            if holiday_status_exceptional_stock>0:
                 raise ValidationError(u"لا يمكن تمديد الاجازة قبل نهاتة رصيدها")
            if extensions_number==1:
                holiday_status_exceptional_stock+=extension_period
                
        if extensions_number >= self.holiday_status_id.extension_number and self.holiday_status_id.extension_number>0:
            raise ValidationError(u"لا يمكن تمديد هذا النوع من الاجازة أكثر من%s "%str(self.holiday_status_id.extension_number))

        view_id = self.env.ref('smart_hr.hr_holidays_form').id
        context = self._context.copy()
        default_date_from = fields.Date.to_string(fields.Date.from_string(self.date_to) + timedelta(days=1))
        context.update({
            u'default_is_extension': True,
            u'default_extended_holiday_id': self.id,
            u'default_date_from': default_date_from,
            u'readonly_by_pass': True,
        })
        return {
            'name': 'تمديد الإجازة',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'hr.holidays',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': False,
            'target': 'current',
            'context': context,
        }
        
    @api.multi
    def button_cancel(self):
        # Objects
        holidays_cancellation_obj = self.env['hr.holidays.cancellation']
        # Variables
        user = self.env['res.users'].browse(self._uid)
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        # Create leave cancellation request
        vals = {
                'employee_id': employee.id,
                'holidays': [(4, self.id)],
                'note': '   ',
            }
        holiday_cancellation_id = holidays_cancellation_obj.create(vals)
        # Add to log
        self.message_post(u"تم ارسال طلب إلغاء من قبل '" + unicode(user.name) + u"'")
        return {
                    'name': u'طلب إلغاء',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'hr.holidays.cancellation',
                    'view_id': self.env.ref('smart_hr.hr_holidays_cancellation_mine_form').id,
                    'type': 'ir.actions.act_window',
                    'res_id': holiday_cancellation_id.id,
                }
    @api.multi
    def button_cut(self):
        # Objects
        holidays_cancellation_obj = self.env['hr.holidays.cancellation']
        # Variables
        user = self.env['res.users'].browse(self._uid)
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        # Create leave cancellation request
        vals = {
                'employee_id': employee.id,
                'holidays': [(4, self.id)],
                'note': '   ',
            }
        holiday_cancellation_id = holidays_cancellation_obj.create(vals)
        # Add to log
        self.message_post(u"تم ارسال طلب القطع من قبل '" + unicode(user.name) + u"'")
        return {
                    'name': u'طلب قطع',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'hr.holidays.cancellation',
                    'view_id': self.env.ref('smart_hr.hr_holidays_cancellation_mine_form').id,
                    'type': 'ir.actions.act_window',
                    'res_id': holiday_cancellation_id.id,
                }
    @api.depends('extension_holidays_ids')
    def _is_extended(self):
        # Check if the holiday have a pending or completed extension leave
        for rec in self:
            is_extended = False
            for ext in rec.extension_holidays_ids:
                if ext.state != 'refuse':
                    is_extended = True
                    break
            rec.is_extended = is_extended
            
    @api.depends('holiday_cancellation')
    def _is_cancelled(self):
        # Check if the holidays have a pending or completed holidays cancellation
        for rec in self:
            is_cancelled = False
            if rec.holiday_cancellation and rec.holiday_cancellation.state != 'refuse': 
                    is_cancelled = True
                    break
            rec.is_cancelled = is_cancelled
            
    holiday_cancellation = fields.Many2one('hr.holidays.cancellation')    
    # Extension
    is_extension = fields.Boolean(string=u'تمديد إجازة')
    is_extended = fields.Boolean(string=u'ممددة', compute='_is_extended')
    extended_holiday_id = fields.Many2one('hr.holidays', string=u'الإجازة الممددة')
    parent_id = fields.Many2one('hr.holidays', string=u'Parent')
    extension_holidays_ids = fields.One2many('hr.holidays', 'parent_id', string=u'التمديدات')



                    
    @api.model
    def _check_state_access_right(self, vals):
        # override this method to be always returning true to avoid checking state access right
        return True
    
    
    @api.depends('employee_id')
    def _is_current_user(self):
        for rec in self:
            if rec.employee_id.user_id.id == rec._uid:
                rec.is_current_user = True
    @api.depends('employee_id')
    def _is_direct_manager(self):
        for rec in self:
            # System Admin Bypass
            if self.env['res.users'].browse(rec._uid).has_group('smart_hr.group_sys_manager'):
                rec.is_direct_manager = True
            elif rec.employee_id.user_id.id != rec._uid and rec.state == 'dm':
                depth = rec._get_dm_depth(rec._uid, rec.employee_id)
                if rec.state_dm == depth:
                    rec.is_direct_manager = True



    @api.depends('date_from', 'date_to')
    def _compute_duration(self):
        for holiday in self:
            if holiday.date_from and holiday.date_to:
                start_date = fields.Date.from_string(holiday.date_from)
                end_date = fields.Date.from_string(holiday.date_to)
                duration = (end_date - start_date).days + 1
                holiday.duration = duration
    @api.one
    def send_holiday_request(self):
        user = self.env['res.users'].browse(self._uid)
        for holiday in self:
            # check if the holiday status is supposed to be confirmed by direct manager
            if holiday.holiday_status_id.direct_director_decision:
                holiday.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"' إلى المدير المباشر")
                holiday.state = 'dm'
            else:
                holiday.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"' إلى مرحلة التدقيق")
                holiday.state = 'audit'
                
    @api.one
    def button_accept_dm(self):
        self.state = 'audit'
    
    @api.multi
    def action_delay_holiday(self):
        context = {};
        context['holiday_id'] = self.id
        return {
              'name': u'حجز الوظيفة',
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'hr.delay.holiday',
              'type': 'ir.actions.act_window',
              'context': context,
              'target': 'new',
              }
        
    @api.one
    def button_delay_dm(self):
        self.state = 'draft'
        
    @api.one
    def button_accept_audit(self):
        if self.holiday_status_id.employees_director_decision:
            self.state = 'hrm'
    
    @api.one
    def button_refuse_audit(self):
        if self.holiday_status_id.direct_director_decision:
            self.state = 'dm'
        else:
            self.state = 'draft'
    @api.one
    def button_accept_hrm(self):
        if not self.holiday_status_id.external_decision:
            self.state = 'done'
            # check illness holiday periode
            self.check_illness_holiday_periode_existance()
            # update holidays balance
            self._compute_balance(self.employee_id)
            if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_compensation'):
                if self.compensation_type == 'holiday':
                    self.employee_id.compensation_stock-=self.duration
                if self.compensation_type == 'money':
                    self.employee_id.compensation_stock=0

        if self.holiday_status_id.external_decision and not self.employee_id.external_decision:
            raise ValidationError(u"الموظف يحتاج إلى موافقة جهة خارجية.")
        if self.holiday_status_id.external_decision and self.employee_id.external_decision:
            self.state = 'external_audit'
            
    @api.one
    def button_delay_hrm(self):
        self.state = 'dm'
        
    @api.one
    def button_accept_external_audit(self):
        if not self.num_outspeech:
            raise ValidationError(u"الرجاء تعبئة رقم الخطاب الصادر.")
        if not self.date_outspeech:
            raise ValidationError(u"الرجاء تعبئة تاريخ الخطاب الصادر.")
        if not self.outspeech_file:
            raise ValidationError(u"الرجاء إرفاق الخطاب.")

        if self.holiday_status_id.external_decision:
            self.state = 'revision'
            
    @api.one
    def button_refuse_external_audit(self):
        self.state = 'audit'
    
    @api.one
    def button_accept_revision(self):
        self.state = 'revision_response'
            
    @api.one
    def button_refuse_revision(self):
        self.state = 'external_audit'
    
    
    
    
    
    def check_illness_holiday_periode_existance(self):
        # open a periode for illness holidays only if there is no open periode
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_illness'):

            # create new open periode if there is no ones
            periodes = self.env['hr.illness.holidays.periode'].search([('employee_id', '=', self.employee_id.id)])
            open_periode = False
            for periode in periodes:
                if fields.Datetime.from_string(periode.date_to) > datetime.now():
                    open_periode = True
                    break
            if not open_periode:
                # get the entitlement from holiday status
                entitlement = False
                for en in self.holiday_status_id.entitlements:
                    if en.entitlment_category.id == self.entitlement_type.id:
                        entitlement = en
                        break
                if entitlement:
                    self.env['hr.illness.holidays.periode'].sudo().create({'employee_id': self.employee_id.id, 'date_to': datetime.now() + relativedelta(years=entitlement.periode)})

        
    @api.one
    def button_accept_revision_response(self):
        if not self.num_inspeech:
            raise ValidationError(u"الرجاء تعبئة رقم الخطاب الوارد.")
        if not self.date_inspeech:
            raise ValidationError(u"الرجاء تعبئة تاريخ الخطاب الوارد.")
        if not self.inspeech_file:
            raise ValidationError(u"الرجاء إرفاق الخطاب.")
        self.state = 'done'
        # check illness holiday periode
        self.check_illness_holiday_periode_existance()
        # update holidays balance
        self._compute_balance(self.employee_id)
    @api.one
    def button_refuse_revision_response(self):
        self.state = 'refuse'
    

                
    @api.constrains('date_from', 'date_to')
    def check_dates_periode(self):
        # Objects
        holiday_obj = self.env['hr.holidays']
        candidate_obj = self.env['hr.candidates']
        deput_obj = self.env['hr.deputation']
         
        for holiday in self:
            # Date validation
            if fields.Date.from_string(holiday.date_from) < fields.Date.from_string(fields.Date.today()):
                raise ValidationError(u"تاريخ من يجب ان يكون أكبر من تاريخ اليوم")
             
            if holiday.date_from > holiday.date_to:
                raise ValidationError(u"تاريخ من يجب ان يكون أصغر من تاريخ الى")
            # check minimum request validation
            if holiday.holiday_status_id.minimum != 0 and holiday.duration < holiday.holiday_status_id.minimum and self.holiday_status_id!=self.env.ref('smart_hr.data_hr_holiday_compensation'):
                raise ValidationError(u"أقل فترة يمكن طلبها من نوع إجازة " + holiday.holiday_status_id.name + u" " + str(holiday.holiday_status_id.minimum) + u" أيام")
             
            # check maximum request validation
            if holiday.holiday_status_id.maximum != 0 and holiday.duration > holiday.holiday_status_id.maximum and self.holiday_status_id!=self.env.ref('smart_hr.data_hr_holiday_compensation'):
                raise ValidationError(u"أكثر فترة يمكن طلبها من نوع إجازة " + holiday.holiday_status_id.name + u" " + str(holiday.holiday_status_id.maximum) + u" أيام")
    
            # Date overlap
            # الإجازات
#             search_domain = [
#                 ('employee_id', '=', holiday.employee_id.id),
#                 ('id', '!=', holiday.id),
#                 ('state', 'not in', ['refuse', 'cancel']),
#             ]
#             for rec in holiday_obj.search(search_domain):
#                 if rec.date_from <= holiday.date_from <= rec.date_to or \
#                         rec.date_from <= holiday.date_to <= rec.date_to or \
#                         holiday.date_from <= rec.date_from <= holiday.date_to or \
#                         holiday.date_from <= rec.date_to <= holiday.date_to:
#                     # normal holidays can be ovelapped with illness type
#                     if not(rec.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_illness_normal') and \
#                             self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_normal') and self.holiday_status_id==self.env.ref('smart_hr.data_hr_holiday_compensation')):
#                         raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق فى الإجازات")
            # التدريب
            search_domain = [
                ('employee_id', '=', holiday.employee_id.id),
                ('state', '=', 'done'),
            ]
 
            for rec in candidate_obj.search(search_domain):
                dateto = fields.Date.from_string(rec.date_to)
                datefrom = fields.Date.from_string(rec.date_from)
                res = relativedelta(dateto, datefrom)
                months = res.months
                days = res.days
                # for none normal holidays test
                if self.holiday_status_id != self.env.ref('smart_hr.data_hr_holiday_status_normal') and  self.holiday_status_id!=self.env.ref('smart_hr.data_hr_holiday_compensation'):
                    if rec.date_from <= holiday.date_from <= rec.date_to or \
                            rec.date_from <= holiday.date_to <= rec.date_to or \
                            holiday.date_from <= rec.date_from <= holiday.date_to or \
                            holiday.date_from <= rec.date_to <= holiday.date_to:
                        raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق في التدريب")
 
                # for normal holidays test
                else:
                    if rec.date_from < holiday.date_from < rec.date_to and rec.date_from < holiday.date_to < rec.date_to:
                        if (months < 1) or (months == 1 and days == 0):
                            raise ValidationError(u"الإجازة يتخللها تدريب مدته أقل من شهر.")
                    if holiday.date_from <= rec.date_from <= holiday.date_to or \
                            holiday.date_from <= rec.date_to <= holiday.date_to:
                        raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق في التدريب")
                     
                         
             
            # الإنتتبات
            search_domain = [
                ('employee_id', '=', holiday.employee_id.id),
                ('state', '!=', 'refuse'),
            ]
            for rec in deput_obj.search(search_domain):
                if rec.date_from <= holiday.date_from <= rec.date_to or \
                        rec.date_from <= holiday.date_to <= rec.date_to or \
                        holiday.date_from <= rec.date_from <= holiday.date_to or \
                        holiday.date_from <= rec.date_to <= holiday.date_to:
                    raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق في الإنتداب")
 
            """
 
            TODO: check dates with :أوقات خارج الدوام ... 
 
            """

    def check_constraintes(self):
        """
        check constraintes beside date and periode ones
        """

        # check if there is another undone request for the same status of holiday
        if self.holiday_status_id in [self.env.ref('smart_hr.data_hr_holiday_status_normal'), self.env.ref('smart_hr.data_hr_holiday_status_exceptional'), self.env.ref('smart_hr.data_hr_holiday_status_compelling')]:
            # check if there is another undone request for the same status of holiday
            domain_search = [
                ('state', 'not in', ['done', 'refuse']),
                ('employee_id.id', '=', self.employee_id.id),
                ('holiday_status_id.id', '=', self.holiday_status_id.id),
                ('id', '!=', self.id)]
            if self.search_count(domain_search) > 0:
                raise ValidationError(u"لديك طلب قيد الإجراء من نفس هذا النوع من الإجازة.")

        # Constraintes for employee's nationnality
        if self.holiday_status_id.for_saudi and not self.holiday_status_id.for_other:
            # check the nationnality of the employee if it is saudi
            if self.employee_id.country_id != self.env.ref('base.sa'):
                raise ValidationError(u"هذا النوع من الإجازة ينطبق فقط على السعوديين.")

        # Constraintes for studyinglevel
        if self.holiday_status_id.educ_lvl_req:
            # check education level
            if self.employee_id.education_level not in self.holiday_status_id.education_levels:
                raise ValidationError(u"لم تتحصل على المستوى الدراسي المطلوب.")
            # check 3 years of services
            date_hiring = self.env['hr.decision.appoint'].search([('employee_id.id', '=', self.employee_id.id)], limit=1).date_hiring
            res = relativedelta(fields.Date.from_string(fields.Datetime.now()), fields.Date.from_string(date_hiring))
            if res.years < 3:
                raise ValidationError(u"ليس لديك ثلاث سنوات خدمة.")

        holiday_status_normal_stock = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', self.employee_id.id),('holiday_status_id', '=', self.env.ref('smart_hr.data_hr_holiday_status_normal').id)]).holidays_available_stock
        current_holiday_status_stock = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', self.employee_id.id),('holiday_status_id', '=', self.holiday_status_id.id)]).holidays_available_stock
        
        for en in self.holiday_status_id.entitlements:
            if self.env.ref('smart_hr.data_hr_holiday_entitlement_all') == en.entitlment_category:
                # غير مشروط
                if not en.conditionnal:
                    break
                else:
                    if self.duration > current_holiday_status_stock and current_holiday_status_stock:
                        raise ValidationError(u"ليس لديك الرصيد الكافي")

        # Constraintes for Compelling holidays اضطرارية
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_compelling'):
            if holiday_status_normal_stock>=self.duration:
                raise ValidationError(u"يوجد رصيد في الإجازات العاديّة")

                    # Constraintes for childbirth holidays وضع
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_childbirth'):
            if self.employee_id.gender!='female':
                raise ValidationError(u"لا يتمتّع بإجازة الوضع إلّا النساء")
            date_from = fields.Date.from_string(self.date_from)
            date_birth = fields.Date.from_string(self.childbirth_date)
            if (date_from-date_birth).days>14:
                raise ValidationError(u" لا يمكن لتاريخ بداية إجازة الوضع ان يتجاوز تاريخ الوضع بأسبوعين")
            print 'الوضع'

                        # Constraintes for maternity الامومة
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_maternity'):
            if self.employee_id.gender!='female':
                raise ValidationError(u"لا يتمتّع بإجازة الامومة إلّا النساء")

            last_holiday_status_childbirth = self.env['hr.holidays'].search([('state', '=', 'done'),('employee_id', '=', self.employee_id.id),('holiday_status_id', '=', self.env.ref('smart_hr.data_hr_holiday_status_childbirth').id)]).ids
            last_id = last_holiday_status_childbirth and max(last_holiday_status_childbirth)
            last_holiday_status_childbirth_browse =self.env['hr.holidays'].browse(last_id)   
            if last_holiday_status_childbirth_browse.date_to>self.date_from:
                raise ValidationError(u"لا يمكن التمتع باجازة الامومة قبل انتهاء اجازة الوضع")
            date_from = fields.Date.from_string(self.date_from)
            date_birth = fields.Date.from_string(last_holiday_status_childbirth_browse.childbirth_date)
            if (date_from-date_birth).days>1095:
                raise ValidationError(u"لا يمكن التمتع باجازة الامومة بعد اكثر من ثلاث سنوات من الوضع")
                        # Constraintes for adoption الحضانة

        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_adoption'):
            if self.employee_id.gender!='female':
                raise ValidationError(u"لا يتمتّع بإجازة الحضانة إلّا النساء")

                        # Constraintes for child_birth_dad المولود

        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_child_birth_dad'):
            if self.employee_id.gender != 'male':
                raise ValidationError(u"لا يتمتّع بإجازة المولود إلّا الرجال")
            date_birth = fields.Date.from_string(self.childbirth_date)
            date_from = fields.Date.from_string(self.date_from)
            if (date_from-date_birth).days > 7:
                raise ValidationError(u"لا يمكن لتاريخ بداية إجازة المولود ان يتجاوز تاريخ الوضع بأسبوع")            
            if (self.duration) > 1:
                raise ValidationError(u"لا يمكن لإجازة المولود ان تتجاوز يوم")  

            # Constraintes for death الوفاة

        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_death'):
            for en in self.holiday_status_id.entitlements:
                if en.entitlment_category.name == self.entitlement_type.name and en.holiday_stock_default<self.duration:
                    raise ValidationError(u" %s  ان تتجاوز يوم %s  لا يمكن لإجازة   " %(en.holiday_stock_default,en.entitlment_category.name))
                    break

        date_from = fields.Date.from_string(self.date_from)
        past_demand_number = self.env['hr.holidays'].search_count([('state', '=', 'done'),('employee_id', '=', self.employee_id.id),
                                                                   ('holiday_status_id', '=', self.holiday_status_id.id), ('date_from', '>=', date(date_from.year, 1, 1))])
        if self.holiday_status_id.demand_number_max<=past_demand_number and self.holiday_status_id.demand_number_max>0:
            raise ValidationError(u" لا يمكن تجزئة هذا النوع من الإجازات على أكثر من %s مرّة " %self.holiday_status_id.demand_number_max)
                  # Constraintes for accompaniment_exceptional اجازة مرافقة استثنائية

        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_accompaniment_exceptional'):
            if self.accompaniment_type=="child" and self.employee_id.gender!='female':
                raise ValidationError(u"لا يتمتّع بإجازة مرافقة طفل  إلّا النساء")
            if self.accompaniment_type=="child" and self.accompanied_child_age>7:
                raise ValidationError(u"يجب أن يكون عمر الطفل أقل من 7 سنوات")
            if holiday_status_normal_stock>0:
                raise ValidationError(u"يوجد رصيد في الإجازات العاديّة")
        
        
        
        """
        
        check solde of illness holidays
        
        """
        # if ilness holiday than check periode
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_illness'):
            periodes = self.env['hr.illness.holidays.periode'].search([('employee_id', '=', self.employee_id.id)])
            open_periode = False
            for periode in periodes:
                if fields.Datetime.from_string(periode.date_to) > datetime.now():
                    open_periode = periode
                    break
            # case there is no open periode
            if open_periode:
                print open_periode
                # case there is an open periode, check the entitlement
                # fetch all illness holidays from the start of open periode
                holidays = self.env['hr.holidays'].search([('state', '=', 'done'), ('employee_id', '=', self.employee_id.id), ('date_from', '>=', fields.Datetime.from_string(open_periode.date_from))])
                sum_days = 0
                for holiday in holidays:
                    sum_days += holiday.duration
                print sum_days
                # get the entitlement from holiday status
                entitlement = False
                for en in self.holiday_status_id.entitlements:
                    if en.entitlment_category.id == self.entitlement_type.id:
                        entitlement = en
                        break
                if entitlement:
                    if entitlement.holiday_stock_default <= sum_days:
                        raise ValidationError(u"ليس لديك الرصيد الكافي")





    @api.model
    def create(self, vals):
        res = super(HrHolidays, self).create(vals)
        res.check_constraintes()
        # Sequence
        vals = {}
        vals['state'] = 'draft'
        vals['name'] = self.env['ir.sequence'].get('hr.holidays.seq')
        res.write(vals)
        return res

class HrIllnessHolidaysPeriode(models.Model):

    _name = 'hr.illness.holidays.periode'
    _description = 'فترات الاجازة المرضية'
    
    employee_id = fields.Many2one('hr.employee')
    date_from = fields.Datetime(string=u'التاريخ من', default=fields.Datetime.now())
    date_to = fields.Datetime(string=u'التاريخ الى')



class HrDelayHoliday(models.Model):
    _name = 'hr.delay.holiday'  
    _description = u'تأجيل إجازة'
    
    date_from = fields.Date(string=u'التاريخ من', default=lambda self: self.env['hr.holidays'].search([('id', '=', self._context['holiday_id'])], limit=1).date_from)
    date_to = fields.Date(string=u'التاريخ الى', readonly=1, default=lambda self: self.env['hr.holidays'].search([('id', '=', self._context['holiday_id'])], limit=1).date_to)
    delay_days = fields.Integer(string=u'عدد أيام التأجيل', compute='_compute_delay_days')

    @api.depends('date_from', 'date_to')
    def _compute_delay_days(self):
        holiday = self.env['hr.holidays'].search([('id', '=', self._context['holiday_id'])])
        for holidayDelay in self:
            if holidayDelay.date_from and holidayDelay.date_to:
                start_date = fields.Date.from_string(holiday.date_from)
                new_start_date = fields.Date.from_string(holidayDelay.date_from)
                if new_start_date < start_date:
                    raise ValidationError(u"الرجاء التأكد من تاريخ بد الإجازة.")
                delay_days = (new_start_date - start_date).days 
                holidayDelay.delay_days = delay_days
                holidayDelay.date_to = fields.Date.from_string(holiday.date_to) + timedelta(days=self.delay_days)
    
    
    @api.multi
    def action_delay_holiday_confirm(self):
        holiday = self.env['hr.holidays'].search([('id', '=', self._context['holiday_id'])])
        if holiday.holiday_status_id.postponement_period > 0:
            if self.delay_days > 0 and self.delay_days <= holiday.holiday_status_id.postponement_period:
                # add delay_days to date_from and date_to of the holiday
                new_date_from = fields.Date.from_string(holiday.date_from) + timedelta(days=self.delay_days)
                new_date_to = fields.Date.from_string(holiday.date_to) + timedelta(days=self.delay_days)
                holiday.write({'date_from': new_date_from, 'date_to': new_date_to, 'state': 'draft'})
    
            if self.delay_days > 0 and self.delay_days > holiday.holiday_status_id.postponement_period:
                raise ValidationError(u"لا يمكن تأجيل هذا النوع من الاجازة أكثر من " + str(holiday.holiday_status_id.postponement_period) + u"يوماً.")
        else:
            raise ValidationError(u"لا يمكن تأجيل هذا النوع من الاجازة. ")
            
class HrHolidaysStatus(models.Model):
    _name = 'hr.holidays.status'
    _inherit = 'hr.holidays.status'
    _description = 'holidays status'


    name = fields.Char(string=u'نوع الاجازة')
    minimum = fields.Integer(string=u'الحد الأدنى في المرة الواحدة')
    maximum = fields.Integer(string=u'الحد الأقصى في المرة الواحدة')
    postponement_period = fields.Integer(string=u'مدة التأجيل')
    extension_number = fields.Integer(string=u'عدد مرات تمديد', default=-1)
    deductible_normal_leave = fields.Boolean(string=u'تخصم مدتها من رصيد الاجازة العادية')
    deductible_duration_service = fields.Boolean(string=u'تخصم مدتها من فترة الخدمة')
    educ_lvl_req = fields.Boolean(string=u'يطبق شرط المستوى التعليمي')
    need_decision = fields.Boolean(string=u' تحتاج إلى قرار')
    direct_decision = fields.Boolean(string=u'تحتاج إلى قرار مباشرة')
    direct_director_decision = fields.Boolean(string=u'موافقة مدير مباشر', default=True)
    external_decision = fields.Boolean(string=u'موافقة خارجية', default=False)
    salary_spending = fields.Boolean(string=u'يجوز صرف راتبها')
    employees_director_decision = fields.Boolean(string=u'موافقة مدير شؤون الموظفين', default=True)
    can_be_cancelled = fields.Boolean(string=u'يمكن الغاؤها', default=True)
    evaluation_condition = fields.Boolean(string=u'يطبق شرط تقويم الأداء')
    education_levels = fields.One2many('hr.employee.education.level', 'leave_type', string=u'المستويات التعليمية')
    entitlements = fields.One2many('hr.holidays.status.entitlement', 'leave_type', string=u'أنواع الاستحقاقات')
    assessments_required = fields.One2many('hr.assessment.result.config', 'leave_type', string=u'التقييمات المطلوبة')
    percentages = fields.One2many('hr.holidays.status.salary.percentage', 'holiday_status', string=u'نسب الراتب المحتسبة')
    for_saudi = fields.Boolean(string=u'تنطبق على السعوديين', default=True)
    for_other = fields.Boolean(string=u'تنطبق على غير السعوديين', default=True)
    promotion_deductible = fields.Boolean(string=u'تخصم مدتها من رصيد الترقية', default=False)
    min_amount = fields.Float(string=u'المبلغ الادنى') 
    pension_percent = fields.Float(string=u' (%)نسبة راتب التقاعد') 
    demand_number_max = fields.Integer(string=u'عدد مرات الطلب',default='-1')
    traveling_ticket = fields.Boolean(string=u'تذكرة سفر', default=False)
    traveling_ticket_familiar = fields.Boolean(string=u'تذكرة سفر عائليّة', default=False)

    @api.onchange('deductible_duration_service')
    def onchange_deductible_duration_service(self):
        if self.deductible_duration_service:
            self.promotion_deductible = True

    
    @api.constrains('pension_percent')
    def check_pension_percent(self):
        for rec in self:
            if rec.pension_percent<0 or rec.pension_percent>100:
                raise ValidationError(u"نسبة راتب التقاعد خاطئة ")
                
class HrHolidaysStatusEntitlement(models.Model):
    _name = 'hr.holidays.status.entitlement'
    _description = u'أنواع الاستحقاقات'
    entitlment_category = fields.Many2one('hr.holidays.entitlement.config', string=u'فئة الاستحقاق')
    holiday_stock_default = fields.Integer(string=u'الرصيد (يوم)')
    conditionnal = fields.Boolean(string=u'مشروط')
    periode = fields.Selection([
        (1, u'سنة'),
        (2, u'سنتين'),
        (3, u'ثلاث سنوات'),
        (4, u'أربع سنوات'),
        (5, u'خمس سنوات'),
        (6, u'ستة سنوات'),
        (7, u'سبعة سنوات'),
        (8, u'ثمانية سنوات'),
        (9, u'تسعة سنوات'),
        (10, u'عشرة سنوات'),
        ], string=u'المدة', default=1)
    leave_type = fields.Many2one('hr.holidays.status', string='leave type')
#     holiday_stock_open = fields.Boolean(string=u'الرصيد مفتوح')
    extension_period = fields.Integer(string=u'مدة التمديد', default=0)
    
class HrHolidaysStatusSalaryPercentage(models.Model):
    _name = 'hr.holidays.status.salary.percentage'
    _description = u'نسب الراتب المحتسبة'

    sequence = fields.Integer(string=u'الأولوية')
    periode = fields.Integer(string=u'عدد الأشهر')
    salary_proportion = fields.Float(string=u'نسبة الراتب (%)', default=100) 
    holiday_status = fields.Many2one('hr.holidays.status', string='holiday status')

class EntitlementConfig(models.Model):
    _name = 'hr.holidays.entitlement.config'
    _description = u' اصناف الاستحقاقات'

    name = fields.Char(string=u'المسمّى')
    code = fields.Char(string='code')




