# -*- coding: utf-8 -*-

from openerp import fields, models, api
from openerp.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

try:
    import pymssql
except ImportError:
    _logger.error("BioStar: Error in loading PyMSSQL Lib ...")

class hr_attendance_biostar_wizard(models.TransientModel):
    _name = "hr.attendance.biostar.wizard"
    _description = "Attendance BioStar Wizard"

    old_records = fields.Integer(string=u'عدد البيانات الحالية', compute='_get_records')
    current_records = fields.Integer(string=u'عدد البيانات على البصمة', compute='_get_records')
    new_records = fields.Integer(string=u'عدد البيانات الجديدة', compute='_get_records')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف')

    @api.multi
    def button_download(self):
        # Objects
        biostar_obj = self.env['hr.attendance.biostar']
        biostar_device = biostar_obj.search([], limit=1)
        biostar_device.run_download_new()

    @api.multi
    def button_employee(self):
        # Objects
        biostar_obj = self.env['hr.attendance.biostar']
        # Download certain employee attendance
        for wiz in self:
            # Validation
            if not wiz.employee_id:
                raise ValidationError(u"يجب اختيار موظف")
            if wiz.employee_id and not wiz.employee_id.biostar_no:
                raise ValidationError(u"هذا الموظف لم يعرف له رقم بصمة")
            # Run download
            biostar_device = biostar_obj.search([], limit=1)
            biostar_device.run_download_employee(wiz.employee_id.biostar_no)

    @api.depends('old_records', 'current_records', 'new_records')
    def _get_records(self):
        # Objects
        biostar_obj = self.env['hr.attendance.biostar']
        # Variables
        flag = False
        biostar_device = biostar_obj.search([], limit=1)
        #
        for wiz in self:
            # Check connection first
            if biostar_device.connection_exists():
                # Update records
                wiz.old_records = biostar_device.last_rec_num
                #
                SQL_Current_Records = """
SELECT TOP 1 nEventLogIdn FROM TB_EVENT_LOG
WHERE nUserID > 0 and nDateTime > 0 and nEventLogIdn > 0
ORDER BY nEventLogIdn DESC;
                """
                conn = pymssql.connect(biostar_device.ip_addr, biostar_device.db_user, biostar_device.db_pass, biostar_device.db_name)
                cursor = conn.cursor()
                cursor.execute(SQL_Current_Records)
                rows = cursor.fetchall()
                for row in rows:
                    wiz.current_records = row[0]
                    flag = True
                diff = wiz.current_records - wiz.old_records
                if flag:
                    wiz.new_records = diff
                else:
                    wiz.old_records = 0
                    wiz.current_records = 0
                    wiz.new_records = 0