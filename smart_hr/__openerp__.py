# -*- coding: utf-8 -*-

{
    'name': 'Smart HR',
    'version': '9.0.1.0',
    'author': 'SMART-ETEK',
    'summary': 'HR',
    'description':
        """
        """,
    'depends': ['hr', 'hr_holidays', 'odoo_rtl', 'web_readonly_bypass', 'hr_payroll', 'hr_attendance', 'smart_base'],
    'data': [


        'security/hr_security.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'payroll/security/payroll_security.xml',
        'payroll/security/ir.model.access.csv',

        'view/hr_menu.xml',

        'data/sequences.xml',
        'data/configurations.xml',
        'data/hr_holidays_data.xml',
        'data/schedulers.xml',
        'data/res.city.csv',
        'data/hr_termination_data.xml',

        'views/report_salary_grid.xml',
        'views/report_hr_deduction.xml',
        'views/report_hr_deduction_line.xml',
        'views/report_medical_examination.xml',
        'views/report_order_enquiry.xml',
#         'views/hr_holidays_report.xml',
        'views/report.xml',
        'views/templates.xml',
        'views/layout.xml',
        'views/hr_deputation_report.xml',
        'views/hr_dep_accr_report.xml',

        'report/reports.xml',
        'report/hr_suspension_end_report.xml',
        'report/hr_suspension_report.xml',
        'report/hr_termination_report.xml',

        'wizards/view/hr_refuse_wizard_view.xml',

        'view/hr_department_views.xml',
        'view/hr.xml',
        'view/hr_job.xml',
        'view/hr_decision_appoint.xml',
        'view/hr_deduction.xml',
        'view/hr_promotion.xml',
        'view/salary_grid.xml',
        'view/hr_training.xml',
        'view/hr_exam_emp.xml',
        'view/res_partner.xml',
        'view/judicial_precedent.xml',
        'view/recruiter.xml',
        'view/hr_holidays.xml',
        'view/hr_holidays_cancellation_view.xml',
        'view/hr_overtime_view.xml',
        'view/hr_employee_education_level.xml',
        'view/hr_assessment_view.xml',
        'view/hr_assessment_point_view.xml',
        'view/hr_deputation_view.xml',
        'view/res_city_view.xml',
        'view/hr_suspension_view.xml',
        'view/hr_suspension_end_view.xml',
        'view/hr_termination_view.xml',
        'view/section.xml',
        'view/hierarchy_level.xml',
        'view/external_autorities.xml',
         'view/holiday_entitlement_types.xml',

        # القرارات
        'view/hr_decision.xml',
        # الرواتب
        'payroll/data.xml',
        'payroll/hr_payroll_view.xml',
        'payroll/setting_view.xml',
        'payroll/hr_salary_rule_view.xml',

        # الحضور والإنصراف
        'attendance/security/attendance_security.xml',
        'attendance/security/ir.model.access.csv',
        'attendance/data/data.xml',
        'attendance/menu.xml',
        'attendance/view/hr_resource_calendar.xml',
        'attendance/view/hr_attendance_schedule.xml',
        'attendance/view/hr_public_holiday.xml',
        'attendance/view/hr_attendance_import_view.xml',
        'attendance/view/hr_attendance.xml',
        'attendance/view/hr_attendance.xml',
        'attendance/view/hr_extra_hours.xml',
        'attendance/view/hr_authorization_view.xml',
        'attendance/view/report_day_view.xml',
        'attendance/view/hr_attendance_check_view.xml',
        'attendance/view/hr_attendance_report_view.xml',
        'attendance/wizard/wizard_attendance_summary_view.xml',
        'attendance/views/attendance_summary_report.xml',
        'attendance/views/report.xml',
    ],
    'auto_install': False,
}
