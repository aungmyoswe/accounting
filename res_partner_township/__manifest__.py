#---coding utf-8 ------
{
	'name'			:'Res Partner Township',
	'version'		:'12.0.1.0',
	'category'		:'base',
	'author'		:'Aung Myo Swe',
	'email'			:'aungmyoswe@asiamatrixsoftware.com',
	'website'		:'asiamatrixsoftware.com',
	'description'	:"""
**********************************************************
This Module is cusotmization for Moblie Distribution
**********************************************************
	Customer Information that handle from mobile township of customer name with code.""",

	'depends'		:['base','res_partner_city'],
	'data'			:['views/res_partner_township_view.xml',
		'security/ir.model.access.csv'],
	'images'		:['static/description/icon.png'],
	'auto_install'	: False,
	'installable'	:True,
	'application'	:True,
}