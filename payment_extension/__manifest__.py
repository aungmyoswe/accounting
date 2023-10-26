{
    'name'              : "Payment Extension",
    'version'           : "12.0.1.0",
    'category'          : "account",
    'author'            : "Aung Myo Swe",
    'email'             : "aungmyoswe@asiamatrixsoftware.com",
    'website'           : "asiamatrixsoftware.com",
    'description'       : """
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
      This Module is customization for Account Payment Module
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& 
        Account module is extend for payment to view remaining amount in payment list.""",
        
    'depends'           : ['account'],
    'data'              : ['views/account_payment_view.xml'],
    'images'            : ['static/description/icon.png'],
    'auto_install'      : False,
    'installable'       : True,
    'application'       : True,
}