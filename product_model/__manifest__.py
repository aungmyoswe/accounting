{
    'name'              : 'Product Model Manager',
    'version'           : '12.0.1.',
    'category'          : 'Product',
    'summary'           : "Product Model Manager",
    'author'            : 'Yi Yi Aung',
    'email'             : 'yiyiaung@asiamatrixsoftware.com',
    'website'           : 'asiamatrixsoftware.com',
    'license'           : 'AGPL-3',
    'descriptiion'      : """
    *****************************************************************
     This module is customization for Product Model Manager
    *****************************************************************
     Product Brand Manger is to seperste the Supplier and Class""",
    'depends'           : ['stock'],
    'data'              : ['security/ir.model.access.csv',
            'views/product_model_view.xml'],
    'images'            : ['static/description/icon.png'],
    'installable'       : True,
    'auto_install'      : False,
    'application'       : True,
}
