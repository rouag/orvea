# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
import pymysql


# https://help.ubuntu.com/12.04/serverguide/mysql.html

class HrAttendanceConfig(models.Model):
    _name = 'hr.attendance.config'
    _description = u'الربط مع قاعدة البيانات'
    _rec_name = 'db'

    host = fields.Char(string='مكان الاستضافة')
    user = fields.Char(string='المستخدم')
    passwd = fields.Char(string='كلمة المرور')
    db = fields.Char(string='قاعدة البيانات')
    port = fields.Char(string='المنفذ')
    latest_date_import = fields.Datetime(string='وقت أخر تحديث')

    @api.one
    def action_done(self):
        employee_obj = self.env['hr.employee']
        attendance_obj = self.env['hr.attendance']
        attendance_import_obj = self.env['hr.attendance.import']
        conn = pymysql.connect(host=self.host, port=3306, user=self.user, passwd=self.passwd, db=self.db)
        cur = conn.cursor()
        cur.execute("SELECT  * FROM hr_attendance WHERE trndatetime2 > %s", self.latest_date_import)
        all_dates = set()

        # get list of attendances by date
        # {'01-01-2017':[{'employee_id':1,'name':name,'action':'sign_in'},{'employee_id':2,'name':name,'action':'sign_in'},....],
        # '02-01-2017':[{'employee_id':1,'name':name,'action':'sign_in'},{'employee_id':2,'name':name,'action':'sign_in'},....] ,...}
        attendance_by_dates = {}
        for row in cur:
            date = row[2].split(' ')[0]
            employee_id = str(row[3])
            employee = self.env['hr.employee'].search([('number', '=', employee_id)])
            if employee:
                if str(row[6]) == '1':
                    action = 'sign_in'
                else:
                    action = 'sign_out'
                hr_attendance_val = {'employee_id': employee.id,
                                     'name': row[2],
                                     'action': action,
                                     'mac_id': row[7]}

                if attendance_by_dates.get(date, False):
                    attendance_by_dates[date].append(hr_attendance_val)
                else:
                    attendance_by_dates.update({date: [hr_attendance_val]})
        # create attendances
        i = 1
        for key, values in attendance_by_dates.items():
            for val in values:
                attendance_obj.create(val)
            attendance_import_obj.chek_import_attendance(key)
            # clos day if the dict  have multiple dates.but done close the latest date because we can import others record after this import
            if len(attendance_by_dates) > 1 and i < len(attendance_by_dates):
                attendance_import_obj.close_day(key)
            i += 1

        # update latest_date_import
        self.latest_date_import = datetime.now()

        cur.close()
        conn.close()
