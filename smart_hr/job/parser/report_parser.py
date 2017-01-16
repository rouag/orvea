# -*- coding: utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.addons.smart_base.util.time_util import float_time_convert


class JobGradeReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(JobGradeReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_lines': self._get_lines,
            'format_time': self._format_time,
            'get_current_date': self._get_current_date,
        })

    def _get_current_date(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")

    def _format_time(self, time_float):
        hour, minn = float_time_convert(time_float)
        return '%s:%s' % (str(hour).zfill(2), str(minn).zfill(2))

    def _get_lines(self, data):
        report_type = data['report_type']
        res = []
        if report_type == 'requested':
            grade_from_id = int(data['grade_from_id'][0])
            grade_to_id = int(data['grade_to_id'][0])
            scale_down_ids = self.pool.get('hr.job.move.grade').search(self.cr, self.uid, [('move_type', '=', 'scale_down'), ('state', '!=', 'done')])
            for rec in self.pool.get('hr.job.move.grade').browse(self.cr, self.uid, scale_down_ids):
                for line in rec.job_movement_ids:
                    if line.grade_id.id == grade_from_id and line.new_grade_id.id == grade_to_id:
                        res.append(line)
        if report_type == 'accepted':
            scale_down_ids = self.pool.get('hr.job.move.grade').search(self.cr, self.uid, [('move_type', '=', 'scale_down'), ('state', '=', 'done')])
            for rec in self.pool.get('hr.job.move.grade').browse(self.cr, self.uid, scale_down_ids):
                for line in rec.job_movement_ids:
                    res.append(line)
        return res


class ReportJobGrade(osv.AbstractModel):
    _name = 'report.smart_hr.report_job_grade'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_job_grade'
    _wrapped_report_class = JobGradeReport


class JobUpdateReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(JobUpdateReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_lines': self._get_lines,
            'format_time': self._format_time,
            'get_current_date': self._get_current_date,
        })

    def _get_current_date(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")

    def _format_time(self, time_float):
        hour, minn = float_time_convert(time_float)
        return '%s:%s' % (str(hour).zfill(2), str(minn).zfill(2))

    def _get_lines(self, data):
        report_type = data['report_type']
        res = []
        if report_type == 'accepted':
            update_request_id = int(data['update_request_id'][0])
            for rec in self.pool.get('hr.job.update').browse(self.cr, self.uid, [update_request_id]):
                for line in rec.job_update_ids:
                    res.append(line)
        if report_type == 'requested':
            job_update_ids = self.pool.get('hr.job.update').search(self.cr, self.uid, [('state', '!=', 'done')])
            for rec in self.pool.get('hr.job.update').browse(self.cr, self.uid, job_update_ids):
                for line in rec.job_update_ids:
                    res.append(line)
        return res


class ReportJobUpdate(osv.AbstractModel):
    _name = 'report.smart_hr.report_job_update'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_job_update'
    _wrapped_report_class = JobUpdateReport
