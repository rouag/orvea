# -*- coding: utf-8 -*-
####################################
### This Module Created by Slnee ###
####################################

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_TIME_FORMAT
from datetime import datetime, timedelta
 
class hr_attendance_followup_report_parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(hr_attendance_followup_report_parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_employees': self._get_employees,
            'get_followup': self._get_followup,
            'get_ummqura': self._get_ummqura,
            'get_total_time': self._get_total_time,
            'today': self._get_ummqura(datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT))[3],
        })

    def _get_employees(self, wiz):
        if wiz['multi_employee']:
            return self.pool.get('hr.employee').browse(self.cr, self.uid, wiz['employee_ids'])
        return self.pool.get('hr.employee').browse(self.cr, self.uid, wiz['employee_id'][0])

    def _get_ummqura(self, g_date):
        g_date = fields.Date.from_string(g_date)
        h_date = ummqura.from_gregorian(g_date.year, g_date.month, g_date.day)
        return int(h_date[0]), int(h_date[1]), int(h_date[2]), ('%04d' % int(h_date[0])) + "/" + ('%02d' % int(h_date[1])) + "/" + ('%02d' % int(h_date[2]))

    def _get_day_name(self, search_date):
        # Variables
        days_arabic = {
            'Sunday': u'الأحد',
            'Monday': u'الأثنين',
            'Tuesday': u'الثلاثاء',
            'Wednesday': u'الأربعاء',
            'Thursday': u'الخميس',
            'Friday': u'الجمعة',
            'Saturday': u'السبت',
        }
        # Get day
        day_date = fields.Date.from_string(search_date)
        return days_arabic[day_date.strftime("%A")]

    def _has_leave(self, employee_id, search_date):
        # Objects
        leave_obj = self.pool.get('hr.leave')
        depu_obj = self.pool.get('hr.deputation')
        training_obj = self.pool.get('hr.training')
        # Check Leaves
        leave_search_domain = [
            ('employee_id', '=', employee_id),
            ('state', '=', 'done'),
        ]
        lv_ids = leave_obj.search(self.cr, self.uid, leave_search_domain)
        for rec in leave_obj.browse(self.cr, self.uid, lv_ids):
            if rec.date_from <= search_date <= rec.date_to:
                return True
        # Check Deputations
        depu_ids = depu_obj.search(self.cr, self.uid, [])
        for rec in depu_obj.browse(self.cr, self.uid, depu_ids):
            if rec.state == 'done' and rec.date_from <= search_date <= rec.date_to:
                if rec.employee_id.id == employee_id:
                    return True
        # Check Training
        train_ids = training_obj.search(self.cr, self.uid, [])
        for rec in training_obj.browse(self.cr, self.uid, train_ids):
            if rec.state == 'done' and rec.effective_date_from <= search_date <= rec.effective_date_to:
                for line in rec.employee_ids:
                    if line.id == employee_id:
                        return True
        return False

    def _is_eid(self, search_date):
        # Objects
        eid_obj = self.pool.get('hr.eid')
        # Check if Eid exists
        eid_ids = eid_obj.search(self.cr, self.uid, [])
        for rec in eid_obj.browse(self.cr, self.uid, eid_ids):
            if rec.date_from <= search_date <= rec.date_to:
                return True, rec.name
        return False, ''

    def _is_ramadan(self, search_date):
        if self._get_ummqura(search_date)[1] == 9:
            return True
        return False

    def _is_weekend(self, search_date):
        single_date = datetime.strptime(search_date, DEFAULT_SERVER_DATE_FORMAT)
        if single_date.weekday() in (4, 5):
            return True
        return False

    def _has_attendance(self, employee_id, search_date):
        # Objects
        att_obj = self.pool.get('hr.attendance')
        # Search for attendance
        search_domain = [
            ('employee_id', '=', employee_id),
            ('name', '>=', search_date + ' 00:00:00'),
            ('name', '<=', search_date + ' 23:59:59'),
        ]
        att_ids = att_obj.search(self.cr, self.uid, search_domain)
        if att_ids:
            return True
        return False

    def _has_sign_in(self, employee_id, search_date):
        # Objects
        att_obj = self.pool.get('hr.attendance')
        # Get Right Work Schedule
        work_sch = self._get_work_schedule(employee_id, search_date)
        # Search for attendance
        search_domain = [
            ('employee_id', '=', employee_id),
            ('name', '>=', search_date + ' 00:00:00'),
            ('name', '<=', search_date + ' 23:59:59'),
            ('action', '=', 'sign_in'),
        ]
        att_ids = att_obj.search(self.cr, self.uid, search_domain, limit=1, order='name')
        for rec in att_obj.browse(self.cr, self.uid, att_ids):
            return True, datetime.strptime(rec.name, DEFAULT_SERVER_DATETIME_FORMAT), work_sch.exempt_sign_in
        return False, False, False

    def _has_sign_out(self, employee_id, search_date):
        # Objects
        att_obj = self.pool.get('hr.attendance')
        # Get Right Work Schedule
        work_sch = self._get_work_schedule(employee_id, search_date)
        # Search for attendance
        search_domain = [
            ('employee_id', '=', employee_id),
            ('name', '>=', search_date + ' 00:00:00'),
            ('name', '<=', search_date + ' 23:59:59'),
            ('action', '=', 'sign_out'),
        ]
        att_ids = att_obj.search(self.cr, self.uid, search_domain, limit=1, order='name desc')
        for rec in att_obj.browse(self.cr, self.uid, att_ids):
            return True, datetime.strptime(rec.name, DEFAULT_SERVER_DATETIME_FORMAT), work_sch.exempt_sign_out
        return False, False, False

    def _forge_datetime(self, search_date, g_time):
        ret_time = datetime.strptime(search_date + ' ' + convert_float_to_time(g_time), DEFAULT_SERVER_DATETIME_FORMAT)
        return ret_time

    def _get_work_schedule(self, employee_id, search_date):
        # Objects
        employee_obj = self.pool.get('hr.employee')
        # Search for corresponding work schedule
        for emp in employee_obj.browse(self.cr, self.uid, employee_id):
            for line in emp.schedule_ids.sorted(key=lambda r: r.date_from, reverse=True):
                date_to = line.date_to
                if date_to == False:
                    date_to = '2050-12-31'
                if line.date_from <= search_date < date_to:
                    return line
        return False

    def _is_late(self, dt_diff, search_date, sign_in=True):
        dhm = elapsed_time(dt_diff.seconds)
        # Late Entry
        if sign_in:
            if dt_diff.days >= 0:
                if search_date >= '2015-11-27':
                    if dt_diff.seconds > 0:
                        return True, dhm
                else:
                    if (dhm[0] > 0 and dhm[1] >= 23) or dhm[2] > 0 or dhm[3] > 0:
                        return True, dhm
            return False, False
        # Early Leave
        if dt_diff.days >= 0:
            if dt_diff.seconds > 0:
                return True, dhm
        return False, False

    def _has_task(self, employee_id, search_date):
        # Objects
        task_obj = self.pool.get('hr.task')
        # Search for tasks
        search_domain = [
            ('task_date', '=', search_date),
            ('employee_id', '=', employee_id),
            ('state', '=', 'done'),
        ]
        task_ids = task_obj.search(self.cr, self.uid, search_domain)
        for rec in task_obj.browse(self.cr, self.uid, task_ids):
            return True, rec.exempt_sign_in, rec.exempt_sign_out
        return False, False, False

    def _is_today(self, search_date):
        search_date = datetime.strptime(search_date, DEFAULT_SERVER_DATE_FORMAT).date()
        today_date = datetime.today().date()
        if search_date == today_date:
            return True
        return False

    def _get_total_time(self, minutes, hours, days):
        secs = (minutes * 60) + (hours * 3600) + (days * 25200)
        dhm = elapsed_time(secs)
        return dhm

    def _get_followup(self, employee_id, date_from, date_to, wiz):
        # Objects
        task_obj = self.pool.get('hr.task')
        # Variables
        ret = []
        seq = 0
        # Run Check
        if employee_id and date_from and date_to:
            start_date = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT)
            end_date = datetime.strptime(date_to, DEFAULT_SERVER_DATE_FORMAT)
            for single_date in daterange(start_date, end_date):
                search_date = single_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
                # Check Weekends
                if self._is_weekend(search_date):
                    continue
                # Check Eid
                if self._is_eid(search_date)[0]:
                    continue
                # Check Leaves
                if self._has_leave(employee_id, search_date):
                    continue
                # Check Attendance
                if self._has_attendance(employee_id, search_date):
                    work_schedule_line_id = self._get_work_schedule(employee_id, search_date)
                    # Avoid Error in case no work schedule
                    if not work_schedule_line_id:
                        raise ValidationError(u"لم يتم تعريف الوردية المناسبة لهذه الفترة لهذا الموظف")
                    # Has Attendance
                    sign_in_datetime = self._has_sign_in(employee_id, search_date)
                    if sign_in_datetime[0]:
                        # Has Sign In
                        start_datetime = self._forge_datetime(search_date, work_schedule_line_id.work_schedule_id.start_time)
                        if self._is_ramadan(search_date):
                            start_datetime = self._forge_datetime(search_date, work_schedule_line_id.work_schedule_id.ramadan_start_time)
                        dt_diff = sign_in_datetime[1] - start_datetime
                        is_late = self._is_late(dt_diff, search_date, True)
                        if is_late[0] and wiz['lateness']:
                            seq += 1
                            att_rec = {
                                'id': seq,
                                'day': self._get_day_name(search_date),
                                'date': self._get_ummqura(search_date)[3],
                                'description': u'دخول متأخر',
                                'minutes': is_late[1][1],
                                'hours': is_late[1][2],
                                'days': is_late[1][3],
                            }
                            ret.append(att_rec)
                    else:
                        # Doesn't have Sign In
                        if not sign_in_datetime[2] and wiz['fingerprint'] and not self._is_today(search_date):
                            if not self._has_task(employee_id, search_date)[0] and not self._has_task(employee_id, search_date)[1]:
                                seq += 1
                                att_rec = {
                                    'id': seq,
                                    'day': self._get_day_name(search_date),
                                    'date': self._get_ummqura(search_date)[3],
                                    'description': u'لا يوجد بصمة دخول',
                                    'minutes': 0,
                                    'hours': 3,
                                    'days': 0,
                                }
                                ret.append(att_rec)
                    sign_out_datetime = self._has_sign_out(employee_id, search_date)
                    if sign_out_datetime[0]:
                        # Has Sign Out
                        end_datetime = self._forge_datetime(search_date, work_schedule_line_id.work_schedule_id.end_time)
                        if self._is_ramadan(search_date):
                            end_datetime = self._forge_datetime(search_date, work_schedule_line_id.work_schedule_id.ramadan_end_time)
                        dt_diff = end_datetime - sign_out_datetime[1]
                        is_late = self._is_late(dt_diff, search_date, False)
                        if is_late[0] and wiz['lateness']:
                            seq += 1
                            att_rec = {
                                'id': seq,
                                'day': self._get_day_name(search_date),
                                'date': self._get_ummqura(search_date)[3],
                                'description': u'خروج مبكر',
                                'minutes': is_late[1][1],
                                'hours': is_late[1][2],
                                'days': is_late[1][3],
                            }
                            ret.append(att_rec)
                    else:
                        # Doesn't have Sign Out
                        if not sign_out_datetime[2] and wiz['fingerprint'] and not self._is_today(search_date):
                            if not self._has_task(employee_id, search_date)[0] and not self._has_task(employee_id, search_date)[2]:
                                seq += 1
                                att_rec = {
                                    'id': seq,
                                    'day': self._get_day_name(search_date),
                                    'date': self._get_ummqura(search_date)[3],
                                    'description': u'لا يوجد بصمة خروج',
                                    'minutes': 0,
                                    'hours': 3,
                                    'days': 0,
                                }
                                ret.append(att_rec)
                else:
                    # Check for full day task
                    task_ids = task_obj.search(self.cr, self.uid, [
                        ('employee_id', '=', employee_id),
                        ('task_date', '=', search_date),
                        ('exempt_sign_in', '=', True),
                        ('exempt_sign_out', '=', True),
                        ('state', '=', 'done'),
                    ])
                    if task_ids:
                        continue
                    else:
                        if wiz['absent']:
                            # Doesn't have Attendance
                            seq += 1
                            att_rec = {
                                'id': seq,
                                'day': self._get_day_name(search_date),
                                'date': self._get_ummqura(search_date)[3],
                                'description': u'غياب',
                                'minutes': 0,
                                'hours': 0,
                                'days': 1,
                            }
                            ret.append(att_rec)
            return ret

class hr_attendance_followup_report(models.AbstractModel):
    _name = 'report.smart_hr.hr_attendance_followup_report'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.hr_attendance_followup_report'
    _wrapped_report_class = hr_attendance_followup_report_parser