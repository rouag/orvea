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
import pymysql


class HrMysqlConfig(models.Model):
    _name = 'hr.mysql.config'
    _description = u'إجراء  جدول الحضور و الإنصراف'
    _rec_name ='db'
    
    host = fields.Char(string='مضيف')
    user = fields.Char(string='المستخدم')
    passwd = fields.Char(string='كلمة المرور')
    db = fields.Char(string='قاعدة معطيات')
    port=fields.Char(string='المنفذ')
    latest_date_import = fields.Datetime(string='وقت أخر تحديث')

    @api.one
    def action_done(self):
        employee_obj = self.env['hr.employee']
        attendance_obj = self.env['hr.attendance']
        conn = pymysql.connect(host=self.host, port=3306, user=self.user, passwd=self.passwd, db=self.db)
        cur = conn.cursor()
        cur.execute("SELECT  * FROM hr_attendance WHERE trndatetime2 > %s", self.latest_date_import)
        all_dates = set()
        for row in cur:
            date = row[2].split(' ')[0]
            all_dates.add(date)
            i = 0
            for date in all_dates:
            #for row in cur:
                date_pointage = row[2].split(' ')[0]
                if date_pointage == date:
                    if len(str(row[3]))==4:
                        empid = str(row[3])
                    else:
                        empid = str(row[3])
                    employee = self.env['hr.employee'].search([('number', '=', empid)])
                    if employee:
                        if str(row[6]) == '1':
                            action = 'sign_in'
                        else:
                            action = 'sign_out'
                        hr_attendance_val = {'employee_id': employee.id,
                                             'name': row[2],
                                             'action': action,
                                             'mac_id': row[7]}
                        hr_attendance = self.env['hr.attendance'].create(hr_attendance_val)
                        self.latest_date_import = row[2]
                i += 1
            self.env['hr.attendance.import'].chek_import_attendance(date)
            # close
            if len(all_dates) > 1 and  i != len(all_dates):
                self.env['hr.attendance.import'].close_day(date)

        cur.close()
        conn.close()


        