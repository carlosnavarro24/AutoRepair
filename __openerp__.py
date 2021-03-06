{
    "name": "Open Auto Repair",
    "version": "1.0",
    "depends": [
        "base",
        "mail",
        "report_webkit",
        "board",
    ],
    "author": "Carlos Navarro",
    "category": "Sales",
    "description": """
OpenAutoRepair
===========

Este módulo permite la gestión de reparaciones de vehículos.

Al instalar el módulo se crean los objetos de Cliente,Vehiculo,Reparación y Piezas
""",
    'data': [
             'autorepair_menu.xml',
             'autorepair_view.xml',
             'autorepair_workflow.xml',
             'wizard/autorepair_wizard_report_repairs_aeroo_view.xml',
             'wizard/autorepair_wizard_report_repairs_webkit_view.xml',
             'report/autorepair_repairs_report_aeroo.xml'

             
        #all other data files, except demo data and tests
        ],
    'demo': [
    
    ],
    'test': [
        #files containg tests
    ],
    'installable': True,
    'auto_install': False,

}