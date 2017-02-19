# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
import base64
from tempfile import TemporaryFile
import csv
import time as time_date
from datetime import datetime, timedelta, time
from openerp.exceptions import ValidationError
from umalqurra.hijri_date import HijriDate
from openerp.addons.smart_base.util.time_util import float_time_convert
from openerp.addons.smart_base.util.time_util import time_float_convert
from openerp.addons.smart_base.util.time_util import float_time_convert_str
from openerp.addons.smart_base.util.umalqurra import *
from dateutil import relativedelta
from umalqurra.hijri import Umalqurra

FORMAT_TIME = '%H:%M:%S'


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    date_from = fields.Date('تاريخ من')
    date_to = fields.Date('إلى')
    schedule_id = fields.Many2one('hr.attendance.schedule', string='خطة الحضور والإنصراف', required=1)


class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    @api.onchange('dayofweek')
    def onchange_dayofweek(self):
        if self.dayofweek == '0':
            day = u'الأثنين'
        if self.dayofweek == '1':
            day = u'الثلاثاء'
        elif self.dayofweek == '2':
            day = u'الأربعاء'
        elif self.dayofweek == '3':
            day = u'الخميس'
        elif self.dayofweek == '4':
            day = u'الجمعة'
        elif self.dayofweek == '5':
            day = u'السبت'
        elif self.dayofweek == '6':
            day = u'الأحد'
        self.name = u'وردية يوم %s ' % day


class hr_attendance(models.Model):
    _inherit = 'hr.attendance'
    _order = 'name desc,id'

    id_emprinte = fields.Char(string=u'رقم ')
    mac_id = fields.Char(string=u'الآلة ')

    def _altern_si_so(self, cr, uid, ids, context=None):
        """  Rewrite this function to remove this test :
             Alternance sign_in/sign_out check.
             Previous (if exists) must be of opposite action.
             Next (if exists) must be of opposite action.
        """
        return True

    _constraints = [(_altern_si_so, 'Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', ['action'])]


class HrPlanPresence(models.Model):
    _name = 'hr.attendance.schedule'
    _inherit = ['mail.thread']
    _description = 'خطة الحضور والإنصراف'

    name = fields.Char(string=u'المسمى', required=1)
    late = fields.Float(string=u'عدد  دقائق التأخير المسموح بها')
    percent_late = fields.Float(string=u'ضارب تأخير ')
    leave = fields.Float(string=u'عدد  دقائق الإنصراف المبكر المسموح بها')
    percent_leave = fields.Float(string=u'ضارب الإنصراف المبكر  ',)
    min_sup_hour = fields.Float(string=u'الحد الادنى للوقت الاضافي بدقائق')
    max_sup_hour = fields.Float(string=u'الحد الأقصى للوقت الاضافي بدقائق')


