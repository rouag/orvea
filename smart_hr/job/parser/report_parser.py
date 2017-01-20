# -*- coding: utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.addons.smart_base.util.time_util import float_time_convert
from openerp import fields
from dateutil.relativedelta import relativedelta


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


class JobDescriptionReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(JobDescriptionReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_lines': self._get_lines,
            'format_time': self._format_time,
            'get_current_date': self._get_current_date,
            'get_job': self._get_job,
            'get_job_create_date': self._get_job_create_date,
            'get_employee_job_decision': self._get_employee_job_decision,
            'get_employee_job_decision_history': self._get_employee_job_decision_history,
            'get_employee_last_training': self._get_employee_last_training
        })

    def _get_employee_last_training(self, job):
        hr_candidates_ids = self.pool.get('hr.candidates').search(self.cr, self.uid, [('training_id.state', '=', 'done'), ('employee_id', '=', job.employee.id)])
        if hr_candidates_ids:
            last_hr_candidate_id = hr_candidates_ids[len(hr_candidates_ids) - 1]
            if last_hr_candidate_id:
                hr_candidate = self.pool.get('hr.candidates').browse(self.cr, self.uid, [last_hr_candidate_id])
            return hr_candidate.training_id
        return False

    def _get_employee_job_decision_history(self, job):
        hr_decision_appoint_ids = self.pool.get('hr.decision.appoint').search(self.cr, self.uid, [('employee_id', '=', job.employee.id), ('state', '=', 'done'), ('active', '=', False)])
        if hr_decision_appoint_ids:
            res = []
            hr_decision_appoints = self.pool.get('hr.decision.appoint').browse(self.cr, self.uid, hr_decision_appoint_ids)
            for rec in hr_decision_appoints:
                date_hiring = fields.Date.from_string(rec.date_hiring)
                diff = relativedelta(fields.Date.from_string(fields.Datetime.now()), date_hiring).years
                if diff <= 2:
                    res.append(rec)
            return res
        return False

    def _get_employee_job_decision(self, job):
        hr_decision_appoint_ids = self.pool.get('hr.decision.appoint').search(self.cr, self.uid, [('job_id', '=', job.id), ('state', '=', 'done')])
        if hr_decision_appoint_ids:
            last_decision_appoint_id = hr_decision_appoint_ids[len(hr_decision_appoint_ids) - 1]
            if last_decision_appoint_id:
                hr_decision_appoint = self.pool.get('hr.decision.appoint').browse(self.cr, self.uid, [last_decision_appoint_id])[0]
                return hr_decision_appoint
        return False

    def _get_job_create_date(self, job):
        return fields.Datetime.from_string(job.create_date).strftime("%Y-%m-%d")

    def _get_job(self, data):
        job_id = data['job_id'][0]
        return self.pool.get('hr.job').browse(self.cr, self.uid, [job_id])[0]

    def _get_current_date(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")

    def _format_time(self, time_float):
        hour, minn = float_time_convert(time_float)
        return '%s:%s' % (str(hour).zfill(2), str(minn).zfill(2))

    def _get_lines(self, data):
        return []


class ReportJobDescription(osv.AbstractModel):
    _name = 'report.smart_hr.report_job_description'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_job_description'
    _wrapped_report_class = JobDescriptionReport


class JobMoveDepReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(JobMoveDepReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_company': self._get_company,
            'format_time': self._format_time,
            'get_current_date': self._get_current_date,
            'get_job': self._get_job,
            'get_job_create_date': self._get_job_create_date,
            'get_move_line': self._get_move_line,
        })

    def _get_company(self):
        return self.pool.get('res.users').browse(self.cr, self.uid, [self.uid])[0].company_id

    def _get_move_line(self, data, job):
        job_move_department_id = data['job_move_department_id'][0]
        job_move_department_obj = self.pool.get('hr.job.move.department').browse(self.cr, self.uid, [job_move_department_id])[0]
        if job_move_department_obj:
            for line in job_move_department_obj.job_movement_ids:
                if line.job_id.id == job.id:
                    return line
        return False

    def _get_job_create_date(self, job):
        return fields.Datetime.from_string(job.create_date).strftime("%Y-%m-%d")

    def _get_job(self, data):
        job_id = data['job_id'][0]
        return self.pool.get('hr.job').browse(self.cr, self.uid, [job_id])[0]

    def _get_current_date(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")

    def _format_time(self, time_float):
        hour, minn = float_time_convert(time_float)
        return '%s:%s' % (str(hour).zfill(2), str(minn).zfill(2))

    def _get_lines(self, data):
        return []


class ReportJobMoveDep(osv.AbstractModel):
    _name = 'report.smart_hr.report_job_move_dep'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_job_move_dep'
    _wrapped_report_class = JobMoveDepReport


class JobUpdateModelReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(JobUpdateModelReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_company': self._get_company,
            'format_time': self._format_time,
            'get_current_date': self._get_current_date,
            'get_job': self._get_job,
            'get_job_create_date': self._get_job_create_date,
            'get_same_activity_depart_job': self._get_same_activity_depart_job,
            'get_move_line': self._get_move_line
        })

    def _get_company(self):
        return self.pool.get('res.users').browse(self.cr, self.uid, [self.uid])[0].company_id

    def _get_move_line(self, data, job):
        job_update_id = data['job_update_id'][0]
        job_update_id_obj = self.pool.get('hr.job.update').browse(self.cr, self.uid, [job_update_id])[0]
        if job_update_id_obj:
            for line in job_update_id_obj.job_update_ids:
                if line.job_id.id == job.id:
                    return line
        return False

    def _get_same_activity_depart_job(self, job_id, job_name_id):
        job_ids = self.pool.get('hr.job').search(self.cr, self.uid, ['|', ('name', '=', job_name_id.name), ('activity_type', '=', job_id.activity_type.id), ('department_id', '=', job_id.department_id.id)])
        if job_ids:
            job_objs = self.pool.get('hr.job').browse(self.cr, self.uid, job_ids)
            return job_objs

    def _get_job_create_date(self, job):
        return fields.Datetime.from_string(job.create_date).strftime("%Y-%m-%d")

    def _get_job(self, data):
        job_id = data['job_id'][0]
        return self.pool.get('hr.job').browse(self.cr, self.uid, [job_id])[0]

    def _get_current_date(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")

    def _format_time(self, time_float):
        hour, minn = float_time_convert(time_float)
        return '%s:%s' % (str(hour).zfill(2), str(minn).zfill(2))

    def _get_lines(self, data):
        return []


class ReportJobUpdateModel(osv.AbstractModel):
    _name = 'report.smart_hr.report_job_update_model'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_job_update_model'
    _wrapped_report_class = JobUpdateModelReport


class JobScaleDownModelReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(JobScaleDownModelReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_company': self._get_company,
            'format_time': self._format_time,
            'get_current_date': self._get_current_date,
            'get_job': self._get_job,
            'get_job_create_date': self._get_job_create_date,
            'get_same_activity_depart_job': self._get_same_activity_depart_job,
            'get_move_line': self._get_move_line
        })

    def _get_company(self):
        return self.pool.get('res.users').browse(self.cr, self.uid, [self.uid])[0].company_id

    def _get_move_line(self, data, job):
        job_move_grade_id = data['job_move_grade_id'][0]
        job_move_grade_obj = self.pool.get('hr.job.move.grade').browse(self.cr, self.uid, [job_move_grade_id])[0]
        if job_move_grade_obj:
            for line in job_move_grade_obj.job_movement_ids:
                if line.job_id.id == job.id:
                    return line
        return False

    def _get_same_activity_depart_job(self, job_id, job_name_id):
        job_ids = self.pool.get('hr.job').search(self.cr, self.uid, ['|', ('name', '=', job_name_id.name), ('activity_type', '=', job_id.activity_type.id), ('department_id', '=', job_id.department_id.id)])
        if job_ids:
            job_objs = self.pool.get('hr.job').browse(self.cr, self.uid, job_ids)
            return job_objs

    def _get_job_create_date(self, job):
        return fields.Datetime.from_string(job.create_date).strftime("%Y-%m-%d")

    def _get_job(self, data):
        job_id = data['job_id'][0]
        return self.pool.get('hr.job').browse(self.cr, self.uid, [job_id])[0]

    def _get_current_date(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")

    def _format_time(self, time_float):
        hour, minn = float_time_convert(time_float)
        return '%s:%s' % (str(hour).zfill(2), str(minn).zfill(2))

    def _get_lines(self, data):
        return []


class ReportJobScaleDownModel(osv.AbstractModel):
    _name = 'report.smart_hr.report_job_scale_down_model'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_job_scale_down_model'
    _wrapped_report_class = JobScaleDownModelReport


class JobCreateModelReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(JobCreateModelReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_company': self._get_company,
            'format_time': self._format_time,
            'get_current_date': self._get_current_date,
        })

    def _get_company(self):
        return self.pool.get('res.users').browse(self.cr, self.uid, [self.uid])[0].company_id

    def _get_current_date(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")

    def _format_time(self, time_float):
        hour, minn = float_time_convert(time_float)
        return '%s:%s' % (str(hour).zfill(2), str(minn).zfill(2))


class ReportJobCreateModel(osv.AbstractModel):
    _name = 'report.smart_hr.report_job_create_model'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_job_create_model'
    _wrapped_report_class = JobCreateModelReport
