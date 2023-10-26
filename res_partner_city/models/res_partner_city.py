from odoo import models, fields, api
 
class ResPartnerCity(models.Model):
 	_name = "res.partner.city"

 	name = fields.Char("Name", store=True, requried=True)
 	code = fields.Char("Code", store=True, requried=True)
 	state_id = fields.Many2one("res.country.state", string="State", store=True, requried=True)
 	active = fields.Boolean(default=True)
 	
 	@api.multi
 	def toggle_active(self):
 		for ct in self:
 			if not ct.active:
 				ct.active= self.active
 			super(ResPartnerCity, self).toggle_active()