class HrAttendanceImport(models.Model):
    _name = 'hr.attendance.import'
    _description = u'ملف الحضور والإنصراف'
    _order = 'id desc'
    _inherit = ['mail.thread']

    name = fields.Char(string='المسمى', readonly=1, states={'new': [('readonly', 0)]})
    description = fields.Text(string=' ملاحظات ', readonly=1, states={'new': [('readonly', 0)]})
    data = fields.Binary(string='الملف', required=1, readonly=1, states={'new': [('readonly', 0)]})
    data_name = fields.Char(string='الملف')
    create_uid = fields.Many2one('res.users', 'المستخدم', readonly=1)
    create_date = fields.Datetime(string='التاريخ', readonly=1, states={'new': [('readonly', 0)]})
    date = fields.Date(string='التاريخ', readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', 'جديد'), ('done', 'تم التحميل')], string='الحالة', readonly=1, default='new')

    def get_day_number(self, date):
        '''
        Return a day number from args date : this number must same in field selection used in model resource.calendar.attendance
        [('0','Monday'),('1','Tuesday'),('2','Wednesday'),('3','Thursday'),('4','Friday'),('5','Saturday'),('6','Sunday')]
        '''
        date_str = str(date).split('-')
        year = date_str[0]
        month = date_str[1]
        day = date_str[2]
        um = HijriDate(int(year), int(month), int(day), gr=True)
        if um.day_name_en in ('Monday', 'lundi'):
            day_number = 0
        elif um.day_name_en in ('Tuesday', 'mardi'):
            day_number = 1
        elif um.day_name_en in ('Wednesday', 'mercredi'):
            day_number = 2
        elif um.day_name_en in ('Thursday', 'jeudi'):
            day_number = 3
        elif um.day_name_en in ('Friday', 'vendredi'):
            day_number = 4
        elif um.day_name_en in ('Saturday', 'samedi'):
            day_number = 5
        elif um.day_name_en in ('Sunday', 'dimanche'):
            day_number = 6
        return str(day_number)

    def get_time_from_to_calendar(self, calendar_id, day):
        '''
        Get time from , time to , late , leave from resource calendar for a day given in args
        '''
        # TODO: if days not in resource.calendar.attendance for example vendredi and samedi it show error
        # must do this case
        calendar_attendance_obj = self.env['resource.calendar.attendance']
        calendar_attendance = calendar_attendance_obj.search([('calendar_id', '=', calendar_id), ('dayofweek', '=', day)])
        if not calendar_attendance:
            raise ValidationError(u"لا يمكن تحميل يوم الجمعة والسبت")
        calendar_attendance = calendar_attendance[0]
        calendar_hour_from = calendar_attendance.hour_from
        calendar_hour_to = calendar_attendance.hour_to
        hour_from_hour, hour_from_min = float_time_convert(calendar_hour_from)
        hour_to_hour, hour_to_min = float_time_convert(calendar_hour_to)
        time_from = time(int(hour_from_hour), int(hour_from_min), 0)
        time_to = time(int(hour_to_hour), int(hour_to_min), 0)
        late = calendar_attendance.calendar_id.schedule_id.late
        leave = calendar_attendance.calendar_id.schedule_id.leave
        datetime_from_max = datetime(100, 1, 1, int(hour_from_hour), int(hour_from_min), 0)
        datetime_from_max = datetime_from_max + timedelta(0, int(late) * 60.0)
        time_from_max = datetime_from_max.time()
        datetime_to_min = datetime(100, 1, 1, int(hour_to_hour), int(hour_to_min), 0)
        datetime_to_min = datetime_to_min - timedelta(0, int(leave) * 60.0)
        time_to_min = datetime_to_min.time()
        return time_from, time_to, late, time_from_max, time_to_min

    @api.multi
    def close_day(self):
        u'''
        غلق اليوم يتم هنا تجميع التأخيرات والغيابات الغير مبرره والخروج المبكر والساعات الإضافية ليوم معين
         ثم يتم إنشاء نماذج لكل عنصر منها وتبقى في إنتظار الإعتماد  .لا  يحتسب تأخير أو خروج مبكر أو غياب
        أو ساعة إضافية إلا بعد الإعتماد من صاحب الصلاحية
        '''
        # date = current date
        # date = datetime.now().date()
        date = self.date
        employee_obj = self.env['hr.employee']
        report_day_obj = self.env['hr.attendance.report_day']
        attendance_check = self.env['hr.attendance.check']
        # first delete all actions for this day
        report_day_ids = report_day_obj.search([('date', '=', date)])
        report_day_ids.unlink()
        #
        for employee in employee_obj.search([]):
            day = self.get_day_number(date)
            time_from, time_to, late, time_from_max, time_to_min = self.get_time_from_to_calendar(employee.calendar_id.id, day)
            self.chek_sign_in(date, employee.id, time_to, datetime.now())
            self.chek_sign_out(date, employee.id, time_to, datetime.now())
        # create attendance.check
        retards = report_day_obj.search([('date', '=', date), ('action', '=', 'retard')])
        leaves = report_day_obj.search([('date', '=', date), ('action', '=', 'leave')])
        hour_supps = report_day_obj.search([('date', '=', date), ('action', '=', 'hour_supp')])
        absences = report_day_obj.search([('date', '=', date), ('action', '=', 'absence')])
        # retard
        for retard in retards:
            val = {'employee_id': retard.employee_id.id,
                   'number': retard.employee_id.number,
                   'department_id': retard.employee_id.job_id.department_id.id,
                   'job_id': retard.employee_id.job_id.id,
                   'grade_id': retard.employee_id.job_id.grade_id.id,
                   'type': 'retard',
                   'date': retard.date,
                   'delay': retard.delay_retard}
            attendance_check.create(val)
        # leave
        for leave in leaves:
            val = {'employee_id': leave.employee_id.id,
                   'number': leave.employee_id.number,
                   'department_id': leave.employee_id.job_id.department_id.id,
                   'job_id': leave.employee_id.job_id.id,
                   'grade_id': leave.employee_id.job_id.grade_id.id,
                   'type': 'leave',
                   'date': leave.date,
                   'delay': leave.delay_leave}
            attendance_check.create(val)
        # hour_supp
        for hour_supp in hour_supps:
            val = {'employee_id': hour_supp.employee_id.id,
                   'number': hour_supp.employee_id.number,
                   'department_id': hour_supp.employee_id.job_id.department_id.id,
                   'job_id': hour_supp.employee_id.job_id.id,
                   'grade_id': hour_supp.employee_id.job_id.grade_id.id,
                   'type': 'hour_supp',
                   'date': hour_supp.date,
                   'delay': hour_supp.delay_hours_supp}
            attendance_check.create(val)
        # absences
        for absence in absences:
            val = {'employee_id': absence.employee_id.id,
                   'number': absence.employee_id.number,
                   'department_id': absence.employee_id.job_id.department_id.id,
                   'job_id': absence.employee_id.job_id.id,
                   'grade_id': absence.employee_id.job_id.grade_id.id,
                   'type': 'absence',
                   'date': absence.date,
                   'delay': absence.delay_absence}
            attendance_check.create(val)
        return True

    def chek_sign_in(self, date, employee_id, latest_time, latest_datetime_import):
        '''
        التحقق من بصمة أو بصمات الدخول لكل موظف أثناء كل عملية تحديث لسجل الحضور و الإنصراف
        :param date:
        :param employee_id:
        :param latest_time: the latest hours for attendance  imported from file
        '''
        report_day_obj = self.env['hr.attendance.report_day']
        employee_obj = self.env['hr.employee']
        attendance_obj = self.env['hr.attendance']
        #
        date_start = datetime.strptime(date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        date_stop = datetime.strptime(date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        employee = employee_obj.browse(employee_id)
        day = self.get_day_number(date)
        time_from, time_to, late, time_from_max, time_to_min = self.get_time_from_to_calendar(employee.calendar_id.id, day)

        first_time = time_float_convert(time_from)
        latest_time = time_float_convert(latest_time)

        employee_attendances_sign_in = attendance_obj.search([('employee_id', '=', employee_id),
                                                              ('action', '=', 'sign_in'),
                                                              ('name', '>=', str(date_start)),
                                                              ('name', '<=', str(date_stop))])
        if not employee_attendances_sign_in:
            # search in طلبات الإستئذان
            authorization_ids = employee.get_authorization_by_date(date, first_time, latest_time)
            if authorization_ids:
                authorization = authorization_ids[0]
                vals = {'employee_id': employee_id,
                        'hour_calendar': first_time,
                        'date': date,
                        'action': 'absence_justified',
                        'description': u'طلب إستئذان رقم %s . من الساعة %s إلى %s  ' % (authorization.name, float_time_convert_str(authorization.hour_from), float_time_convert_str(authorization.hour_to)),
                        'latest_date_import': latest_datetime_import
                        }
                report_day_obj.create(vals)
                return True

            # search in hr_holidays
            holidays_ids = employee.get_holidays_by_date(date)
            if holidays_ids:
                holiday = holidays_ids[0]
                vals = {'employee_id': employee_id,
                        'hour_calendar': first_time,
                        'date': date,
                        'action': 'absence_justified',
                        'description': u'إجازة %s  من تاريخ %s إلى %s ' % (holiday.holiday_status_id.name, holiday.date_from, holiday.date_to),
                        'latest_date_import': latest_datetime_import
                        }
                report_day_obj.create(vals)
                return True

            # search in training
            training_ids = employee.get_training_by_date(date)
            if training_ids:
                training = training_ids[0]
                vals = {'employee_id': employee_id,
                        'hour_calendar': first_time,
                        'date': date,
                        'action': 'absence_justified',
                        'description': u'دورة تدريبية %s  من تاريخ %s إلى %s ' % (training.training_id.name, training.date_from, training.date_to),
                        'latest_date_import': latest_datetime_import
                        }
                report_day_obj.create(vals)
                return True
            # else create غياب غير مبرر
            current_time = datetime.now().time().strftime(FORMAT_TIME)
            if datetime.now().time() >= time_to:
                current_time = str(time_to)
            delay_absence = datetime.strptime(current_time, FORMAT_TIME) - datetime.strptime(str(time_from), FORMAT_TIME)
            delay_absence_seconds = delay_absence.seconds
            delay_absence = delay_absence_seconds / 3600.0
            vals = {'employee_id': employee_id,
                    'hour_calendar': first_time,
                    'hour_calendar_to': False,
                    'hour_attendance': False,
                    'delay_absence': delay_absence,
                    'date': date,
                    'action': 'absence',
                    'description': u'الموظف لم يسجل دخوله',
                    'latest_date_import': latest_datetime_import
                    }
            report_day_obj.create(vals)
        else:
            first_sign_in = employee_attendances_sign_in[-1]
            first_sign_in_time = datetime.strptime(first_sign_in.name, '%Y-%m-%d %H:%M:%S').time()
            if first_sign_in_time > time_from_max:
                # إذا كان للموظف إستئذان يجب احتساب وقت التأخير بداية من  وقت نهاية فترة الإستئذان
                sign_in_time_start = time_from
                authorization_ids = employee.get_authorization_by_date(date, first_time, latest_time)
                if authorization_ids:
                    # إذا كان لديه إستئذان يجب إنشاء غياب مبرر واحتساب أخر وقت  دخوله بعد الإستئذان
                    authorization = authorization_ids[0]
                    vals = {'employee_id': employee_id,
                            'hour_calendar': first_time,
                            'date': date,
                            'action': 'absence_justified',
                            'description': u'طلب إستئذان رقم %s . من الساعة %s إلى %s  ' % (authorization.name, float_time_convert_str(authorization.hour_from), float_time_convert_str(authorization.hour_to)),
                            'latest_date_import': latest_datetime_import
                            }
                    report_day_obj.create(vals)
                    hour_start, min_start = float_time_convert(authorization.hour_to)
                    sign_in_time_start = time(int(hour_start), int(min_start), 0)
                # create retard action
                delay_retard = datetime.strptime(str(first_sign_in_time), FORMAT_TIME) - datetime.strptime(str(sign_in_time_start), FORMAT_TIME)
                delay_retard_seconds = delay_retard.seconds
                delay_retard = delay_retard_seconds / 3600.0
                vals = {'employee_id': employee.id,
                        'hour_calendar': time_float_convert(sign_in_time_start),
                        'hour_attendance': time_float_convert(first_sign_in_time),
                        'delay_retard': delay_retard,
                        'date': date,
                        'action': 'retard',
                        'latest_date_import': latest_datetime_import}
                report_day_obj.create(vals)

        return True

    def chek_sign_out(self, date, employee_id, latest_time, latest_date_import):
        '''
        التحقق من بصمة أو بصمات الخروج لكل موظف أثناء كل عملية تحديث لسجل الحضور و الإنصراف
        :param date:
        :param employee_id:
        :param first_time: the latest hours for attendance (from from attendance.schedule)  ex 14:30
        :param latest_time: the latest hours for attendance  imported from file
        '''
        report_day_obj = self.env['hr.attendance.report_day']
        employee_obj = self.env['hr.employee']
        attendance_obj = self.env['hr.attendance']
        #
        date_start = datetime.strptime(date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        date_stop = datetime.strptime(date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        employee = employee_obj.browse(employee_id)
        day = self.get_day_number(date)
        time_from, time_to, late, time_from_max, time_to_min = self.get_time_from_to_calendar(employee.calendar_id.id, day)
        # time_to = time_float_convert(time_to)
        latest_time = time_float_convert(latest_time)
        current_time = datetime.now().time()
        #
        employee_attendances_sign_out = attendance_obj.search([('employee_id', '=', employee.id),
                                                               ('action', '=', 'sign_out'),
                                                               ('name', '>=', str(date_start)),
                                                               ('name', '<=', str(date_stop))])

        # إذا كان الوقت الحالي أكبر أو يساوي وقت الخروج الموجود في الوردية
        if current_time >= time_to:
            if not employee_attendances_sign_out:
                vals = {'employee_id': employee_id,
                        'hour_calendar_to': time_float_convert(time_to),
                        'date': date,
                        'action': 'no_leave',
                        'description': u'لم يسجل بصمة الخروج',
                        'latest_date_import': latest_date_import
                        }
                report_day_obj.create(vals)
            else:
                last_sign_out = employee_attendances_sign_out[0]
                last_sign_out_time = datetime.strptime(last_sign_out.name, '%Y-%m-%d %H:%M:%S').time()
                if last_sign_out_time < time_to_min:
                    delay_leave = datetime.strptime(str(time_to), FORMAT_TIME) - datetime.strptime(str(last_sign_out_time), FORMAT_TIME)
                    delay_leave_seconds = delay_leave.seconds
                    delay_leave = delay_leave_seconds / 3600.0
                    vals = {'employee_id': employee.id,
                            'hour_calendar_to': time_float_convert(time_to),
                            'hour_attendance': time_float_convert(last_sign_out_time),
                            'delay_leave': delay_leave,
                            'date': date,
                            'action': 'leave',
                            'latest_date_import': latest_date_import}
                    report_day_obj.create(vals)
                # احتساب وقت إضافي
                elif last_sign_out_time > time_to:
                    delay_hours_supp = datetime.strptime(str(last_sign_out_time), FORMAT_TIME) - datetime.strptime(str(time_to), FORMAT_TIME)
                    min_sup_hour = employee.calendar_id.schedule_id.min_sup_hour * 60.0
                    max_sup_hour = employee.calendar_id.schedule_id.max_sup_hour * 60.0
                    delay_hours_supp = delay_hours_supp.seconds
                    if delay_hours_supp > min_sup_hour:
                        if delay_hours_supp > max_sup_hour:
                            delay_hours_supp = max_sup_hour
                        vals = {'employee_id': employee.id,
                                'hour_attendance': time_float_convert(last_sign_out_time),
                                'hour_calendar_to': time_float_convert(time_to),
                                'delay_hours_supp': delay_hours_supp / 3600.0,
                                'date': date,
                                'action': 'hour_supp',
                                'latest_date_import': latest_date_import}
                        report_day_obj.create(vals)
        # إذا  لم يكن كذلك يجب التثبت إن كان هناك دخول وخروج أثناء  فترة العمل
        for sign_out in employee_attendances_sign_out:
            sign_out_time = datetime.strptime(sign_out.name, '%Y-%m-%d %H:%M:%S').time()
            # this is a sign_out we must search the sign_in for this sign_out
            attendances_sign_in = attendance_obj.search([('employee_id', '=', employee.id),
                                                        ('action', '=', 'sign_in'),
                                                        ('name', '>=', str(date_start)),
                                                        ('name', '<=', str(date_stop)),
                                                        ('id', '>', sign_out.id)])
            if not attendances_sign_in:
                # nothing todo
                continue
            else:
                sign_in = attendances_sign_in[-1]
                sign_in_time = datetime.strptime(sign_in.name, '%Y-%m-%d %H:%M:%S').time()
                # إذا كان لديه إستئذان يجب إنشاء غياب مبرر واحتساب أخر وقت  دخوله بعد الإستئذان
                sign_in_time_after_authorization = sign_in_time
                authorization_ids = employee.get_authorization_by_date(date, time_float_convert(sign_out_time), time_float_convert(sign_in_time))
                if authorization_ids:
                    authorization = authorization_ids[0]
                    vals = {'employee_id': employee_id,
                            'hour_calendar': time_float_convert(sign_in_time),
                            'date': date,
                            'action': 'absence_justified',
                            'description': u'طلب إستئذان رقم %s . من الساعة %s إلى %s  ' % (authorization.name, float_time_convert_str(authorization.hour_from), float_time_convert_str(authorization.hour_to)),
                            'latest_date_import': latest_date_import
                            }
                    report_day_obj.create(vals)
                    hour_start, min_start = float_time_convert(authorization.hour_to)
                    sign_in_time_after_authorization = time(int(hour_start), int(min_start), 0)
                    # احتساب التأخر إذا عاد متأخراً بعد الإستئذان
                    if sign_in_time > sign_in_time_after_authorization:
                        # create retard action
                        delay_retard = datetime.strptime(str(sign_in_time), FORMAT_TIME) - datetime.strptime(str(sign_in_time_after_authorization), FORMAT_TIME)
                        delay_retard_seconds = delay_retard.seconds
                        delay_retard = delay_retard_seconds / 3600.0
                        vals = {'employee_id': employee.id,
                                'hour_calendar': time_float_convert(sign_in_time_after_authorization),
                                'hour_attendance': time_float_convert(sign_in_time),
                                'delay_retard': delay_retard,
                                'date': date,
                                'action': 'retard',
                                'latest_date_import': latest_date_import}
                        report_day_obj.create(vals)
                # إذا لم يكن هناك إستئذان يعتبر غياب غير مبرر
                else:
                    delay_absence = datetime.strptime(str(sign_in_time), FORMAT_TIME) - datetime.strptime(str(sign_out_time), FORMAT_TIME)
                    delay_absence_seconds = delay_absence.seconds
                    delay_absence = delay_absence_seconds / 3600.0
                    vals = {'employee_id': employee_id,
                            'hour_calendar': time_float_convert(sign_in_time),
                            'hour_calendar_to': time_float_convert(sign_out_time),
                            'hour_attendance': time_float_convert(sign_in_time),
                            'delay_absence': delay_absence,
                            'date': date,
                            'action': 'absence',
                            'description': u'خروج الساعة %s وعودة الساعة %s دون إستئذان' % (str(sign_out_time), str(sign_in_time)),
                            'latest_date_import': latest_date_import
                            }
                    report_day_obj.create(vals)
        return True

    def chek_import_attendance(self, date):
        employee_obj = self.env['hr.employee']
        attendance_obj = self.env['hr.attendance']
        report_day_obj = self.env['hr.attendance.report_day']
        date_start = datetime.strptime(date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        date_stop = datetime.strptime(date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        # first delete all actions for this day
        report_day_ids = report_day_obj.search([])
        report_day_ids.unlink()
        # get latest time for attendence
        all_attendances = attendance_obj.search([('name', '>=', str(date_start)), ('name', '<=', str(date_stop))])
        latest_time = datetime.strptime(all_attendances[0].name, '%Y-%m-%d %H:%M:%S').time()
        # check for each employee
        employees = employee_obj.search([('employee_state', '=', 'employee')])
        for employee in employees:
            if not employee.calendar_id:
                raise ValidationError(u"يجب تحديد الورديّات للموظف %s " % employee.name)

            self.chek_sign_in(date, employee.id, latest_time, all_attendances[0].name)
            self.chek_sign_out(date, employee.id, latest_time, all_attendances[0].name)

        return True

    @api.multi
    def import_attendance(self):
        '''
          تحديث سجل الحضور و الإنصراف
        '''
        quotechar = '"'
        delimiter = ','
        fileobj = TemporaryFile('w+')
        fileobj.write((base64.decodestring(self.data)))
        fileobj.seek(0)
        reader = csv.DictReader(fileobj, quotechar=str(quotechar), delimiter=str(delimiter))
        all_attendances_ids = []
        # le fichier doit etre un pointage pour une seule journée.
        all_dates = set()
        for row in reader:
            date = row['trndatetime2'].split(' ')[0]
            all_dates.add(date)
        if len(all_dates) != 1:
            raise ValidationError(u"الحضور و الإنصراف يجب أن يكون ليوم واحد")
        fileobj.seek(0)
        for row in reader:
            print '----row------', row
            employee = self.env['hr.employee'].search([('number', '=', str(row['empid'].strip(" ")))])
            if employee:
                if str(row['TrnType']) == '1':
                    action = 'sign_in'
                else:
                    action = 'sign_out'
                hr_attendance_val = {'employee_id': employee.id,
                                     'name': row['trndatetime2'],
                                     'action': action,
                                     'mac_id': row['MacName']}
                hr_attendance = self.env['hr.attendance'].create(hr_attendance_val)
                all_attendances_ids.append(hr_attendance.id)

            else:
                message = u"الموظف رقم %s غير موجود في قاعدة البيانات" % row['empid']
                self.message_post(message)

        self.chek_import_attendance(list(all_dates)[0])

        self.state = 'done'
        return True


class HrAttendanceReportDay(models.Model):
    _name = 'hr.attendance.report_day'
    u'''
      التأخيرات والغيابات الغير مبرره والخروج المبكر والساعات الإضافية تستعمل في لوحة المؤشرات
     ويتم تحديثها بعد كل عملية تحديث لسجل الحضور والإنصراف
    '''

    employee_id = fields.Many2one('hr.employee', string='الموظف')
    hour_calendar = fields.Float(string='وقت الدخول')
    hour_calendar_to = fields.Float(string='وقت الخروج')
    hour_attendance = fields.Float(string='وقت البصمة')
    delay_retard = fields.Float(string='المدة')
    delay_leave = fields.Float(string='المدة')
    delay_absence = fields.Float(string='المدة')
    delay_hours_supp = fields.Float(string='المدة')
    date = fields.Date(string='التاريخ')
    latest_date_import = fields.Datetime(string='وقت أخر تحديث')
    action = fields.Selection([('retard', 'تأخير'),
                               ('leave', 'خروج مبكر'),
                               ('no_leave', 'لم يسجل بصمة الخروج'),
                               ('absence_justified', 'غياب مبرر'),
                               ('absence', 'غياب'),
                               ('hour_supp', 'وقت إضافي')], string='الحالة')
    description = fields.Char(string='السبب')


class HrAttendanceCheck(models.Model):
    u'''
     يتم هنا تجميع التأخيرات والغيابات الغير مبرره والخروج المبكر والساعات الإضافية ليوم معين وتبقى في إنتظار الإعتماد
    لا  يحتسب تأخير أو خروج مبكر أو غياب أو ساعة إضافية إلا بعد الإعتماد من صاحب الصلاحية    '''
    _name = 'hr.attendance.check'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = 'ساعات التأخير و الخروج المبكر'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1, readonly=1)
    number = fields.Char(string='الرقم الوظيفي', readonly=1)
    department_id = fields.Many2one('hr.department', string='الادارة', readonly=1)
    job_id = fields.Many2one('hr.job', string='الوظيفة', readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', readonly=1)
    description = fields.Text(string=' ملاحظات ')
    state = fields.Selection([('new', 'تدقيق'),
                              ('cancel', 'ملغى'),
                              ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')
    type = fields.Selection([('leave', 'خروج مبكر'),
                             ('retard', 'تأخير'),
                             ('hour_supp', 'وقت إضافي'),
                             ('absence', 'غياب'),
                             ], string='النوع', readonly=1)
    date = fields.Date(string='التاريخ', required=1, readonly=1)
    delay = fields.Float(string='المدة', readonly=1)

    @api.multi
    def action_done(self):
        self.state = 'done'
        # check if all is done create a summary_report for this day
        checks = self.search([('date', '=', self.date), ('state', '=', 'new')])
        if not checks:
            self.create_summary_report(self.date)

    @api.one
    def action_refuse(self):
        self.state = 'cancel'
        # check if all is done create a summary_report for this day
        checks = self.search([('date', '=', self.date), ('state', '=', 'new')])
        if not checks:
            self.create_summary_report(self.date)

    def create_summary_report(self, date):
        # search old day closed
        employee_obj = self.env['hr.employee']
        attendance_obj = self.env['hr.attendance']
        attendance_check_obj = self.env['hr.attendance.check']
        summary_obj = self.env['hr.attendance.summary']

        date_start = datetime.strptime(date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        date_stop = datetime.strptime(date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        # check for each employee
        employees = employee_obj.search([('employee_state', '=', 'employee')])
        for employee in employees:
            val = {'employee_id': employee.id,
                   'number': employee.number,
                   'department_id': employee.job_id.department_id.id,
                   'job_id': employee.job_id.id,
                   'grade_id': employee.job_id.grade_id.id,
                   'date': date}
            # get hour_start
            employee_attendances_sign_in = attendance_obj.search([('employee_id', '=', employee.id),
                                                                  ('action', '=', 'sign_in'),
                                                                  ('name', '>=', str(date_start)),
                                                                  ('name', '<=', str(date_stop))])
            if employee_attendances_sign_in:
                first_sign_in = employee_attendances_sign_in[-1]
                first_sign_in_time = datetime.strptime(first_sign_in.name, '%Y-%m-%d %H:%M:%S').time()
                val.update({'hour_start': time_float_convert(first_sign_in_time)})
            # get hour_stop
            employee_attendances_sign_out = attendance_obj.search([('employee_id', '=', employee.id),
                                                                  ('action', '=', 'sign_out'),
                                                                  ('name', '>=', str(date_start)),
                                                                  ('name', '<=', str(date_stop))])
            if employee_attendances_sign_out:
                last_sign_out = employee_attendances_sign_out[0]
                last_sign_out_time = datetime.strptime(last_sign_out.name, '%Y-%m-%d %H:%M:%S').time()
                val.update({'hour_stop': time_float_convert(last_sign_out_time)})
            # get retard
            retard = leave = hours_supp = absence = 0.0
            attendances = attendance_check_obj.search([('employee_id', '=', employee.id), ('state', '=', 'done'), ('date', '=', date)])
            for attendance in attendances:
                if attendance.type == 'retard':
                    retard += attendance.delay
                elif attendance.type == 'leave':
                    leave += attendance.delay
                elif attendance.type == 'hour_supp':
                    hours_supp += attendance.delay
                elif attendance.type == 'absence':
                    absence += attendance.delay
            val.update({'retard': retard, 'leave': leave, 'hours_supp': hours_supp, 'absence': absence})
            # get authorization
            authorization_delay = 0.0
            authorization_ids = employee.get_authorization_by_date(date)
            for authorization in authorization_ids:
                authorization_delay += authorization.hour_number
            val.update({'authorization': authorization_delay})
            # get holidays
            holidays_ids = employee.get_holidays_by_date(date)
            holiday_nb = len(holidays_ids)
            val.update({'holiday': holiday_nb})
            # create report summary
            summary_obj.create(val)
        return True


class HrAttendanceSummary(models.Model):
    _name = 'hr.attendance.summary'
    _order = 'id desc'
    _description = u'الخلاصة اليومية للغيابات والتأخير'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1, readonly=1)
    number = fields.Char(string='الرقم الوظيفي', readonly=1)
    department_id = fields.Many2one('hr.department', string='الادارة', readonly=1)
    job_id = fields.Many2one('hr.job', string='الوظيفة', readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', readonly=1)
    date = fields.Date(string='التاريخ', required=1, readonly=1)
    hour_start = fields.Float(string='الدخول')
    hour_stop = fields.Float(string='الخروج')
    retard = fields.Float(string='تأخير')
    leave = fields.Float(string='خروج مبكر')
    hours_supp = fields.Float(string='وقت إضافي')
    authorization = fields.Float(string='إستئذان')
    holidays = fields.Float(string='إجازة')
    absence = fields.Float(string='غياب')


class HrMonthlySummary(models.Model):
    _name = 'hr.monthly.summary'
    _inherit = ['mail.thread']
    _description = u'الخلاصة الشهرية للغيابات والتأخير'
    _order = 'id desc'

    @api.multi
    def get_default_month(self):
        return get_current_month_hijri(HijriDate)

    name = fields.Selection(MONTHS, string='الشهر', required=1, readonly=1, states={'new': [('readonly', 0)]}, default=get_default_month)
    date = fields.Date(string='التاريخ', required=1, readonly=1, states={'new': [('readonly', 0)]}, default=fields.Datetime.now())
    date_from = fields.Date('تاريخ من', readonly=1, states={'new': [('readonly', 0)]})
    date_to = fields.Date('إلى', readonly=1, states={'new': [('readonly', 0)]})
    description = fields.Text(string=' ملاحظات ')
    state = fields.Selection([('new', 'مسودة'),
                              ('waiting', 'في إنتظار الإعتماد'),
                              ('cancel', 'مرفوض'),
                              ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')
    line_ids = fields.One2many('hr.monthly.summary.line', 'monthly_summary_id', string='التفاصيل', readonly=1, states={'new': [('readonly', 0)]})

    @api.onchange('name')
    def onchange_month(self):
        if self.name:
            self.date_from = get_hijri_month_start(HijriDate, Umalqurra, self.name)
            self.date_to = get_hijri_month_end(HijriDate, Umalqurra, self.name)
            line_ids = []
            # delete current line
            self.line_ids.unlink()
            # get all line
            attendance_summary_obj = self.env['hr.attendance.summary']
            all_attendances = attendance_summary_obj.search([('date', '>=', self.date_from), ('date', '<=', self.date_to)])
            print '-----all_attendances-----', all_attendances
            monthly_summary = {}
            for attendance in all_attendances:
                if attendance.retard or attendance.leave or attendance.absence:
                    key = attendance.employee_id
                    if key not in monthly_summary:
                        monthly_summary[key] = {'retard': 0.0, 'leave': 0.0, 'absence': 0.0}
                    if attendance.retard:
                        monthly_summary[key]['retard'] += attendance.retard
                    if attendance.leave:
                        monthly_summary[key]['leave'] += attendance.leave
                    if attendance.absence:
                        monthly_summary[key]['absence'] += attendance.absence
            # create line in summary
            request_transfer_obj = self.env['hr.request.transfer']
            for employee in monthly_summary:
                retard = monthly_summary[employee]['retard']
                leave = monthly_summary[employee]['leave']
                absence = monthly_summary[employee]['absence']
                balance_previous_retard = 0.0
                balance_previous_absence = 0.0
                balance_forward_retard = 0.0
                balance_forward_absence = 0.0
                days_retard = 0.0
                days_absence = 0.0
                delay_hours = retard + leave
                delay_request = 0.0
                # check طلبات تحويل ساعات التأخير
                request_transfers = request_transfer_obj.search([('state', '=', 'done'), ('employee_id', '=', employee.id), ('date', '>=', self.date_from), ('date', '<=', self.date_to)])
                for request in request_transfers:
                    delay_request += request.number_request
                # check رصيد الشهر السابق
                monthly_summary_line_obj = self.env['hr.monthly.summary.line']
                summary_lines = monthly_summary_line_obj.search([('employee_id', '=', employee.id)])
                if summary_lines:
                    balance_previous_retard = summary_lines[0].balance_forward_retard
                    balance_previous_absence = summary_lines[0].balance_forward_absence
                # create line if employee have a delay_hours or balance_previous
                if delay_hours or absence or balance_previous_retard or balance_previous_absence:
                    balance_forward_retard = delay_hours + balance_previous_retard - delay_request
                    balance_forward_absence = absence + balance_previous_absence
                    if balance_forward_retard >= 7:
                        days_retard += int(balance_forward_retard / 7)
                        balance_forward_retard = balance_forward_retard % 7
                    if balance_forward_absence >= 7:
                        days_absence += int(balance_forward_absence / 7)
                        balance_forward_absence = balance_forward_absence % 7
                    line = {'monthly_summary_id': self.id,
                            'employee_id': employee.id,
                            'department_id': employee.job_id.department_id,
                            'job_id': employee.job_id,
                            'grade_id': employee.job_id.grade_id,
                            'retard': retard,
                            'leave': leave,
                            'absence': absence,
                            'delay_hours': delay_hours,
                            'delay_request': delay_request,
                            'days_retard': days_retard,
                            'days_absence': days_absence,
                            'balance_previous_retard': balance_previous_retard,
                            'balance_previous_absence': balance_previous_absence,
                            'balance_forward_retard': balance_forward_retard,
                            'balance_forward_absence': balance_forward_absence,
                            }
                    line_ids.append(line)
            self.line_ids = line_ids

    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_refuse(self):
        self.state = 'cancel'


class HrMonthlySummaryLine(models.Model):
    _name = 'hr.monthly.summary.line'
    _order = 'id desc'
    _rec_name = 'employee_id'

    monthly_summary_id = fields.Many2one('hr.monthly.summary', string='الخلاصة الشهرية', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1, readonly=1)
    department_id = fields.Many2one('hr.department', string='الادارة', readonly=1)
    job_id = fields.Many2one('hr.job', string='الوظيفة', readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', readonly=1)
    balance_previous_retard = fields.Float(string='رصيد الشهر السابق تأخير وخروج (س.)')
    balance_previous_absence = fields.Float(string='رصيد الشهر السابق غياب (س.)')
    retard = fields.Float(string=' تأخير (س)')
    leave = fields.Float(string='خروج مبكر(س)')
    absence = fields.Float(string='غياب(س)')
    delay_hours = fields.Float(string='المجموع (س)')
    delay_request = fields.Float(string='تحويل(س)')
    days_retard = fields.Float(string='أيام خصم التأخير')
    days_absence = fields.Float(string='أيام خصم الغياب')
    balance_forward_retard = fields.Float(string='الرصيد المرحل تأخير وخروج (س.)')
    balance_forward_absence = fields.Float(string='الرصيد المرحل غياب (س.)')
