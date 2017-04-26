# -*- encoding: utf-8 -*-

{
    'name': 'Internal portal',
    'version': '9.0.1.0.0',
    'category': 'Web',
    'summary': """
Internal portal
""",
    'author': "Abderrahmen Khalledi",
    'depends': ['web', 'website'
                ],
    'data': [
        'views/assets.xml',
        'views/website_template.xml',
        'views/login.xml',
        'views/index.xml',
    ],
    'installable': True,
    'application': False,
}
