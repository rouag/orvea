# -*- coding: utf-8 -*-

{
    'name': 'Odoo RTL',
    'version': '1.1',
    'author': 'Smart',
    'sequence': 4,
    'summary': 'Web RTL(Right to Left) layout',
    'description':
        """
Adding RTL(Right to Left) Support for Odoo.

Adding RTL (Right to Left) Support for Reports.

        """,
    'depends': ['web','report'],
    'auto_install': False,
    'data': [
        'views/templates.xml',
    ],
}
