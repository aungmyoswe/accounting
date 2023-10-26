from odoo import api, models, fields

class DeliveryTerm(models.Model):
	_name = "delivery.term"

	name = fields.Char("Name")