{
    'name': 'Admission Hub',
    'version': '17.0.1.0.0',
    'category': 'Education',
    'summary': 'Gestion des admissions via LimeSurvey',
    'sequence': 1,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menu_root.xml',
        'views/limesurvey_config_views.xml',
        'views/limesurvey_server_config_views.xml',
        'views/survey_template_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {},
    'external_dependencies': {
        'python': [],
    },
    'description': """
Module de gestion des admissions intégré avec LimeSurvey.
=======================================================

Fonctionnalités principales :
----------------------------
* Synchronisation des formulaires LimeSurvey
* Gestion des réponses
* Suivi des candidatures
* Interface moderne et intuitive
""",
} 