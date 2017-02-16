# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class ResGroups(models.Model):

    _inherit = "res.groups"

    @api.multi
    def write(self, vals):
        res = super(ResGroups, self).write(vals)
        group_id = self.env.ref('smart_hr.group_hr_authority_board')
        if 'users' in vals and self.id == group_id.id:
            user_ids = vals['users']
            for user_id in user_ids[0][2]:
                user = self.env['res.users'].browse(user_id)
                for emp in user.employee_ids:
                    job_required_ids = self.env['hr.authority.board.setting'].search([], limit=1).job_required_ids
                    if emp.job_id.id not in job_required_ids.ids:
                        raise ValidationError(u"الرجاء مراجعة اعدادات وظائف اعضاء مجلس الهيئة")
            users_number = self.env['hr.authority.board.setting'].search([], limit=1).users_number
            if len(self.users.ids)  > users_number:
                raise ValidationError(u"عدد اعضاء مجلس الهيئة لا يمكن ان يكون ا كثر من %s"%users_number)
        return res


class ResUsers(models.Model):

    _inherit = "res.users"

    @api.multi
    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        group_id = self.env.ref('smart_hr.group_hr_authority_board')
        valsgroup_id = 'in_group_'+ str(group_id.id)
        if valsgroup_id in vals:
            if vals[valsgroup_id] is True:
                job_required_ids = self.env['hr.authority.board.setting'].search([], limit=1).job_required_ids
                for emp in self.employee_ids:
                    if emp.job_id.id not in job_required_ids.ids:
                        raise ValidationError(u"الرجاء مراجعة اعدادات وظائف اعضاء مجلس الهيئة")
                users_number = self.env['hr.authority.board.setting'].search([], limit=1).users_number
                if len(group_id.users.ids) > users_number:
                    raise ValidationError(u"عدد اعضاء مجلس الهيئة لا يمكن ان يكون ا كثر من %s"%users_number)
        return res
