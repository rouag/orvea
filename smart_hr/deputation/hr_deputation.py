# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
from openerp.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from umalqurra.hijri_date import HijriDate
from lxml import etree


class HrDeputation(models.Model):
    _name = 'hr.deputation'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _rec_name = 'order_date'
    _description = u'الانتدابات'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        # Objects
        user_obj = self.env['res.users']
        uid = self._uid
        user = user_obj.browse(uid)
        if self._context.get('params', False):
            active_id = self._context.get('params', False).get('id', False)
            deputation_obj = self.env['hr.deputation'].search([('id', '=', int(active_id))], limit=1)
        res = super(HrDeputation, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                        submenu=submenu)
        if view_type == 'form' and deputation_obj:
            arch = etree.XML(res['arch'])
            is_exelence = user.has_group('smart_hr.group_exelence_employee')
            secret_report = deputation_obj.secret_report
            if secret_report:
                if is_exelence is False:
                    for node in arch.xpath("//field[@name='lettre_number']"):
                        node.set('invisible', '1')
                        setup_modifiers(node, res['fields']['lettre_number'])
                    for node in arch.xpath("//field[@name='lettre_date']"):
                        node.set('invisible', '1')
                        setup_modifiers(node, res['fields']['lettre_date'])
                    for node in arch.xpath("//field[@name='file_lettre']"):
                        node.set('invisible', '1')
                        setup_modifiers(node, res['fields']['file_lettre'])
            # Get current user group
            res['arch'] = etree.tostring(arch, encoding="utf-8")

        return res

    order_date = fields.Date(string='تاريخ الطلب', default=fields.Datetime.now(), readonly=1)
    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', domain=[('employee_state', '=', 'employee'), ('emp_state', 'not in', ['suspended', 'terminated'])],
                                  required=1)
    number = fields.Char(string='الرقم الوظيفي', readonly=1)
    code = fields.Char(string=u'رمز الوظيفة ', readonly=1)
    governmental_entity = fields.Many2one('res.partner', string=u'الجهة ',
                                          domain=['|', ('company_type', '=', 'governmental_entity'),
                                                  ('company_type', '=', 'company')])
    country_id = fields.Many2one(related='employee_id.country_id', store=True, readonly=True, string='الجنسية')

    number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1)
    job_id = fields.Many2one('hr.job', string='الوظيفة', store=True, readonly=1)
    type_id = fields.Many2one('salary.grid.type', string='الصنف', store=True, readonly=1)
    department_id = fields.Many2one('hr.department', string='الادارة', store=True, readonly=1)
    department_inter_id = fields.Many2one('hr.department', string='الادارة',)
    city_id = fields.Many2one(related='department_inter_id.dep_city', store=True, readonly=True, string='المدينة')
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', store=True, readonly=1)
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', store=True, readonly=1)
    date_from = fields.Date(string=u'تاريخ البدء', required=1)
    date_to = fields.Date(string=u'تاريخ الإنتهاء', required=1)
    date_start = fields.Date(string=u'من')
    date_end = fields.Date(string=u'الى')
    note = fields.Text(string=u'الملاحظات', readonly=1, states={'draft': [('readonly', 0)]})
    ministre_report = fields.Boolean(string='  قرار من الوزير المختص', compute='_compute_ministre_report')
    decision_number = fields.Char(string='رقم القرارمن الوزير المختص')
    decision_date = fields.Date(string='تاريخ القرارمن الوزير المختص ', default=fields.Datetime.now(), readonly=1)
    file_order = fields.Binary(string=' صورة القرار من الوزير المختص  ', attachment=True)
    file_order_name = fields.Char(string=' صورة القرار من الوزير المختص  ')
    file_decision = fields.Binary(string='نسخة من حالة الميزانية', attachment=True)
    calcul_wekeend = fields.Boolean(string='  احتساب عطلة نهاية الاسبوع', default=False)

    lettre_number = fields.Char(string='رقم خطاب التغطية')
    lettre_date = fields.Date(string='تاريخ خطاب التغطية', default=fields.Datetime.now(), readonly=1)
    file_lettre = fields.Binary(string='نسخة خطاب التغطية', attachment=True)
    file_lettre_name = fields.Char(string='نسخة خطاب التغطية')

    report_number = fields.Char(string='عنوان التقرير')
    report_date = fields.Date(string='تاريخ التقرير', default=fields.Datetime.now(), readonly=1)
    file_report = fields.Binary(string='صورة التقرير', attachment=True)
    file_report_name = fields.Char(string='صورة التقرير')

    amount = fields.Float(string='المبلغ')

    transport_alocation = fields.Boolean(string='بدل نقل')
    net_salary = fields.Boolean(string=' الراتب')
    secret_report = fields.Boolean(string=' سري')
    anual_balance = fields.Boolean(string=' الرصيد السنوي')
    alowance_bonus = fields.Boolean(string=' البدلات و التعويضات و المكافات')
    the_availability = fields.Selection([
        ('hosing_and_food', u'السكن و الطعام '),
        ('hosing_or_food', u'السكن أو الطعام '),
        ('nothing', u'لا شي '),
    ], string=u'السكن و الطعام ', default='hosing_and_food')
    type = fields.Selection([
        ('internal', u'  داخلى'),
        ('external', u' خارجى ')], string=u'إنتداب', default='internal')
    # city_id = fields.Many2one('res.city', string=u'المدينة')
    category_id = fields.Many2one('hr.deputation.category', string=u'فئة التصنيف')
    country_ids = fields.Many2one('hr.country.city', string=u'البلاد'  ) 
    state = fields.Selection([
        ('draft', u'طلب'),
        ('audit', u'دراسة الطلب'),
        ('waiting', u'اللجنة'),
        ('order', u'إصدار التقرير'),
        ('humain', u'موارد البشرية'),
        ('done', u'اعتمدت'),
        ('finish', u'منتهية'),
        ('refuse', u'مرفوضة')
    ], string=u'حالة', default='draft',)
    task_name = fields.Char(string=u' المهمة', required=1)
    duration = fields.Integer(string=u'المدة')

    member_deputation = fields.Selection([
        ('member', u'انتداب عضو'),
        ('notmember', u'انتداب غيرعضو')
    ], string=u'انتداب عضو', default='notmember', required=1)
    deputation_type = fields.Many2one('hr.deputation.type', string='نوع الانتداب', required="1")
    deputation_balance_override = fields.Boolean(string=u"تجاوز رصيد الانتدابات")
    external_deputation_balance_override = fields.Boolean(string=u"تجاوز رصيد الانتداب الخارجي")
    is_paied = fields.Boolean(string='is paied', default=False)
    payslip_id = fields.Many2one('hr.payslip')
    decission_id  = fields.Many2one('hr.decision', string=u'القرارات')

    @api.multi
    def open_decission_deputation(self):
        decision_obj= self.env['hr.decision']
        if self.decission_id:
            decission_id = self.decission_id.id
        else :
            decision_type_id = 1
            decision_date = fields.Date.today() # new date
            if self.deputation_type :
                decision_type_id = self.env.ref('smart_hr.data_employee_deputation').id

            decission_val={
                'name': self.env['ir.sequence'].get('hr.deputation.seq'),
                'decision_type_id':decision_type_id,
                'date':decision_date,
                'employee_id' :self.employee_id.id }
            decision = decision_obj.create(decission_val)
            decision.text = decision.replace_text(self.employee_id,decision_date,decision_type_id,'employee')
            decission_id = decision.id
            self.decission_id =  decission_id
        return {
            'name': _(u'قرار  إنتداب'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.decision',
            'view_id': self.env.ref('smart_hr.hr_decision_wizard_form').id,
            'type': 'ir.actions.act_window',
            'res_id': decission_id,
            'target': 'new'
            }

#     @api.onchange('category_id')
#     def onchange_category_id(self):
#         res = []
#         if  self.category_id :
#             category_search_ids = self.env['hr.deputation.category'].search([('id', '=' , self.category_id.id)]).country_city_ids
#             for rec in category_search_ids :
#                 self.country_ids =rec.id
#                 print"category_search_ids",category_search_ids
# #             result_employee_ids = list(minus_employee_ids)
# #             print"result_employee_ids",result_employee_ids
# #             res = {'country_ids': [('id', 'in', result_employee_ids.country_id)]}
# #             return res
# #             
# #             print"category_search_ids",category_search_ids
# #             res.update({'domain': {'country_ids': [('id', 'in', category_search_ids.country_id.id)]}})
# #         return res


    @api.onchange('member_deputation')
    def onchange_member_deputation(self):
        res = {}
        if self.member_deputation == 'member':
            res['domain'] = {'employee_id': [('is_member', '=', True)]}
        else:
            res['domain'] = {'employee_id': [('is_member', '=', False)]}
        return res

    @api.model
    def get_deputation_allowance_amount(self, number_of_days):
        deputation_amount = 0.0
        transport_amount = 0.0
        deputation_allowance = False
        deputation_allowance_obj = self.env['hr.deputation.allowance']
        employee = self.employee_id
        deputation_allowance_lines = deputation_allowance_obj.search([('grade_ids', 'in', [employee.grade_id.id])])
        if deputation_allowance_lines:
            deputation_allowance = deputation_allowance_lines[0]
            if self.type == 'internal':
                if deputation_allowance.internal_transport_type == 'daily':
                    transport_amount = deputation_allowance.internal_transport_amount * number_of_days
                elif deputation_allowance.internal_transport_type == 'monthly':
                    transport_amount = deputation_allowance.internal_transport_amount / 30.0 * number_of_days
                if deputation_allowance.internal_deputation_type == 'daily':
                    deputation_amount = deputation_allowance.internal_deputation_amount * number_of_days
                elif deputation_allowance.internal_deputation_type == 'monthly':
                    deputation_amount = deputation_allowance.internal_deputation_amount / 30.0 * number_of_days
            elif self.type == 'external':
                if deputation_allowance.external_transport_type == 'daily':
                    transport_amount = deputation_allowance.external_transport_amount * number_of_days
                elif deputation_allowance.external_transport_type == 'monthly':
                    transport_amount = deputation_allowance.external_transport_amount / 30.0 * number_of_days
                # search a correct category
                searchs = deputation_allowance.category_ids.search([('category_id', '=', self.category_id.id)])
                if searchs:
                    if deputation_allowance.external_deputation_type == 'daily':
                        deputation_amount = searchs[0].amount * number_of_days
                    elif deputation_allowance.internal_transport_type == 'monthly':
                        deputation_amount = searchs[0].amount / 30.0 * number_of_days
        return deputation_amount, transport_amount, deputation_allowance

    @api.onchange('duration')
    def onchange_duration(self):
        dep_setting = self.env['hr.deputation.setting'].search([], limit=1)
        warning={}
        if self.employee_id:
            if self.employee_id.deputation_balance < self.duration:
                warning = {
                    'title': _('تحذير!'),
                    'message': _('لقد تم تجاوز الرصيد السنوي للإنتداب!'),
                }
                self.deputation_balance_override = True
        if self.duration and dep_setting:
            if self.duration >= dep_setting.period_decision:
                self.ministre_report = True
        if self.type == 'external':
            external_type_id_balance = self.deputation_type.external_balance
            external_deputations = self.search([('type', '=', 'external'), ('employee_id', '=', self.employee_id.id), ('state', '=','done'), ('type_id', '=', self.type_id.id )])
            ext_dep_duration = 0
            for dep in external_deputations:
                ext_dep_duration += dep.duration
            if ext_dep_duration + self.duration > external_type_id_balance:
                self.external_deputation_balance_override = True
        return {'warning': warning}
    
    @api.one
    @api.depends('duration')
    def _compute_ministre_report(self):
        dep_setting = self.env['hr.deputation.setting'].search([], limit=1)
        if self.duration and dep_setting:
            if self.duration >= dep_setting.period_decision:
                self.ministre_report = True

    @api.multi
    def action_draft(self):
        self.ensure_one()
            # ‫check completion of essay periode

        task_obj = self.env['hr.employee.task']
        self.env['hr.employee.task'].create({'name': self.task_name,
                                                 'employee_id': self.employee_id.id,
                                                 'date_from': self.date_from,
                                                 'date_to': self.date_to,
                                                 'duration': self.duration,
                                                 'governmental_entity': self.governmental_entity.id,
                                                 'type_procedure': 'deputation',
                                                 })
        title = u" إشعار  بطلب إنتداب "
        msg = u" إشعار  بطلب إنتداب " + unicode(self.employee_id.display_name)
        group_id = self.env.ref('smart_hr.group_exelence_employee')
        self.send_exelence_group(group_id, title, msg)
        self.state = 'audit'

    def send_exelence_group(self, group_id, title, msg):
        '''
        @param group_id: res.groups
        '''
        for recipient in group_id.users:
            self.env['base.notification'].create({'title': title,
                                                  'message': msg,
                                                  'user_id': recipient.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_deputation',
                                                  'notif': True
                                                  })

    def send_refuse_dep_group(self, group_id, title, msg):
        '''
        @param group_id: res.groups
        '''
        for recipient in group_id.users:
            self.env['base.notification'].create({'title': title,
                                                  'message': msg,
                                                  'user_id': recipient.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_deputation',
                                                  'notif': True
                                                  })

    @api.multi
    def action_commission(self):
        for deputation in self:
            deputation.state = 'waiting'

    @api.multi
    def action_audit(self):
        for deputation in self:
            deputation.state = 'done'

    @api.multi
    def action_waiting(self):
        for deputation in self:
            deputation.state = 'done'

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.state = 'order'

    @api.multi
    def button_refuse_audit(self):
        for deputation in self:
            title = u"' إشعار برفض  الإنتداب'"
            msg = u"' لقد رفض  الإنتداب  '" + unicode(self.employee_id.display_name) + u"'"
            group_id = self.env.ref('smart_hr.group_deputation_department')
            self.send_exelence_group(group_id, title, msg)
            deputation.state = 'refuse'

    @api.multi
    def action_order(self):
        for deputation in self:
            deputation.state = 'humain'

    @api.multi
    def action_humain(self):
        for deputation in self:
            #             type = ' إنتداب'
            #             self.env['hr.employee.history'].sudo().add_action_line(self.employee_id, deputation.decision_number,  deputation.date_from, type)
            deputation.state = 'finish'


    @api.multi
    def button_refuse(self):
        for deputation in self:
            deputation.state = 'refuse'

    @api.multi
    def action_refuse(self):
        for deputation in self:
            deputation.state = 'refuse'

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'done' :
                raise ValidationError(u'لا يمكن حذف الإنتداب فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(HrDeputation, self).unlink()


    @api.constrains('date_from', 'date_to')
    @api.onchange('date_from', 'date_to')
    def onchange_date_to(self):
        if self.date_from:
            if fields.Date.from_string(self.date_from).weekday() in [4, 5]:
                raise ValidationError(u"هناك تداخل في تاريخ البدء مع عطلة نهاية الاسبوع  ")
            if self.env['hr.smart.utils'].public_holiday_intersection(self.date_from):
                raise ValidationError(u"هناك تداخل في تاريخ البدء مع  عطلة او عيد  ")
        if self.date_to:
            if fields.Date.from_string(self.date_to).weekday() in [4, 5]:
                raise ValidationError(u"هناك تداخل في تاريخ الإنتهاء مع عطلة نهاية الاسبوع")
            if self.env['hr.smart.utils'].public_holiday_intersection(self.date_from):
                raise ValidationError(u"هناك تداخل في تاريخ الإنتهاء مع  عطلة او عيد  ")        
        if self.date_from and self.date_to:
            self.duration = self.env['hr.smart.utils'].compute_duration(self.date_from, self.date_to)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.number = self.employee_id.number
            self.country_id = self.employee_id.country_id
            appoint_line = self.env['hr.decision.appoint'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'done')], limit=1)
            if appoint_line:
                self.job_id = appoint_line.job_id.id
                self.code = appoint_line.job_id.name.number
                self.number_job = appoint_line.number
                self.type_id = appoint_line.type_id.id
                self.grade_id = appoint_line.grade_id.id
                self.department_id = appoint_line.department_id.id

    @api.one
    @api.constrains('date_from', 'date_to')
    def check_dates_periode(self):
        # Objects
        holiday_obj = self.env['hr.holidays']
        candidate_obj = self.env['hr.candidates']
        deput_obj = self.env['hr.deputation']
        comm_obj = self.env['hr.employee.commissioning']
        lend_obj = self.env['hr.employee.lend']
        schol_obj = self.env['hr.scholarship']
        termination_obj = self.env['hr.termination']
        # TODO  الدورات التدربية

        # Date validation
        if self.date_from > self.date_to:
            raise ValidationError(u"تاريخ البدء يجب ان يكون أصغر من تاريخ الإنتهاء")
            # check minimum request validation
            # التدريب
        search_domain = [
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'done'),
        ]

        for rec in candidate_obj.search(search_domain):
            dateto = fields.Date.from_string(rec.date_to)
            datefrom = fields.Date.from_string(rec.date_from)
            res = relativedelta(dateto, datefrom)
            months = res.months
            days = res.days
        # for none normal holidays test
        for rec in holiday_obj.search(search_domain):
            if rec.date_from <= self.date_from <= rec.date_to or \
                                    rec.date_from <= self.date_to <= rec.date_to or \
                                    self.date_from <= rec.date_from <= self.date_to or \
                                    self.date_from <= rec.date_to <= self.date_to:
                raise ValidationError(u"هناك تداخل في التواريخ مع إجازة")
                # الإنتداب
        for rec in deput_obj.search(search_domain):
            if rec.date_from <= self.date_from <= rec.date_to or \
                                    rec.date_from <= self.date_to <= rec.date_to or \
                                    self.date_from <= rec.date_from <= self.date_to or \
                                    self.date_from <= rec.date_to <= self.date_to:
                raise ValidationError(u"هناك تداخل في التواريخ مع إنتداب")
        # تكليف
        for rec in comm_obj.search(search_domain):
            if rec.date_from <= self.date_from <= rec.date_to or \
                                    rec.date_from <= self.date_to <= rec.date_to or \
                                    self.date_from <= rec.date_from <= self.date_to or \
                                    self.date_from <= rec.date_to <= self.date_to:
                raise ValidationError(u"هناك تداخل في التواريخ مع تكليف")
        # إعارة
        for rec in lend_obj.search(search_domain):
            if rec.date_from <= self.date_from <= rec.date_to or \
                                    rec.date_from <= self.date_to <= rec.date_to or \
                                    self.date_from <= rec.date_from <= self.date_to or \
                                    self.date_from <= rec.date_to <= self.date_to:
                raise ValidationError(u"هناك تداخل في التواريخ مع إعارة")
        # الابتعاث
        for rec in schol_obj.search(search_domain):
            if rec.date_from <= self.date_from <= rec.date_to or \
                                    rec.date_from <= self.date_to <= rec.date_to or \
                                    self.date_from <= rec.date_from <= self.date_to or \
                                    self.date_from <= rec.date_to <= self.date_to:
                raise ValidationError(u"هناك تداخل في التواريخ مع ابتعاث")
        for rec in termination_obj.search(search_domain):
            if rec.date <= self.date_from:
                raise ValidationError(u"هناك تداخل في التواريخ مع  طى قيد")
        # التدريب
        for rec in candidate_obj.search(search_domain):
            if rec.date_from <= self.date_from <= rec.date_to or \
                                    rec.date_from <= self.date_to <= rec.date_to or \
                                    self.date_from <= rec.date_from <= self.date_to or \
                                    self.date_from <= rec.date_to <= self.date_to:
                raise ValidationError(u"هناك تداخل في التواريخ مع تدريب")

class HrDeputationCategory(models.Model):
    _name = 'hr.deputation.category'
     
#     category = fields.Selection([
#         ('high', u'مرتفعة'),
#         ('a', u'أ'),
#         ('b', u'ب'),
#         ('c', u'ج'),
#     ], string=u'الفئات', default='c')
    country_city_ids = fields.One2many('hr.country.city', 'duputation_category_id', string=u'البلاد')
    name = fields.Char(string='المسمى', required=1)


class HrCountryCity(models.Model):
    _name = 'hr.country.city'
    
    name = fields.Char(string='المسمى', related='country_id.name')
    country_id = fields.Many2one('res.country', string=u'البلاد', domain="[('code_nat','!=',False)]")
    city_id = fields.Many2one('res.city', string=u'المدينة', domain="[('country_id','=',country_id)]")
    duputation_category_id = fields.Many2one('hr.deputation.category', string=u'الفئة')


class HrDeputationType(models.Model):
    _name = 'hr.deputation.type'

    name = fields.Char(string='المسمى')
    code = fields.Char(string='الرمز')
    external_balance = fields.Float(string='رصيد الإنتداب الخارجي الذي تستوجب قرار من الوزير')

