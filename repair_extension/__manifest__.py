{
    'name'             : "repair_extension",
    'version'          : "12.1.0.4",
    'category'         : "repair",
    'author'           : "Yi Yi Aung",
    'Email'            : "yiyiaund@asiamatrixsoftware.com",
    'website'          : "asiamatrixsoftware.com",
    'description'      : """
***************************************************************
    This Module is to add the checkbox in repair form
***************************************************************
    The Repair_extension module is handle from  Repair in DB""",

    'depends'          : ['repair','helpdesk'],
    'data'             : ['views/repair.xml',
        'report/service_quatotion_template.xml'],
    'images'           : ['static/description/icon.png'],
    'auto_install'     : False,
    'installable'      : True,
    'application'      : True,
}