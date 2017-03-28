# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
from openerp.exceptions import UserError
from openerp.tools import SUPERUSER_ID
from umalqurra.hijri_date import HijriDate
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from umalqurra.hijri_date import HijriDate


class HrOvertime(models.Model):
    _name = 'hr.overtime'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _rec_name = 'order_date'
    _description = u'إجراء خارج دوام'

    order_date = fields.Date(string='تاريخ الطلب', default=fields.Datetime.now(), readonly=1)
    amount = fields.Float(string='المبلغ')
    note = fields.Text(string=u'الملاحظات', readonly=1, states={'draft': [('readonly', 0)]})
    line_ids = fields.One2many('hr.overtime.ligne', 'overtime_id', string=u'خارج دوام', readonly=1, states={'draft': [('readonly', 0)]})
    decision_number = fields.Char(string='رقم القرار')
    decision_date = fields.Date(string='تاريخ القرار', default=fields.Datetime.now(), readonly=1)
    file_decision = fields.Binary(string='صورة القرار', attachment=True)
    file_decision_name = fields.Char(string='صورة القرار')
    lettre_number = fields.Char(string='رقم خطاب التغطية')
    lettre_date = fields.Date(string='تاريخ خطاب التغطية', default=fields.Datetime.now(), readonly=1)
    file_lettre = fields.Binary(string='نسخة خطاب التغطية', attachment=True)
    file_lettre_name = fields.Char(string='نسخة خطاب التغطية')
    state = fields.Selection([
                              ('draft', u'طلب'),
                              ('audit', u'دراسة الطلب'),
                              ('waiting', u'اللجنة'),
                              ('humain', u'موارد البشرية'),
                              ('done', u'اعتمدت'),
                              ('finish', u'منتهية'),
                               ('cut', u'مقطوعة'),
                              ('cancel', u'ملغى'),
                               ('refuse', u'مرفوضة')
                              ], string=u'حالة', default='draft',)

    @api.multi
    def button_cancel_overtime(self):
        for overtime in self :
            for line in overtime.line_ids :
                for rec in line :
                    date = fields.Date.from_string(fields.Date.today())
                    if rec.date_from < str(date)  :
                        raise ValidationError(u"لا يمكن الإلغاء نظرا لبدأ  بعض المهام")
            title = u"' إشعار   بإلغاء  خارج الدوام'"
            msg = u"' إشعار   بإلغاء  خارج الدوام رقم'" + unicode(overtime.decision_number) + u"'"
            group_id = self.env.ref('smart_hr.group_overtime_department')
            overtime.state = 'cancel'

    @api.multi
    def button_cut(self):
        for overtime in self:
            for line in overtime.line_ids :
                for rec in line :
                    date = fields.Date.from_string(fields.Date.today())
                    if rec.date_to < str(date)  :
                        raise ValidationError(u"لا يمكن القطع نظرا لإنهاء  بعض المهام")
                    self.env['base.notification'].create({'title': u'إشعار   بقطع  خارج الدوام',
                                              'message': u'لقد تم إشعار  بقطع  خارج الدوام',
                                              'user_id': line.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': line.id,
                                             'res_action': 'smart_hr.action_hr_overtime'})
            overtime.state = 'cut'

            title = u"' إشعار   بقطع  خارج الدوام'"
            msg = u"' إشعار   بقطع  خارج الدوام رقم'" + unicode(overtime.decision_number) + u"'"
            group_id = self.env.ref('smart_hr.group_overtime_department')
            self.send_overtime_department_group(group_id, title, msg)



    @api.multi
    def action_draft(self):
        for overtime in self:
            for line in overtime.line_ids :
                for rec in line :
                    task_obj = self.env['hr.employee.task']
                    self.env['hr.employee.task'].create({'name' : rec.mission,
                        'employee_id' : rec.employee_id.id,
                        'date_from' : rec.date_from ,
                        'date_to' : rec.date_to,
                        'duration' : rec.days_number,
                        #  'governmental_entity' : self.governmental_entity.id,
                        'type_procedure' :'overtime',
                        })
            overtime.state = 'audit'

    @api.multi
    def action_commission(self):
        for overtime in self:
            overtime.state = 'waiting'

    @api.multi
    def action_audit(self):
        for overtime in self:
            overtime.state = 'humain'

    @api.multi
    def action_waiting(self):
        for overtime in self:
            overtime.state = 'humain'

    @api.multi
    def action_done(self):
        for overtime in self:
            for line in overtime.line_ids :
                for rec in line :
                    date = fields.Date.from_string(fields.Date.today())
                    if rec.date_to > str(date)  :
                        raise ValidationError(u"يوجد مهمة لم يصل تاريخ انتهائها بعد")
                    self.env['base.notification'].create({'title': u'إشعار بإنهاء  خارج الدوام',
                                              'message': u'لقد تم إشعار بإنهاء  خارج الدوام',
                                              'user_id': line.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': line.id,
                                             'res_action': 'smart_hr.action_hr_overtime'})

            title = u"' إشعار   بإنهاء  خارج الدوام'"
            msg = u"' إشعار   بإنهاء  خارج الدوام رقم'" + unicode(overtime.decision_number) + u"'"
            group_id = self.env.ref('smart_hr.group_overtime_department')
            self.send_overtime_department_group(group_id, title, msg)
            overtime.state = 'finish'

    @api.multi
    def action_humain(self):
        for overtime in self:
            overtime.state = 'done'


    @api.multi
    def button_refuse(self):
        for overtime in self:
            for line in overtime.line_ids :
                self.env['base.notification'].create({'title': u'إشعار إشعار برفض  خارج الدوام',
                                              'message': u'لقد تم إشعار برفض  خارج الدوام',
                                              'user_id': line.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': line.id,
                                             'res_action': 'smart_hr.action_hr_overtime'})

            overtime.state = 'refuse'

    def send_overtime_department_group(self, group_id, title, msg):
        '''
        @param group_id: res.groups
        '''
        for recipient in group_id.users:
            self.env['base.notification'].create({'title': title,
                                                  'message': msg,
                                                  'user_id': recipient.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_overtime',
                                                  'notif': True
                                                  })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_(u'لا يمكن حذف خارج دوام  إلا في حالة طلب !'))
        return super(HrOvertime, self).unlink()


