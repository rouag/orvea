# -*- coding: utf-8 -*-

{
    'name': 'Smart HR',
    'version': '9.0.1.0',
    'author': 'SMART-ETEK',
    'summary': 'HR',
    'description':
        """
        """,
    'depends': ['hr', 'hr_holidays', 'odoo_rtl', 'web_readonly_bypass','resource','hr_attendance'],
    'data': [
        'view/hr_menu.xml',
        
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        
        'data/sequences.xml',
        'data/configurations.xml',
        'data/hr_leave_data.xml',
        'data/schedulers.xml',
        
        
        'views/report_salary_grid.xml',
        'views/report_medical_examination.xml',
        'views/report_order_enquiry.xml',
        'views/hr_leave_report.xml',
        'views/report.xml',
        'views/templates.xml',
        'views/layout.xml',

        
        
        'wizards/view/hr_refuse_wizard_view.xml',

               
        
        'view/hr.xml',
        'view/hr_job.xml',
        'view/hr_decision_appoint.xml',
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
        'view/hr_eid_view.xml',
        'view/hr_employee_education_level.xml',
        'view/hr_assessment_view.xml',
        'view/hr_assessment_point_view.xml',
        
        #
        'attendance/wizard/hr_attendance_biostar_wizard_view.xml',
        'attendance/wizard/hr_attendance_followup_summary_view_wizard_view.xml',
        'attendance/wizard/hr_attendance_followup_view_wizard_view.xml',
        'attendance/wizard/hr_attendance_view_wizard_view.xml',
        'attendance/view/hr_resource_calendar.xml',
        'attendance/view/hr_plan_presence.xml',
        'attendance/view/import_csv_view.xml',
        'attendance/view/hr_attendance.xml',
        'attendance/view/hr_public_holiday.xml',
        'attendance/view/hr_attendance.xml',
        'attendance/view/hr_attendance_followup_summary_view_report_view.xml',
        'attendance/view/hr_attendance_followup_view_report_view.xml',
        'attendance/view/hr_attendance_followup_summary_view_report_view.xml',
        'attendance/views/hr_attendance_followup_report.xml',
        'attendance/views/hr_attendance_followup_summary_report.xml',
        'attendance/views/hr_attendance_report.xml',
        'attendance/views/report.xml',
        
    ],
    'auto_install': False,
}
