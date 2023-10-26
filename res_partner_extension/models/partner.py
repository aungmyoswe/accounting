# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, tools, _
from odoo.tools import pycompat

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_default_country(self):
        if not self.country_id:
            country = self.env['res.country'].search([('name','ilike','Myanmar')]).id
        return country

    township = fields.Many2one("res.partner.township", string="Township",required=True, store=True)
    city_id = fields.Many2one("res.partner.city", string="City", store=True)
    city = fields.Char("City", related="city_id.name", store=True)
    code = fields.Char("Code", default="/",readonly=True)
    contact_name = fields.Char("Contact Name")
    state_id = fields.Many2one("res.country.state",required=True, string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('website'):
                vals['website'] = self._clean_website(vals['website'])
            if vals.get('parent_id'):
                vals['company_name'] = False
            # compute default image in create, because computing gravatar in the onchange
            # cannot be easily performed if default images are in the way
            if not vals.get('image'):
                vals['image'] = self._get_default_image(vals.get('type'), vals.get('is_company'), vals.get('parent_id'))
            tools.image_resize_images(vals, sizes={'image': (1024, None)})
            ts_code= st_code = None
            if vals.get('code', _('/')) == _('/') and vals.get('code') == None:
                print ("Partner",vals)
                s_code = str(self.env['res.country.state'].browse(vals['state_id'])['code'])
                t_code = str(self.env['res.partner.township'].browse(vals['township'])['code'])
                vals['code'] = str(self.env['ir.config_parameter'].get_param('res_partner_parameter_key')) + s_code + '/' + t_code + '/' + self.env['ir.sequence'].next_by_code('res.partner') or _('/')
        partners = super(ResPartner, self).create(vals_list)
        for partner, vals in pycompat.izip(partners, vals_list):
            partner._fields_sync(vals)
            partner._handle_first_contact_creation()
        return partners