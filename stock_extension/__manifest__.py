# -*- coding: utf-8 -*-
{
    'name'          : "stock_extension",
    'version'       : "12.1.0.0",
    'category'      : "stock",
    'author'        : "Yi Yi Aung",
    'email'         : "yiyiaung@asiamatrixsoftware.com",
    'website'       : "asiamatrixsoftware.com",
    'description'   : """
--------------------------------------------------------------
    This Module is cutomized to show the delivery slip
--------------------------------------------------------------
    The stock_extension is handle from stock in DB""",

    'depends'       : ['stock','base','sale_stock'],

    'data'          : ['report/delivery_report.xml',
        'views/stock_extension_view.xml',
        'security/inventory_access.xml'],
    'images'        : ['static/description/icon.png'],
    'auto_install'  : False,
    'installable'   : True,
    'application'   : True,
}