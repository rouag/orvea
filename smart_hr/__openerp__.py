# -*- coding: utf-8 -*-

{
    'name': 'Smart HR',
    'version': '9.0.1.0',
    'author': 'SMART-ETEK',
    'summary': 'HR',
    'description':
        """
        """,
    'depends': ['hr', 'hr_holidays', 'odoo_rtl', 'smart_base', 'web_readonly_bypass', 'hr_payroll'],
    'data': [


        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'payroll/security/payroll_security.xml',
        'payroll/security/ir.model.access.csv',

        'view/hr_menu.xml',

        'data/sequences.xml',
        'data/configurations.xml',
        'data/hr_holidays_data.xml',
        'data/schedulers.xml',


        'views/report_salary_grid.xml',
        'views/report_hr_deduction.xml',
        'views/report_hr_deduction_line.xml',
        'views/report_medical_examination.xml',
        'views/report_order_enquiry.xml',
        'views/hr_holidays_report.xml',
        'views/report.xml',
        'views/templates.xml',
        'views/layout.xml',

        'wizards/view/hr_refuse_wizard_view.xml',


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

        # القرارات
        'view/hr_decision.xml',
        # الرواتب
        'payroll/data.xml',
        'payroll/hr_payroll_view.xml',
        'payroll/setting_view.xml',
    ],
    'auto_install': False,
}
