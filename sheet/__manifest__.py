{
	'name': 'Enquiry Form',
	'depends': ['base', 'website'],
	'data': [
        'security/ir.model.access.csv',
	    'views/views.xml',
	    'views/enquiry_form.xml',
	    'views/helpdesk_menu.xml',
	    'data/ir_sequence_data.xml',
	    # 'views/helpdesk_enquiry_templates.xml',
	    
	],
	
	'application': True,
	'license': 'LGPL-3',
}