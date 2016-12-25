# -*- coding: utf-8 -*-


from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_TIME_FORMAT
from datetime import datetime, timedelta
 
class hr_attendance_report_parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(hr_attendance_report_parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_employees': self._get_employees,
            'get_attendance_leaves': self._get_attendance_leaves,
            'get_ummqura': self._get_ummqura,
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

    def _get_attendance_leaves(self, employee_id, date_from, date_to):
        # Variables
        ret = []
        seq = 0
        # Build records
        if employee_id and date_from and date_to:
            start_date = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT)
            end_date = datetime.strptime(date_to, DEFAULT_SERVER_DATE_FORMAT)
            for single_date in daterange(start_date, end_date):
                search_date = single_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
                seq += 1
                att_rec = {
                    'id': seq,
                    'day': self._get_day_name(search_date),
                    'date': self._get_ummqura(search_date)[3],
                    'sign_in': self._get_first_sign_in(employee_id, search_date)[0],
                    'sign_out': self._get_last_sign_out(employee_id, search_date)[0],
                    'leave': self._get_leave(employee_id, search_date),
                    'color': self._get_color(employee_id, search_date),
                }
                ret.append(att_rec)
        return ret

    def _get_first_sign_in(self, employee_id, search_date):
        # Objects
        att_obj = self.pool.get('hr.attendance')
        # Variables
        search_attendance_domain = [
                ('employee_id', '=', employee_id),
                ('name', '>=', search_date + ' 00:00:00'),
                ('name', '<=', search_date + ' 23:59:59'),
                ('action', '=', 'sign_in'),
        ]
        # Get Right Work Schedule
        work_sch = self._get_work_schedule(employee_id, search_date)
        # Get Attendance
        att_ids = att_obj.search(self.cr, self.uid, search_attendance_domain, order='name', limit=1)
        for rec in att_obj.browse(self.cr, self.uid, att_ids):
            return fields.Datetime.from_string(rec.name).strftime("%I:%M %p"), fields.Datetime.from_string(rec.name), work_sch.exempt_sign_in
        return '', False, False

    def _get_last_sign_out(self, employee_id, search_date):
        # Objects
        att_obj = self.pool.get('hr.attendance')
        # Variables
        search_attendance_domain = [
                ('employee_id', '=', employee_id),
                ('name', '>=', search_date + ' 00:00:00'),
                ('name', '<=', search_date + ' 23:59:59'),
                ('action', '=', 'sign_out'),
        ]
        # Get Right Work Schedule
        work_sch = self._get_work_schedule(employee_id, search_date)
        # Get Attendance
        att_ids = att_obj.search(self.cr, self.uid, search_attendance_domain, order='name desc', limit=1)
        for rec in att_obj.browse(self.cr, self.uid, att_ids):
            return fields.Datetime.from_string(rec.name).strftime("%I:%M %p"), fields.Datetime.from_string(rec.name), work_sch.exempt_sign_out
        return '', False, False

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

    def _get_leave(self, employee_id, search_date):
        # Objects
        leave_obj = self.pool.get('hr.leave')
        depu_obj = self.pool.get('hr.deputation')
        training_obj = self.pool.get('hr.training')
        task_obj = self.pool.get('hr.task')
        # Check Eid
        eid_res = self._is_eid(search_date)
        if eid_res[0]:
            return eid_res[1]
        # Check Leaves
        leave_search_domain = [
            ('employee_id', '=', employee_id),
            ('state', '=', 'done'),
        ]
        lv_ids = leave_obj.search(self.cr, self.uid, leave_search_domain)
        for rec in leave_obj.browse(self.cr, self.uid, lv_ids):
            if rec.date_from <= search_date <= rec.date_to:
                return u'اجازة'
        # Check Deputations
        depu_ids = depu_obj.search(self.cr, self.uid, [])
        for rec in depu_obj.browse(self.cr, self.uid, depu_ids):
            if rec.state == 'done' and rec.date_from <= search_date <= rec.date_to:
                if rec.employee_id.id == employee_id:
                    return u'انتداب'
        # Check Training
        train_ids = training_obj.search(self.cr, self.uid, [])
        for rec in training_obj.browse(self.cr, self.uid, train_ids):
            if rec.state == 'done' and rec.effective_date_from <= search_date <= rec.effective_date_to:
                for line in rec.employee_ids:
                    if line.id == employee_id:
                        for period_line in rec.period_line_ids:
                            if period_line.date_from <= search_date <= period_line.date_to:
                                if period_line.state == 'deputation':
                                    return u'انتداب'
                                else:
                                    return u'تدريب'
        # Check Full Day Task
        task_ids = task_obj.search(self.cr, self.uid, [])
        for rec in task_obj.browse(self.cr, self.uid, task_ids):
            if rec.task_date == search_date and rec.employee_id.id == employee_id and rec.state == 'done' and rec.exempt_sign_in and rec.exempt_sign_out:
                return u'مهمة'
        return ''

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

    def _get_color(self, employee_id, search_date):
        # Objects
        leave_obj = self.pool.get('hr.leave')
        depu_obj = self.pool.get('hr.deputation')
        training_obj = self.pool.get('hr.training')
        att_obj = self.pool.get('hr.attendance')
        eid_obj = self.pool.get('hr.eid')
        task_obj = self.pool.get('hr.task')
        # Leave
        leave_search_domain = [
            ('employee_id', '=', employee_id),
            ('state', '=', 'done'),
        ]
        lv_ids = leave_obj.search(self.cr, self.uid, leave_search_domain)
        for rec in leave_obj.browse(self.cr, self.uid, lv_ids):
            if rec.date_from <= search_date <= rec.date_to:
                return 2
        # Deputation
        depu_ids = depu_obj.search(self.cr, self.uid, [])
        for rec in depu_obj.browse(self.cr, self.uid, depu_ids):
            if rec.state == 'done' and rec.date_from <= search_date <= rec.date_to:
                if rec.employee_id.id == employee_id:
                    return 2
        # Training
        train_ids = training_obj.search(self.cr, self.uid, [])
        for rec in training_obj.browse(self.cr, self.uid, train_ids):
            if rec.state == 'done' and rec.effective_date_from <= search_date <= rec.effective_date_to:
                for line in rec.employee_ids:
                    if line.id == employee_id:
                        return 2
        # Eid
        eid_ids = eid_obj.search(self.cr, self.uid, [])
        for rec in eid_obj.browse(self.cr, self.uid, eid_ids):
            if rec.date_from <= search_date <= rec.date_to:
                return 2
        # Weekend
        s_date = fields.Date.from_string(search_date)
        if s_date.weekday() in (4, 5):
            return 5
        # Absent
        search_domain = [
            ('employee_id', '=', employee_id),
            ('name', '>=', search_date + ' 00:00:00'),
            ('name', '<=', search_date + ' 23:59:59'),
        ]
        att_ids = att_obj.search(self.cr, self.uid, search_domain, order="name desc")
        if not att_ids:
            # Check for full day task
            task_ids = task_obj.search(self.cr, self.uid, [
                ('employee_id', '=', employee_id),
                ('task_date', '=', search_date),
                ('exempt_sign_in', '=', True),
                ('exempt_sign_out', '=', True),
                ('state', '=', 'done'),
            ])
            if task_ids:
                return 1
            return 4
        # Late
        else:
            # Check if late
            sign_in_datetime = self._get_first_sign_in(employee_id, search_date)
            sign_out_datetime = self._get_last_sign_out(employee_id, search_date)
            # Sign In
            if sign_in_datetime[1]:
                work_schedule_line_id = self._get_work_schedule(employee_id, search_date)
                if work_schedule_line_id:
                    start_work_datetime = self._forge_datetime(search_date, work_schedule_line_id.work_schedule_id.start_time)
                    if self._is_ramadan(search_date):
                        start_work_datetime = self._forge_datetime(search_date, work_schedule_line_id.work_schedule_id.ramadan_start_time)
                    diff_datetime = sign_in_datetime[1] - start_work_datetime
                    dhm = elapsed_time(diff_datetime.seconds)
                    if search_date >= '2015-11-27':
                        if diff_datetime.days >= 0 and diff_datetime.seconds > 0:
                            return 3
                    else:
                        if (dhm[0] > 0 and dhm[1] >= 23) or dhm[2] > 0 or dhm[3] > 0:
                            return 3
            # No Sign In
            elif not sign_in_datetime[1]:
                # Check Exempt
                if not sign_in_datetime[2]:
                    # Check Task
                    search_domain = [
                        ('employee_id', '=', employee_id),
                        ('task_date', '=', search_date),
                        ('exempt_sign_in', '=', True),
                        ('state', '=', 'done'),
                    ]
                    task_ids = task_obj.search(self.cr, self.uid, search_domain)
                    if not task_ids:
                        return 3
            # Sign Out
            if sign_out_datetime[1]:
                work_schedule_line_id = self._get_work_schedule(employee_id, search_date)
                if work_schedule_line_id:
                    end_work_datetime = self._forge_datetime(search_date, work_schedule_line_id.work_schedule_id.end_time)
                    if self._is_ramadan(search_date):
                        end_work_datetime = self._forge_datetime(search_date, work_schedule_line_id.work_schedule_id.ramadan_end_time)
                    diff_datetime = (end_work_datetime - timedelta(minutes=1)) - sign_out_datetime[1]
                    if diff_datetime.days >= 0 and diff_datetime.seconds > 0:
                        return 3
            # No Sign Out
            elif not sign_out_datetime[1]:
                # Check Exempt
                if not sign_out_datetime[2]:
                    # Check Task
                    search_domain = [
                        ('employee_id', '=', employee_id),
                        ('task_date', '=', search_date),
                        ('exempt_sign_out', '=', True),
                        ('state', '=', 'done'),
                    ]
                    task_ids = task_obj.search(self.cr, self.uid, search_domain)
                    if not task_ids:
                        return 3
        return 1

class hr_attendance_report(models.AbstractModel):
    _name = 'report.smart_hr.hr_attendance_report'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.hr_attendance_report'
    _wrapped_report_class = hr_attendance_report_parser