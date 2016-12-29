# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
import base64
from tempfile import TemporaryFile
import csv
from datetime import datetime, timedelta, time
from openerp.exceptions import ValidationError
from umalqurra.hijri_date import HijriDate
from openerp.addons.smart_base.util.time_util import float_time_convert
from openerp.addons.smart_base.util.time_util import time_float_convert

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
    _inherit = ['mail.thread']

    name = fields.Char(string='المسمى', readonly=1, states={'new': [('readonly', 0)]})
    description = fields.Text(string=' ملاحظات ', readonly=1, states={'new': [('readonly', 0)]})
    data = fields.Binary(string='الملف', required=1, readonly=1, states={'new': [('readonly', 0)]})
    create_uid = fields.Many2one('res.users', 'المستخدم', readonly=1)
    create_date = fields.Datetime(string='التاريخ', readonly=1, states={'new': [('readonly', 0)]})
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
        if um.day_name_en == 'lundi':  # Monday
            day_number = 0
        elif um.day_name_en == 'Tuesday':
            day_number = 1
        elif um.day_name_en == 'Wednesday':
            day_number = 2
        elif um.day_name_en == 'Thursday':
            day_number = 3
        elif um.day_name_en == 'Friday':
            day_number = 4
        elif um.day_name_en == 'Saturday':
            day_number = 5
        elif um.day_name_en == 'Sunday':
            day_number = 6
        return str(day_number)

    def get_time_from_to_calendar(self, calendar_id, day):
        '''
        Get time from , time to , late , leave from resource calendar for a day given in args
        '''
        calendar_attendance_obj = self.env['resource.calendar.attendance']
        calendar_attendance = calendar_attendance_obj.search([('calendar_id', '=', calendar_id), ('dayofweek', '=', day)])
        calendar_attendance = calendar_attendance[0]
        calendar_hour_from = calendar_attendance.hour_from
        calendar_hour_to = calendar_attendance.hour_to
        hour_from_hour, hour_from_min = float_time_convert(calendar_hour_from)
        hour_to_hour, hour_to_min = float_time_convert(calendar_hour_to)
        time_from = time(int(hour_from_hour), int(hour_from_min), 0)
        time_to = time(int(hour_to_hour), int(hour_to_min), 0)
        late = calendar_attendance.calendar_id.schedule_id.late
        leave = calendar_attendance.calendar_id.schedule_id.leave
        time_from_max = time(int(hour_from_hour), int(hour_from_min) + int(late), 0)
        time_to_min = time(int(hour_to_hour), int(hour_to_min) - int(leave), 0)
        # TODO: FixMe  dont use  hour+late or  hour-leave because minute must be in 0..59 must use timedelta
        return time_from, time_to, late, time_from_max, time_to_min

    def close_day(self, date):
        employee_obj = self.env['hr.employee']
        for employee in employee_obj.search([]):
            day = self.get_day_number(date)
            time_from, time_to, late, time_from_max, time_to_min = self.get_time_from_to_calendar(employee.calendar_id.id, day)
            self.chek_sign_in(date, employee.id, time_to, datetime.now())
            self.chek_sign_out(date, employee.id, time_to, datetime.now())
        # create الاشعارات
        
        
        return  True

    def chek_sign_in(self, date, employee_id, latest_time, latest_datetime_import):
        '''
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
                        'description': u'طلب إستئذان رقم %s . من الساعة %s إلى %s  ' % (authorization.name, authorization.hour_from, authorization.hour_to),
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
            vals = {'employee_id': employee_id,
                    'hour_calendar': first_time,
                    'date': date,
                    'action': 'absence',
                    'description': u'غياب غير مبرر',
                    'latest_date_import': latest_datetime_import
                    }
            report_day_obj.create(vals)
            print '-------no attendance in ', employee.name

        else:
            first_sign_in = employee_attendances_sign_in[-1]
            first_sign_in_time = datetime.strptime(first_sign_in.name, '%Y-%m-%d %H:%M:%S').time()
            print '--calendar from,_to-----', first_sign_in_time, time_from, time_to, late, time_from_max
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
                            'description': u'طلب إستئذان رقم %s . من الساعة %s إلى %s  ' % (authorization.name, authorization.hour_from, authorization.hour_to),
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
                        'hour_calendar': time_float_convert(time_from),
                        'hour_attendance': time_float_convert(first_sign_in_time),
                        'delay_retard': delay_retard,
                        'date': date,
                        'action': 'retard',
                        'latest_date_import': latest_datetime_import}
                report_day_obj.create(vals)

        return True

    def chek_sign_out(self, date, employee_id, latest_time, latest_date_import):
        '''
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

        print '------current_time,time_to--------', current_time, time_to
        if current_time >= time_to:
            if not employee_attendances_sign_out:
                vals = {'employee_id': employee_id,
                        'hour_calendar': time_float_convert(time_to),
                        'date': date,
                        'action': 'no_leave',
                        'description': u'لم يسجل بصمة الخروج',
                        'latest_date_import': latest_date_import
                        }
                report_day_obj.create(vals)
                print '-------no attendance out ', employee.name
            else:
                last_sign_out = employee_attendances_sign_out[0]
                last_sign_out_time = datetime.strptime(last_sign_out.name, '%Y-%m-%d %H:%M:%S').time()
                if last_sign_out_time < time_to_min:
                    delay_leave = datetime.strptime(str(time_to), FORMAT_TIME) - datetime.strptime(str(last_sign_out_time), FORMAT_TIME)
                    delay_leave_seconds = delay_leave.seconds
                    delay_leave = delay_leave_seconds / 3600.0
                    vals = {'employee_id': employee.id,
                            'hour_calendar': time_float_convert(time_to),
                            'hour_attendance': time_float_convert(last_sign_out_time),
                            'delay_leave': delay_leave,
                            'date': date,
                            'action': 'leave',
                            'latest_date_import': latest_date_import}
                    report_day_obj.create(vals)
                # احتساب وقت إضافي
                elif last_sign_out_time > time_to_min:
                    delay_hours_supp = datetime.strptime(str(last_sign_out_time), FORMAT_TIME) - datetime.strptime(str(time_to), FORMAT_TIME)
                    delay_hours_supp_seconds = delay_hours_supp.seconds
                    delay_hours_supp = delay_hours_supp_seconds / 3600.0
                    vals = {'employee_id': employee.id,
                            'hour_calendar_to': time_float_convert(time_to),
                            'delay_hours_supp': delay_hours_supp,
                            'date': date,
                            'action': 'hour_supp',
                            'latest_date_import': latest_date_import}
                    report_day_obj.create(vals)
        return True

    def chek_import_attendance(self, date):
        employee_obj = self.env['hr.employee']
        attendance_obj = self.env['hr.attendance']
        report_day_obj = self.env['hr.attendance.report_day']
        date_start = datetime.strptime(date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        date_stop = datetime.strptime(date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        # first delete all actions for this day
        report_day_ids = report_day_obj.search([('date', '=', date)])
        report_day_ids.unlink()
        # get latest time for attendence
        all_attendances = attendance_obj.search([('name', '>=', str(date_start)), ('name', '<=', str(date_stop))])
        latest_time = datetime.strptime(all_attendances[0].name, '%Y-%m-%d %H:%M:%S').time()
        # check for each employee
        for employee in employee_obj.search([]):  # TODO: must add it [('employee_state', '=', 'employee')]
            if not employee.calendar_id:
                raise ValidationError(u"يجب تحديد ساعات العمل للموظف %s " % employee.name)

            self.chek_sign_in(date, employee.id, latest_time, all_attendances[0].name)
            self.chek_sign_out(date, employee.id, latest_time, all_attendances[0].name)

        return True

    @api.multi
    def import_attendance(self):
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

    employee_id = fields.Many2one('hr.employee', string='الموظف')
    hour_calendar = fields.Float(string='وقت الوردية')
    hour_calendar_to = fields.Float(string='وقت الوردية')
    hour_attendance = fields.Float(string='وقت البصمة')
    delay_retard = fields.Float(string='مدة التأخير')
    delay_leave = fields.Float(string='مدة الخروج المبكر')
    delay_hours_supp = fields.Float(string='مدة الوقت الإضافي')
    date = fields.Date(string='التاريخ')
    latest_date_import = fields.Datetime(string='أخر وقت تحديث البيانات')
    action = fields.Selection([('retard', 'تأخير'),
                               ('leave', 'خروج مبكر'),
                               ('no_leave', 'لم يسجل بصمة الخروج'),
                               ('absence_justified', 'غياب مبرر'),
                               ('absence', 'غياب'),
                               ('hour_supp', 'وقت إضافي')], string='الحالة')
    description = fields.Char(string='السبب')