class HrOvertimeLigne(models.Model):
    _name = 'hr.overtime.ligne'
    _description = u' خارج دوام'

    overtime_id = fields.Many2one('hr.overtime', string=u' خارج دوام', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string=u' الموظف', required=1, Domain=[('emp_state', '!=', 'suspended'), ('emp_state', '!=', 'terminated')])
    type = fields.Selection([('friday_saturday', ' أيام الجمعة والسبت'),
                             ('holidays', 'أيام الأعياد'),
                             ('normal_days', 'الايام العادية')
                             ], string='نوع خارج الدوام', default='friday_saturday')
    days_number = fields.Integer(string='عدد الايام')
    heure_number = fields.Integer(string='عدد الساعات')
    date_from = fields.Date(string=u'التاريخ من ', required=1)
    date_to = fields.Date(string=u'الى', required=1)
    type_compensation = fields.Selection([('compensatory_leave', ' إجازة تعويضية'),
                                          ('amount', 'مقابل مادي')], string='نوع التعويض', required=1, default='compensatory_leave')
    mission = fields.Text(string='المهمة', required=1)

    is_grade = fields.Boolean(string=u'يتطلب تكليف', default=False)
    number_direct_overtime = fields.Char(string='رقم التكليف ')
    date_direct_overtime = fields.Date(string='تاريخ التكليف')
    file_direct_overtime = fields.Binary(string='صورة التكليف', attachment=True)
    file_direct_overtime_name = fields.Char(string='صورة التكليف')
    is_paied = fields.Boolean(string='is paied', default=False)
    payslip_id = fields.Many2one('hr.payslip')


    @api.onchange('date_to')
    def _onchange_date_to(self):
        if self.date_to and self.date_from:
            date_from = fields.Date.from_string(self.date_from)
            date_to = fields.Date.from_string(self.date_to)
            days_number = (date_to - date_from).days
            self.days_number = days_number

    @api.onchange('days_number')
    def _onchange_days_number(self):
        if self.days_number:
            self.date_to = fields.Date.from_string(self.date_from) + timedelta(days=self.days_number)

    @api.one
    @api.constrains('days_number')
    def check_days_heure_number(self):
        if self.type_compensation == 'compensatory_leave' and self.days_number < 1 :
            raise ValidationError(u"عدد الأيام في إجازة تعويضية يكون أكبر من صفر")


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
        over_obj = self.env['hr.overtime.ligne']
        # TODO  الدورات التدربية
            # Date validation
        if self.date_from > self.date_to:
            raise ValidationError(u"تاريخ البدء يجب ان يكون أصغر من تاريخ الإنتهاء")
            # check minimum request validation
            # التدريب
        search_domain = [
                ('employee_id', '=', self.employee_id.id)]

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
                self.date_from <= rec.date_to <= self.date_to :
                raise ValidationError(u"هناك تداخل في التواريخ مع إجازة")
    
        for rec in comm_obj.search(search_domain):
            if rec.date_from <= self.date_from <= rec.date_to or \
                    rec.date_from <= self.date_to <= rec.date_to or \
                    self.date_from <= rec.date_from <= self.date_to or \
                    self.date_from <= rec.date_to <= self.date_to:
                raise ValidationError(u"هناك تداخل في التواريخ مع  تكليف")
        # إعارة
        for rec in lend_obj.search(search_domain):
            if rec.date_from <= self.date_from <= rec.date_to or \
                    rec.date_from <= self.date_to <= rec.date_to or \
                    self.date_from <= rec.date_from <= self.date_to or \
                    self.date_from <= rec.date_to <= self.date_to:
                raise ValidationError(u"هناك تداخل في التواريخ مع إعارة")

        for rec in over_obj.search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id)]):
             if rec.date_from <= self.date_from <= rec.date_to or \
                    rec.date_from <= self.date_to <= rec.date_to or \
                    self.date_from <= rec.date_from <= self.date_to or \
                    self.date_from <= rec.date_to <= self.date_to:
                 raise ValidationError(u"هناك تداخل في التواريخ مع خارج دوام")

        for rec in schol_obj.search(search_domain):
            if rec.date_from <= self.date_from <= rec.date_to or \
                    rec.date_from <= self.date_to <= rec.date_to or \
                    self.date_from <= rec.date_from <= self.date_to or \
                    self.date_from <= rec.date_to <= self.date_to:
                raise ValidationError(u"هناك تداخل في التواريخ مع  ابتعاث")

    @api.one
    @api.constrains('heure_number')
    def check_heure_number(self):
        if self.heure_number > 7  :
            raise ValidationError(u"عدد الساعات يجب ان يكون أصغر من 7 ساعات")
        if self.heure_number > 0 and self.type_compensation == 'compensatory_leave' :
            raise ValidationError(u"عدد الساعات في إجازة تعويضية يكون صفر")


#       
