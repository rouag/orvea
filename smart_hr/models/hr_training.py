# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime, timedelta
import math
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

HOURS_PER_DAY = 7


class HrTraining(models.Model):
    _name = 'hr.training'
    _description = u'التدريب'

    @api.one
    @api.depends('line_ids')
    def _compute_info(self):
        self.number_participant = len(self.line_ids)

    name = fields.Char(string=' المسمى', required=1, states={'new': [('readonly', 0)]})
    number = fields.Char(string='رقم القرار', required=1, states={'new': [('readonly', 0)]})
    date = fields.Date(string=' تاريخ القرار', required=1, states={'new': [('readonly', 0)]})
    date_from = fields.Date(string='تاريخ من', required=1, states={'new': [('readonly', 0)]})
    date_to = fields.Date(string=' إلى', required=1, states={'new': [('readonly', 0)]})
    number_of_days = fields.Float(string=' المدة', readonly=1,compute='_compute_duration')
    experience = fields.Selection([('experience_directe', 'الخبرات‬  المباشرة'),
                              ('experience_in_directe', 'الخبرات الغير المباشرة'),
                              ],  string=' نوع الخبرة المكتسبة',required=1,states={'new': [('readonly', 0)]})
    department = fields.Char(string=' الجهة', required=1, states={'new': [('readonly', 0)]})
    place = fields.Many2one('res.city', string=u'المدينة ',required=1, states={'new': [('readonly', 0)]})
    number_place = fields.Integer(string='عدد المقاعد', required=1, states={'new': [('readonly', 0)]})
    number_participant = fields.Integer(string=' عدد المشتركين', store=True, readonly=True, compute='_compute_info')
    line_ids = fields.One2many('hr.candidates', 'training_id', string='المترشحين', readonly=1, states={'new': [('readonly', 0)]})
    
    state = fields.Selection([('new', 'جديد'),
                              ('candidat', 'الترشح'),
                              ('review', 'المراجعة'),
                              ('done', 'اعتمدت'),
                              ('refused', 'رفض'),
                              ('cancel', 'ملغاة'),
                              ], readonly=1, string='الحالة', default='new')
    job_trainings = fields.One2many('hr.job.training', 'type', string='job trainings')
    compute_weekends = fields.Boolean(string=u'احتساب عطلة نهاية الاسبوع')

    @api.one
    @api.depends('date_from', 'date_to','compute_weekends')
    def _compute_duration(self):
        if self.date_from and self.date_to:
            if self.compute_weekends:
                date_from = fields.Date.from_string(self.date_from)
                self.number_of_days = self.env['hr.smart.utils'].compute_duration(self.date_from, self.date_to)
            else:
                date_from = fields.Date.from_string(self.date_from)
                date_to = fields.Date.from_string(self.date_to)
                self.number_of_days = (date_to - date_from).days + 1

    @api.one
    @api.constrains('date_from')
    def check_order_chek_date(self):
        if self.date_from < datetime.today().strftime('%Y-%m-%d'):
            raise ValidationError(u" تاريخ التدريب يجب أن يكون أكبر من تاريخ إليوم")

    @api.onchange('date_to')
    def _onchange_date_to(self):
        date_from = self.date_from
        date_to = self.date_to
        if date_to < date_from:
            raise ValidationError(u'تاريخ بداية الدورة يجب ان يكون أصغر من تاريخ انتهاء الدورة')

    @api.one
    def action_candidat(self):
        self.state = 'candidat'

    @api.one
    def action_review(self):
        for line in self.line_ids:
            line.state='waiting'
        self.state = 'review'

    @api.one
    def action_done(self):
        list_done=[]
        for line in self.line_ids:
            if line.state!='cancel':
                line.state='done'
                type = "لقد تتمت الموافقة على طلب ترشحكم للدورة تدريبية رقم :"+" " + self.name.encode('utf-8')
                self.env['base.notification'].create({'title': u' إشعار بتدريب',
                                              'message': type,
                                              'user_id': line.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': self.id,
                                              'res_action': 'smart_hr.action_hr_training',})
                list_done.append(line.id)
               
            if line.state=='cancel':
                self.env['base.notification'].create({'title': u' إشعار بالرفض',
                                              'message': u' لقد تمت رفض الترشح للدورة التدريبية ',
                                              'user_id': line.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': self.id,
                                              'res_action': 'smart_hr.action_hr_training',})
                line.training_id=False
                
                
      
        
        self.state = 'done'
        
    @api.one
    def action_refused(self):
        self.state = 'refused'
    @api.one
    def action_cancel(self):
        self.state = 'cancel'
        
   
        
class HrTrainingType(models.Model):
    _name = 'hr.training.type'
    _description = u'أنواع التدريب'
    name = fields.Char(string=u'المسمى', required=True)


