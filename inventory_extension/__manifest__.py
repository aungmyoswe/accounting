#---coding utf-8 ------
{
	'name'			:'Inventory Extension',
	'version'		:'12.0.1.0',
	'category'		:'base',
	'author'		:'Aung Myo Swe',
	'email'			:'aungmyoswe@asiamatrixsoftware.com',
	'website'		:'asiamatrixsoftware.com',
	'summary'		:'Customize For Inventory',
	'description'	:"""
**********************************************************
This Module is cusotmization for Inventroy Module
**********************************************************
 Add Remark field in inventroy """,
	'depends'		:['stock'],
	'data'			:['views/inventory_extension_view.xml'],
	'images'		:['static/description/icon.png'],
	'auto_install'	: False,
	'installable'	:True,
	'application'	:True,
}