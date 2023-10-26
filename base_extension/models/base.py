from odoo import models, fields, api

class Company(models.Model):
    _inherit = "res.company"

    mobile=fields.Char('Mobile',stored=True)
    service=fields.Char('Service Phone',stored=True)
    township=fields.Char('Township',stored=True)