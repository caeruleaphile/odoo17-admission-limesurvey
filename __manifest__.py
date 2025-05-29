{
    'name': 'Admission Hub',
    'version': '17.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Manage and synchronize LimeSurvey forms in Odoo',
    'description': """
        This module allows to manage and automatically synchronize LimeSurvey forms in Odoo.
        Features:
        - LimeSurvey form configuration
        - Automatic synchronization
        - Form tracking and monitoring
    """,
    'author': 'bannour-imane',
    'website': 'https://www.odoo.com',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/limesurvey_config_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
} 