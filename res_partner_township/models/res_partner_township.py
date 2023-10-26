from odoo import models, fields, api
 
class ResPartnerTownship(models.Model):
 	_name = "res.partner.township"

 	code = fields.Char("Code", store=True, requried=True)
 	name = fields.Char("Name", store=True, requried=True)
 	city = fields.Many2one("res.partner.city", store=True, requried=True)
 	active = fields.Boolean(default=True)
 	
 	@api.multi
 	def toggle_active(self):
 		for vt in self:
 			if not vt.active:
 				vt.active= self.active
 			super(ResPartnerTownship, self).toggle_active()