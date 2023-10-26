{
    'name'          : "base_extension",
    'version'       : "12.1.0.0",
    'category'      : "base",
    'author'        : "Yi Yi Aung",
    'email'         : "yiyiaung@asiamatrixsoftware.com",
    'website'       : "asiamatrixsoftware.com",
    'description'   : """
--------------------------------------------------------------
    This Module is cutomized to add the field in company form
--------------------------------------------------------------
    The base_extension is handle from base in DB""",

    'depends'       : ['base'],
    'data'          : ['views/base.xml'],
    #'images'        : ['static/description/icon.png'],
    'auto_install'  : False,
    'installable'   : True,
    'application'   : True,
}