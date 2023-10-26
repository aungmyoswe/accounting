#---coding utf-8 ------
{
	'name'			:'Res Partner City',
	'version'		:'12.0.1.0',
	'category'		:'base',
	'author'		:'Aung Myo Swe',
	'email'			:'aungmyoswe@asiamatrixsoftware.com',
	'website'		:'asiamatrixsoftware.com',
	'summary'		:'Customize City Default to relation with township',
	'description'	:"""
**********************************************************
This Module is cusotmization for Moblie Distribution
**********************************************************
	Customer Information that change from mobile city of default field with name and code of relation table.""",

	'depends'		:['base','sales_team','sale','sale_management'],
	'data'			:['views/res_partner_city_view.xml',
		'security/ir.model.access.csv'],
	'images'		:['static/description/icon.png'],
	'auto_install'	: False,
	'installable'	:True,
	'application'	:True,
}