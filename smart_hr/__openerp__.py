# -*- coding: utf-8 -*-

{
    'name': 'Smart HR',
    'version': '9.0.1.0',
    'author': 'SMART-ETEK',
    'summary': 'HR',
    'description':
        """
        """,
    'depends': ['hr', 'hr_holidays', 'odoo_rtl', 'web_readonly_bypass', 'hr_payroll', 'hr_attendance', 'smart_base', 'survey', 'hr_appraisal'],
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
        'data/decisions_type_data.xml',
        'data/hr_appoint_type_data.xml',
        'data/hr_sanction_type_data.xml',

        # الوظائف
        'job/menu.xml',
        'job/security/job_security.xml',
        'job/security/ir.model.access.csv',
        'job/security/ir.model.access.csv',
        'job/data/data.xml',
        'job/wizard/wizard_job_grade_view.xml',
        'job/wizard/wizard_job_update_view.xml',
        'job/wizard/wizard_job_description_view.xml',
        'job/wizard/wizard_job_move_dep_view.xml',
        'job/wizard/wizard_job_update_model_view.xml',
        'job/wizard/wizard_job_scale_down_model_view.xml',
        'job/wizard/wizard_job_create_model_view.xml',
        'job/wizard/wizard_job_modifying_model_view.xml',
        'job/wizard/wizard_job_career_model_view.xml',
        'job/views/job_career_model_report.xml',
        'job/views/job_modifying_model_report.xml',
        'job/views/job_create_model_report.xml',
        'job/views/job_scale_down_model_report.xml',
        'job/views/job_move_dep_report.xml',
        'job/views/job_grade_report.xml',
        'job/views/job_update_report.xml',
        'job/views/job_description_report.xml',
        'job/views/job_update_model_report.xml',
        'job/views/report.xml',

        # setting
        'setting/menu.xml',

        # الإدارات
        'hr/menu.xml',
        'hr/view/hierarchy_level.xml',
        'hr/view/hr_department_view.xml',
        'hr/view/hr_contract_inherit_view.xml',
        'hr/view/hr_contract_item_view.xml',
        'hr/views/report_hr_contract.xml',
        'hr/views/report.xml',
        'hr/data/hr_department_type_data.xml',

        'views/report_salary_grid.xml',
        'views/report_medical_examination.xml',
        'views/report_order_enquiry.xml',
        'views/hr_holidays_report.xml',
        'views/report_hr_holidays_decision.xml',
        'views/report_hr_decision.xml',
        'views/report.xml',
        'views/templates.xml',
        'views/layout.xml',
        'views/hr_deputation_report.xml',
        'views/hr_dep_accr_report.xml',
        'views/report_point_decinne.xml',
        'views/report_hr_direct_appoint.xml',
        'views/hr_employee_functionnal_card_report.xml',
        'report/reports.xml',
        'report/hr_suspension_end_report.xml',
        'report/hr_suspension_report.xml',
        'report/hr_termination_report.xml',

        'wizards/view/hr_refuse_wizard_view.xml',

        'view/hr.xml',

        'view/hr_decision_appoint.xml',
#         'view/hr_promotion.xml',
        'view/hr_training.xml',
        'view/hr_training_setting.xml',
        'view/hr_exam_emp.xml',
        'view/res_partner.xml',
        'view/judicial_precedent.xml',
        'view/recruiter.xml',
        'view/hr_holidays.xml',
        'view/hr_holidays_cancellation_view.xml',
        'view/hr_holidays_decision_view.xml',
        'view/hr_overtime_view.xml',
        'view/hr_employee_education_level.xml',
        'view/hr_assessment_view.xml',
        'view/hr_assessment_point_view.xml',
        'view/hr_deputation_view.xml',
        'view/res_city_view.xml',
        'view/hr_suspension_view.xml',
        'view/hr_suspension_end_view.xml',
        'view/hr_termination_view.xml',
        'view/external_autorities.xml',
        'view/holiday_entitlement_types.xml',
        'view/hr_holidays_extension.xml',
        'view/religion.xml',
        'view/courses_follow_up.xml',
        'view/hr_direct_appoint_view.xml',
        'view/hr_sanction_view.xml',
        'view/hr_remove_sanction_view.xml',
        'view/hr_employee_functional_card.xml',
        'view/res_users.xml',

        # القرارات
        'view/hr_decision.xml',
        # الرواتب
        'payroll/menu.xml',
        # 'payroll/data/data.xml',
        'payroll/data/salary_grid_type_data.xml',
        'payroll/wizard/wizard_bonus_employee.xml',
        'payroll/wizard/wizard_bonus_action.xml',
        'payroll/wizard/wizard_deducation_action.xml',
        'payroll/wizard/wizard_loan_action.xml',
        'payroll/view/salary_grid.xml',
        'payroll/view/hr_payroll_view.xml',
        'payroll/view/setting_view.xml',
        'payroll/view/hr_salary_rule_view.xml',
        'payroll/view/hr_deduction.xml',
        'payroll/view/hr_bonus_view.xml',
        'payroll/view/hr_loan_view.xml',
        'payroll/views/report_hr_deduction.xml',
        'payroll/views/report.xml',
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
        'attendance/view/hr_request_transfer_view.xml',
        'attendance/view/report_day_view.xml',
        'attendance/view/hr_attendance_check_view.xml',
        'attendance/view/hr_attendance_report_view.xml',
        'attendance/view/hr_monthly_summary_view.xml',
        'attendance/wizard/wizard_attendance_summary_view.xml',
        'attendance/views/attendance_summary_report.xml',
        'attendance/views/monthly_summary_report.xml',
        'attendance/views/monthly_summary_report_all.xml',
        'attendance/views/report.xml',
        # تصنيف الوظائف
        'job/view/hr_job_setting.xml',
        'job/view/hr_skils_job.xml',
        'job/view/hr_job.xml',
        'job/view/hr_job_workflow.xml',

        # الاجازات
        'holidays/menu.xml',
        'holidays/wizard/wizard_resume_holidays_view.xml',
        'holidays/views/resume_holidays_report.xml',
        'holidays/views/report.xml',

        #apprasal menu
        #التقييم والإختبار
        'hr_appraisal/view/hr_appraisal_menu.xml',
        'hr_appraisal/view/hr_appraisal_view.xml',
        'hr_appraisal/view/hr_evaluation_point_view.xml',
        
        #promotion
        'hr_promotions/view/hr_promotion_view.xml',

    ],
    'auto_install': False,
}
