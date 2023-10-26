{
    'name'          : 'Account Invoice Extension',
    'version'       : '12.0.1.4',
    'category'      : 'account',
    'summary'       : "Discount and Tax on total in Invoice with Line Discount Fixed/Percentage and Journal Entry",
    'author'        : 'Aung Myo Swe',
    'website'       : 'www.asiamatrixsoftware.com',
    'email'         : 'aungmyoswe@asiamatrixsoft.com',
    'description'   : """

Account Invoice Extension for Total Amount and Journal Entry
==================================================
Module to manage discount and tax on total amount in Invoice.
        as an specific amount and journal.
""",
    'depends'       : ['account','base'],
    'data'          : ['views/res_config_setting_view.xml',
        'views/account_invoice_view.xml',
        'report/account_invoice_report.xml'],
    'images'        : ['static/description/icon.png'],
    'application'   : True,
    'installable'   : True,
    'auto_install'  : False,
}