class HrCandidates(models.Model):
    _name = 'hr.candidates'
    _description = u'المترشحين'
    _rec_name = 'employee_id'
    _sql_constraints = [
        ('name_uniq', 'unique(employee_id, training_id)', 'هذا الموظف موجود بالدورة التدريبية!'),
        ]

    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), required=1)
    number = fields.Char(related='employee_id.number', store=True, readonly=True, string=' الرقم الوظيفي')
    job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True, string=' الوظيفة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True, string=' الادارة')
    training_id = fields.Many2one('hr.training', string=' الدورة')
    date_from = fields.Date(related='training_id.date_from', store=True, readonly=True)
    date_to = fields.Date(related='training_id.date_to', store=True, readonly=True)
    department = fields.Char(related='training_id.department', store=True, readonly=True)
    state = fields.Selection([('new', ' ارسال طلب'),
                             ('waiting', 'في إنتظار الإعتماد'),
                             ('cancel', 'رفض'),
                             ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')
    number_of_days = fields.Float(string=' المدة',related='training_id.number_of_days' )
    place = fields.Many2one(string=' المكان',related='training_id.place' )
    experience = fields.Selection([('experience_directe', 'الخبرات‬  المباشرة'),
                              ('experience_in_directe', 'الخبرات الغير المباشرة'),
                              ],  string=' نوع الخبرة المكتسبة',)
    cause = fields.Text(string = u'سبب الرفض')
   

    @api.onchange('training_id')
    def _onchange_training_id(self):
        if self.training_id:
            self.date_from = self.training_id.date_from
            self.date_to = self.training_id.date_to
            self.department = self.training_id.department
            self.experience=self.training_id.experience
            
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
       
        if self.employee_id:
            self.number = self.employee_id.number
            self.job_id = self.employee_id.job_id.id
            self.department_id = self.employee_id.department_id.id

    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_refuse(self):
        self.state = 'cancel'
    
    

    @api.one
    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        for candidate in self:
            try:
                train_obj = self.env['hr.training']
                effective_date_from = (datetime.strptime(candidate.date_from, DEFAULT_SERVER_DATE_FORMAT)).strftime(DEFAULT_SERVER_DATE_FORMAT)
                effective_date_to = (datetime.strptime(candidate.date_to, DEFAULT_SERVER_DATE_FORMAT)).strftime(DEFAULT_SERVER_DATE_FORMAT)
                for rec in train_obj.search([]):
                    if rec.date_from <= effective_date_from <= rec.date_to or \
                            rec.date_from <= effective_date_to <= rec.date_to or \
                            effective_date_from <= rec.date_from <= effective_date_to or \
                            effective_date_from <= rec.date_to <= effective_date_to:
                        for line in rec.line_ids:
                            if line.employee_id.id == candidate.employee_id.id and rec.id != self.training_id.id and line.state!='cancel':
                                raise ValidationError(u"هناك تداخل فى التواريخ مع قرار سابق فى التدريب")
            except:
                print 
# TODO: all conditions not work
#     @api.constrains('date_from', 'date_to')
#     def check_dates(self):
#         for train in self:
#             # Objects
#             dep_obj = self.env['hr.deputation']
#             train_obj = self.env['hr.training']
#             overtime_obj = self.env['hr.overtime']
#             hr_public_holiday_obj = self.env['hr.public.holiday']
#             # Variables
#             #days_before_after = train.city_id.days_before_after
#             # Calculate Effective Dates
#             effective_date_from = (datetime.strptime(train.date_from, DEFAULT_SERVER_DATE_FORMAT)).strftime(DEFAULT_SERVER_DATE_FORMAT)
#             effective_date_to = (datetime.strptime(train.date_to, DEFAULT_SERVER_DATE_FORMAT)).strftime(DEFAULT_SERVER_DATE_FORMAT)
#             # Check for incomplete data
#             if train.date_from > train.date_to:
#                 raise ValidationError(u'تاريخ بداية الدورة يجب ان يكون أصغر من تاريخ انتهاء الدورة')
#             # Check for eid
#             for public_holiday in hr_public_holiday_obj.search([]):
#                 if public_holiday.date_from <= effective_date_from <= public_holiday.date_to or \
#                         public_holiday.date_from <= effective_date_to <= public_holiday.date_to or \
#                         effective_date_from <= public_holiday.date_from <= effective_date_to or \
#                         effective_date_from <= public_holiday.date_to <= effective_date_to:
#                     raise ValidationError(u"هناك تداخل فى التواريخ مع اعياد و مناسبات رسمية")
#             # Check for any intersection with other decisions
#             for emp in train.employee_ids:
#                 # Overtime
#                 search_domain = [
#                     ('overtime_line_ids.employee_id', '=', emp.id),
#                     ('state', '!=', 'refuse'),
#                 ]
#                 for rec in overtime_obj.search(search_domain):
#                     for line in rec.overtime_line_ids:
#                         if (line.date_from <= effective_date_from <= line.date_to or \
#                                 line.date_from <= effective_date_to <= line.date_to or \
#                                 effective_date_from <= line.date_from <= effective_date_to or \
#                                 effective_date_from <= line.date_to <= effective_date_to) and \
#                                 line.employee_id == emp:
#                             raise ValidationError(u"هناك تداخل فى التواريخ مع قرار سابق فى خارج الدوام")
#                 # Leave
#                 search_domain = [
#                     ('employee_id', '=', emp.id),
#                     ('state', '!=', 'refuse'),
#                 ]
#                 # Training
#                 search_domain = [
#                     ('employee_ids', 'in', [emp.id]),
#                     ('id', '!=', train.id),
#                     ('state', '!=', 'refuse'),
#                 ]
#                 for rec in train_obj.search(search_domain):
#                     if rec.date_from <= effective_date_from <= rec.date_to or \
#                             rec.date_from <= effective_date_to <= rec.date_to or \
#                             effective_date_from <= rec.date_from <= effective_date_to or \
#                             effective_date_from <= rec.date_to <= effective_date_to:
#                         raise ValidationError(u"هناك تداخل فى التواريخ مع قرار سابق فى التدريب")
#                 # Deputation
#                 search_domain = [
#                     ('employee_id', '=', emp.id),
#                     ('state', '!=', 'refuse'),
#                 ]
#                 for rec in dep_obj.search(search_domain):
#                     if rec.date_from <= effective_date_from <= rec.date_to or \
#                             rec.date_from <= effective_date_to <= rec.date_to or \
#                             effective_date_from <= rec.date_from <= effective_date_to or \
#                             effective_date_from <= rec.date_to <= effective_date_to:
#                         raise ValidationError(u"هناك تداخل فى التواريخ مع قرار سابق فى الأنتداب")