{
    'name'              : 'Product Brand Manager',
    'version'           : '12.0.1.0.0',
    'category'          : 'Product',
    'summary'           : "Product Brand Manager",
    'author'            : 'Yi Yi Aung',
    'email'             : 'yiyiaung@asiamatrixsoftware.com',
    'website'           : 'asiamatrixsoftware.com',
    'license'           : 'AGPL-3',
    'descriptiion'      : """
    *****************************************************************
     This module is customization for Product Brand Manager
    *****************************************************************
     Product Brand Manger is to seperste the Supplier and Class""",
    'depends'           : ['stock'],
    'data'              : ['security/ir.model.access.csv',
            'views/product_brand_view.xml',],
            #'reports/pos_order_report.xml',],
            # 'reports/sale_report_view.xml',
            # 'reports/account_invoice_report_view.xml'],
    'images'            : ['static/description/icon.png'],
    'installable'       : True,
    'auto_install'      : False,
    'application'       : True,
}
