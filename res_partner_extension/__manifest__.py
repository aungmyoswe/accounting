#---coding utf-8 ------
{
    'name'          : 'Partner Extension',
    'version'       : '12.0.1.0',
    'category'      : 'Partner',
    'license'       : 'AGPL-3',
    'author'        : 'Aung Myo Swe',
    'email'         : 'aungmyoswe@asiamatrixsoftware.com',
    'website'       : 'http://www.asiamatrixsoftware.com',
    'description'       : 'Set credit limit warning And add needed data for sale distribution channel',
    'depends'       : ['sale_management','res_partner_township','res_partner_city'],
    'data'          : ['views/partner_view.xml',
        'data/ir_sequence_data.xml'],
    'installable'   : True,
    'auto_install'  : False,
    'application'   : True,
}
