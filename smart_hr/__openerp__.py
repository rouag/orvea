# -*- coding: utf-8 -*-

{
    'name': 'Smart HR',
    'version': '9.0.1.0',
    'author': 'SMART-ETECH',
    'summary': 'HR',
    'external_dependencies': {'python': ['umalqurra']},
    'description':
        """
        """,
    'depends': ['hr', 'hr_holidays', 'odoo_rtl', 'web_readonly_bypass', 'hr_payroll', 'hr_attendance', 'smart_base', 'survey', 'hr_appraisal', 'website','report_custom_filename'],
    'data': [

        'hr_promotions/security/promotion_security.xml',
        'security/hr_security.xml',
        'security/ir_rule.xml',
        'hr_promotions/security/ir_rule.xml',
        'security/ir.model.access.csv',
        'deputation/security/hr_security.xml',
        'payroll/security/payroll_security.xml',
        'payroll/security/ir.model.access.csv',
        'hr_scholarship/security/hr_security.xml',
        'hr_scholarship/security/ir.model.access.csv',
        'data/relegion_data.xml',
        'payroll/data/data.xml',

        'hr_menu.xml',
        'data/sequences.xml',
        'data/configurations.xml',
        'holidays/data/hr_holidays_data.xml',
        'data/schedulers.xml',
        'data/res_city_data.xml',
        'data/hr_termination_data.xml',
        'data/decisions_type_data.xml',
        'data/hr_appoint_type_data.xml',
        'payroll/data/data.xml',
        
        #'data/scholarship_data.xml',
        'hr_appraisal/data/hr_appraisal_data.xml',
        
        
        'wizards/view/hr_refuse_training_wizard_view.xml',
        'wizards/view/hr_refuse_employee_wizard_view.xml',
     
        

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
        'hr/security/hr_security.xml',
        'hr/security/ir.model.access.csv',
        'hr/wizard/hr_termination_wizard_view.xml',
        'hr/wizard/hr_transfert_wizard_view.xml',
        
        'hr/menu.xml',
        
        'hr/view/hierarchy_level.xml',
        'hr/view/hr_department_view.xml',
        'hr/view/hr_contract_inherit_view.xml',
        'hr/view/hr_contract_item_view.xml',
        'hr/views/report_hr_contract.xml',
        'hr/views/report_hr_employee_lend.xml',
        'hr/views/report_hr_employee_transfert.xml',
        'hr/views/report_hr_employee_assign.xml',
        'hr/views/hr_termination_retraite_reportt.xml',
        'hr/views/report_hr_employee_assign.xml',
        'hr/views/report.xml',
        'hr/data/hr_department_type_data.xml',
        'hr/data/hr_data.xml',
        'hr/view/hr_employee_transfert_view.xml',


        'hr/view/hr_setting.xml',
        'hr/view/hr_employee_lend_view.xml',
        'hr/view/hr_employee_comm_view.xml',
       
        'hr_promotions/views/report_promotion.xml',
        'hr/view/hr_employee_task_view.xml',

        'views/report_salary_grid.xml',
        'views/report_medical_examination.xml',
        'views/report_order_enquiry.xml',
     
        'views/report_hr_decision.xml',
        'views/report.xml',
        'views/templates.xml',
        'views/layout.xml',
        'views/hr_dep_accr_report.xml',
        'views/report_point_decinne.xml',
        'views/report_hr_direct_appoint.xml',
        'views/hr_employee_functionnal_card_report.xml',
        'views/hr_employee_card_report.xml',

        'views/hr_emp_card_report.xml',
        'report/reports.xml',
        'report/hr_suspension_end_report.xml',
        'report/hr_suspension_report.xml',
        'report/hr_termination_report.xml',
        'views/employee_situation_order_report.xml',
        'report/hr_suspension_report_decision.xml',
        'wizards/view/hr_refuse_wizard_view.xml',
        'view/hr_decision_appoint.xml',



#         'view/hr_promotion.xml',
        'view/hr_training.xml',
        'view/hr_training_setting.xml',
        'view/hr_exam_emp.xml',
        'view/res_partner.xml',
        'view/judicial_precedent.xml',
        'view/recruiter.xml',

        'view/hr_employee_education_level.xml',
        'view/hr_assessment_view.xml',
        'view/hr_assessment_point_view.xml',
        'view/res_city_view.xml',
        'view/hr_termination_view.xml',
        'view/hr_suspension_view.xml',
        'view/hr_suspension_end_view.xml',
        'view/religion.xml',
        'view/courses_follow_up.xml',
        'view/hr_direct_appoint_view.xml',
        'view/hr_employee_functional_card.xml',
        'view/res_users.xml',
        'view/employee_situation_order.xml',
        'view/hr_improve_situation_view.xml',
        'view/mail_message_view.xml',
        'view/res_country.xml',
        # sanction
        'sanction/security/ir.model.access.csv',
        'sanction/security/sanction_security.xml',
        'sanction/wizard/wizard_deprivation_action_view.xml',
        'sanction/wizard/wizard_sanction_action.xml',
        'sanction/hr_sanction_type_data.xml',
        'sanction/hr_sanction_view.xml',
        'sanction/views/hr_deprivation_premium_report.xml',
        'sanction/views/report.xml',
       # 'sanction/hr_deprivation_premium_view.xml',
        # القرارات
        'hr_decision/hr_decision.xml',
        'hr_decision/hr_decision_setting.xml',
        'hr_decision/wizard/wizard_hr_decision.xml',
        # الرواتب
        'payroll/menu.xml',

        'payroll/views/report_hr_deduction.xml',
        'payroll/views/report_payslip.xml',
        'payroll/views/report_payslip_extension.xml',
        'payroll/views/report_hr_payslip_changement.xml',
        'payroll/views/report_hr_error_employee_run.xml',
        'payroll/views/report_hr_increase_employee.xml',
        'payroll/views/report.xml',

        'payroll/data/salary_grid_type_data.xml',
        'payroll/wizard/wizard_bonus_employee.xml',
        'payroll/wizard/wizard_bonus_action.xml',
        'payroll/wizard/wizard_deducation_action.xml',
        'payroll/wizard/wizard_loan_action.xml',
        'payroll/wizard/hr_refuse_wizard_view.xml',
        'payroll/wizard/wizard_update_salary_grid_view.xml',
        'payroll/view/salary_grid.xml',
        'payroll/view/hr_payroll_view.xml',
        'payroll/view/hr_special_payslip_view.xml',
        'payroll/view/hr_payslip_stop_view.xml',
        'payroll/view/hr_payslip_stop_run_view.xml',
        'payroll/view/setting_view.xml',
        'payroll/view/hr_salary_rule_view.xml',
        'payroll/view/hr_deduction.xml',
        'payroll/view/hr_bonus_view.xml',
        'payroll/view/hr_loan_view.xml',
        'payroll/view/hr_increase_view.xml',
        'payroll/view/period_fiscalyear.xml',
        'payroll/view/hr_differential.xml',
        'payroll/view/hr_payslip_difference_history_view.xml',



        # الحضور والإنصراف
        'attendance/security/attendance_security.xml',
        'attendance/security/ir.model.access.csv',
        'attendance/data/data.xml',
        'attendance/data/schedulers.xml',
        'attendance/menu.xml',
        'attendance/views/report.xml',
        'attendance/view/hr_resource_calendar.xml',
        'attendance/view/hr_attendance_schedule.xml',
        'attendance/view/hr_public_holiday.xml',
        'attendance/view/hr_attendance_import_view.xml',
        'attendance/view/hr_attendance.xml',
        'attendance/view/hr_attendance.xml',
        'attendance/view/hr_extra_hours.xml',
        'attendance/view/hr_authorization_view.xml',
        'attendance/view/hr_attendance_config.xml',
        'attendance/view/hr_request_transfer_view.xml',
        'attendance/view/report_day_view.xml',
        'attendance/view/hr_attendance_check_view.xml',
        'attendance/view/hr_attendance_report_view.xml',
        'attendance/view/hr_monthly_summary_view.xml',
        'attendance/wizard/wizard_attendance_summary_view.xml',
        'attendance/views/attendance_summary_report.xml',
        'attendance/views/monthly_summary_report.xml',
        'attendance/views/monthly_summary_report_all.xml',
        'attendance/views/request_transfer_delay_hours_report.xml',
        'attendance/views/request_transfer_absence_days_report.xml',
     #   'attendance/views/absences_employees_list.xml',
       # 'attendance/views/delay_employees_list.xml',
        
        # تصنيف الوظائف
        'job/view/hr_job_setting.xml',
        'job/view/hr_skils_job.xml',
        'job/view/hr_job.xml',
        'job/view/hr_job_workflow.xml',

        # الاجازات
        'holidays/menu.xml',
        'holidays/wizard/wizard_resume_holidays_view.xml',
        'holidays/views/resume_holidays_report.xml',
        'holidays/views/resume_normal_holidays_report.xml',
        'holidays/views/report.xml',
        'holidays/view/hr_holidays.xml',
        'holidays/view/hr_holidays_cancellation_view.xml',
        'holidays/view/hr_holidays_decision_view.xml',
        'holidays/view/holiday_entitlement_types.xml',
        'holidays/view/hr_holidays_extension.xml',
        'holidays/views/hr_holidays_report.xml',
        'holidays/views/report_hr_holidays_decision.xml',

        'view/hr.xml',
        # التقييم والإختبار
        'hr_appraisal/security/ir.model.access.csv',
        'hr_appraisal/view/hr_appraisal_menu.xml',
        'hr_appraisal/view/hr_appraisal_view.xml',
        'hr_appraisal/view/hr_evaluation_point_view.xml',

        # promotion
        'hr_promotions/wizard/hr_promotion_benefits_wizard_view.xml',
        'hr_promotions/view/hr_promotion_view.xml',
        'hr_promotions/view/hr_employee_promotion_view.xml',

        # deputation
        'deputation/security/ir.model.access.csv',
        'deputation/data/data.xml',
        'deputation/view/hr_deputation_setting.xml',
        'deputation/view/hr_deputation_view.xml',
        'deputation/view/transport_decision_view.xml',
        'deputation/views/deputation_report.xml',
        'deputation/views/report.xml',
        # overtime
        'overtime/security/security_view.xml',
        'overtime/security/ir.model.access.csv',
        'overtime/data/data.xml',
        'overtime/wizard/overtime_cut_wizard_view.xml',
        'overtime/view/hr_overtime_view.xml',
        'overtime/view/hr_overtime_setting.xml',
        'overtime/views/overtime_report.xml',
        'overtime/views/report.xml',
        # hr_scholarship
        'hr_scholarship/data/sequences.xml',
        'hr_scholarship/data/scholarship_data.xml',
        'hr_scholarship/views/report_hr_scholarship_decision.xml',
        'hr_scholarship/view/hr_scholarship.xml',
        'hr_scholarship/wizards/view/hr_scholarship_succeed_wizard.xml',
        'hr_scholarship/wizards/view/hr_scholarship_extend_wizard.xml',
        'hr_scholarship/views/hr_scholarship_extension_report.xml',
        'hr_scholarship/views/report.xml',
        'employee_durations/views/promotion_duration_view.xml',
        'employee_durations/views/service_duration_view.xml',
        # 'hr_survey/views/website_templates.xml',

    ],
    'auto_install': False,
    'sequence': 150,
}
