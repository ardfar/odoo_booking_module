# -*- coding: utf-8 -*-
{
    'name': 'Booking Order Module',
    'summary': 'A module to create booking order',
    'description': 'This module was created for HashMicro Technical Testing of ERP Developer Application',
    'author': 'Farras Arrafii',
    'website': 'https://farras-arrafi.my.id',
    'category': 'Testing',
    
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    # any module necessary for this one to work correctly
    'depends': [
        'base', 'sale'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        
        # For Service Team Model
        'views/service_team/tree_view.xml',
        'views/service_team/form_view.xml',
        'views/service_team/action.xml',
        
        # For Booking Order Model 
        'views/booking_order/tree_view.xml',
        'views/booking_order/form_view.xml',
        'views/booking_order/action.xml',
        
        # For Work Order Model
        'views/work_order/utilities/cancel_work_wizard.xml',
        'views/work_order/utilities/report.xml',
        'views/work_order/utilities/report_action.xml',
        'views/work_order/tree_view.xml',
        'views/work_order/form_view.xml',
        'views/work_order/action.xml',
        
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}