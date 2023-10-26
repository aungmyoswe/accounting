#---coding utf-8 ------
{
    'name': 'CRM Extension',
    'version': '12.0.1.0.0',
    'summary': "Customer Information Edition",
    'category': 'crm',
    'author':'Aung Myo Swe',
    'email': 'aungmyoswe@asiamatrix.com',
    'company': 'Asia Matrix Solutions',
    'website': 'https://www.asiamatrixsoftware.com',
    'depends': [
                'base',
                'crm',
                'res_partner_township',
                'res_partner_city',
                ],
    'data': [
            'views/crm_extension_view.xml',
            ],
    'images': ['static/description/icon.png'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
    'application': True,
}
