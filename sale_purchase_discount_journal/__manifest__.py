{
    'name': 'Sale/Purchase Discount Journal',
    'version': '12.0.1.1',
    'category': 'Sales Management',
    'summary': "Sale/Purchase Discount on total in Invoice with Discount Fixed and Journal Entry",
    'author': 'Aung Myo Swe',
    'website': '',
    'email': 'aungmyoswe@asiamatrixsoft.com',
    'description': """

Sale/Purchase Discount for Total Amount and Journal Entry
==================================================
Module to manage discount on total amount in Sale/Purchase.
        as an specific amount  and journal.
""",
    'depends': ['account'],
    'data': ['views/account_invoice_view.xml',
        'views/res_config_view.xml',
        'report/account_invoice_report.xml'],
    'images': ['static/description/icon.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
}
