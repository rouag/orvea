# -*- coding: utf-8 -*-


from openerp import fields, models, api, tools
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT



class hr_attendance_view_report(models.Model):
    _name = 'hr.attendance.view.report'
    _description = ' Attendance View Report'
    _auto = False

    day = fields.Char(string=u'يوم')
    date = fields.Char(string=u'تاريخ')
    sign_in = fields.Char(string=u'تسجيل دخول')
    sign_out = fields.Char(string=u'تسجيل خروج')
    leave = fields.Char(string=u'أجازة')
    color = fields.Selection([
        (1, 'Black'),
        (2, 'Green'),
        (3, 'Orange'),
        (4, 'Red'),
        (5, 'Grey'),
    ], string='Color', default=1)

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

    def _get_ummqura(self, g_date):
        g_date = fields.Date.from_string(g_date)
        h_date = ummqura.from_gregorian(g_date.year, g_date.month, g_date.day)
        return int(h_date[0]), int(h_date[1]), int(h_date[2]), ('%04d' % int(h_date[0])) + "/" + ('%02d' % int(h_date[1])) + "/" + ('%02d' % int(h_date[2]))

    def _get_first_sign_in(self, employee_id, search_date):
        # Objects
        att_obj = self.env['hr.attendance']
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
        for rec in att_obj.search(search_attendance_domain, order='name', limit=1):
            return fields.Datetime.from_string(rec.name).strftime("%I:%M %p"), fields.Datetime.from_string(rec.name), work_sch.exempt_sign_in
        return '', False, False

    def _get_last_sign_out(self, employee_id, search_date):
        # Objects
        att_obj = self.env['hr.attendance']
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
        for rec in att_obj.search(search_attendance_domain, order='name desc', limit=1):
            return fields.Datetime.from_string(rec.name).strftime("%I:%M %p"), fields.Datetime.from_string(rec.name), work_sch.exempt_sign_out
        return '', False, False

    def _get_leave(self, employee_id, search_date):
        # Objects
        leave_obj = self.env['hr.leave']
        depu_obj = self.env['hr.deputation']
        training_obj = self.env['hr.training']
        task_obj = self.env['hr.task']
        # Check Eid
        eid_res = self._is_eid(search_date)
        if eid_res[0]:
            return eid_res[1]
        # Check Leaves
        leave_search_domain = [
            ('employee_id', '=', employee_id),
            ('state', '=', 'done'),
        ]
        for rec in leave_obj.search(leave_search_domain):
            if rec.date_from <= search_date <= rec.date_to:
                return u'اجازة'
        # Check Deputations
        for rec in depu_obj.search([]):
            if rec.state == 'done' and rec.date_from <= search_date <= rec.date_to:
                if rec.employee_id.id == employee_id:
                    return u'انتداب'
        # Check Training
        for rec in training_obj.search([]):
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
        for rec in task_obj.search([]):
            if rec.task_date == search_date and rec.employee_id.id == employee_id and rec.state == 'done' and rec.exempt_sign_in and rec.exempt_sign_out:
                return u'مهمة'
        return ''

    def _is_eid(self, search_date):
        # Objects
        eid_obj = self.env['hr.eid']
        # Check if Eid exists
        for rec in eid_obj.search([]):
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
        employee_obj = self.env['hr.employee']
        # Search for corresponding work schedule
        for emp in employee_obj.browse(employee_id):
            for line in emp.schedule_ids.sorted(key=lambda r: r.date_from, reverse=True):
                date_to = line.date_to
                if date_to == False:
                    date_to = '2050-12-31'
                if line.date_from <= search_date < date_to:
                    return line
        return False

    def _get_color(self, employee_id, search_date):
        # Objects
        leave_obj = self.env['hr.leave']
        depu_obj = self.env['hr.deputation']
        training_obj = self.env['hr.training']
        att_obj = self.env['hr.attendance']
        eid_obj = self.env['hr.eid']
        task_obj = self.env['hr.task']
        # Leave
        leave_search_domain = [
            ('employee_id', '=', employee_id),
            ('state', '=', 'done'),
        ]
        for rec in leave_obj.search(leave_search_domain):
            if rec.date_from <= search_date <= rec.date_to:
                return 2
        # Deputation
        for rec in depu_obj.search([]):
            if rec.state == 'done' and rec.date_from <= search_date <= rec.date_to:
                if rec.employee_id.id == employee_id:
                    return 2
        # Training
        for rec in training_obj.search([]):
            if rec.state == 'done' and rec.effective_date_from <= search_date <= rec.effective_date_to:
                for line in rec.employee_ids:
                    if line.id == employee_id:
                        return 2
        # Eid
        for rec in eid_obj.search([]):
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
        att_ids = att_obj.search(search_domain, order="name desc")
        if not att_ids:
            # Check for full day task
            task_ids = task_obj.search([
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
                    task_ids = task_obj.search(search_domain)
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
                    task_ids = task_obj.search(search_domain)
                    if not task_ids:
                        return 3
        return 1

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        # Variables
        ret = []
        cx = self._context
        employee_id = cx.get('employee_id', False)
        date_from = cx.get('date_from', False)
        date_to = cx.get('date_to', False)
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
        # Clean record set
        self = self & self.browse(list(xrange(1, len(ret) + 1)))
        return ret

    """
        Dummy SQL Query
    """
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'hr_attendance_view_report')
        cr.execute("""
            create or replace view hr_attendance_view_report as (
                SELECT
                   x.id as id,
                   '' as day,
                   '' as date,
                   '' as sign_in,
                   '' as sign_out,
                   '' as leave,
                   0 as color
                FROM generate_series(1,1000000) AS x(id)
            )
            """)