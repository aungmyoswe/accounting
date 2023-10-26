{
    'name'              : "helpdesk_extension",
    'version'           : "12.1.0.3",
    'category'          : "hekpdesk",
    'author'            : "Yi Yi Aung",
    'email'             : "yiyiaung@asiamatrixsoftware.com",
    'website'           : "asiamatrixsoftware.com",
    'description'       : """
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
      This Module is customization for Helpdesk_extension Module
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& 
        Helpdesk_extention module is handle from Helpdesk in DB""",
        
    'depends'           : ['helpdesk'],
    'data'              : ['security/ir.model.access.csv',
        'views/service_ticket_view.xml',
        'views/helpdesk.xml',
        'data/service_ticket_data.xml',
        'report/service_ticket_report.xml'],
    'images'            : ['static/description/icon.png'],
    'auto_install'      : False,
    'installable'       : True,
    'application'       : True,
}