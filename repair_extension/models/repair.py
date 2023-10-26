from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare

class ProductTemplate(models.Model):
    _inherit = "product.template"

    service_ok = fields.Boolean('Is Spare Part', default=False)

class RepairLine(models.Model):
    _inherit = 'repair.line'
    product_id = fields.Many2one('product.product', 'Product', required=True, domain=[('service_ok','=',True)])

#name yiyiaung Repair Form Replacing date 20190619 
class Repair(models.Model):
    _inherit = 'repair.order'

    contact_name= fields.Char('Contact Person Name')
    phone= fields.Char('Phone Number')
    product_name= fields.Char('Product Name')
    product_brand= fields.Char('Product brand')
    date_receive= fields.Char('Received Date')
    date_request= fields.Char('Requset Date')
    assign= fields.Char('Assign Technician')
    product_model= fields.Char('Product Model')
    serial= fields.Char('Serial Number')
    service= fields.Char('Service')
    product_id = fields.Many2one('product.product', string='Product to Repair',required=False)
    product_qty = fields.Float('Product Quantity',required=False)
    product_uom = fields.Many2one('uom.uom', 'Product Unit of Measure',required=False)
    tracking = fields.Selection('Product Tracking', readonly=False)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('cancel', 'Cancelled'),
        ('confirmed', 'Confirmed'),
        ('under_repair', 'Under service'),
        ('ready', 'Ready to Service'),
        ('2binvoiced', 'To be Invoiced'),
        ('invoice_except', 'Invoice Exception'),
        ('done', 'Repaired')], string='Status',
        copy=False, default='draft', readonly=True, track_visibility='onchange',
        help="* The \'Draft\' status is used when a user is encoding a new and unconfirmed repair order.\n"
            "* The \'Confirmed\' status is used when a user confirms the repair order.\n"
            "* The \'Ready to Repair\' status is used to start to repairing, user can start repairing only after repair order is confirmed.\n"
            "* The \'To be Invoiced\' status is used to generate the invoice before or after repairing done.\n"
            "* The \'Done\' status is set when repairing is completed.\n"
            "* The \'Cancelled\' status is used when user cancel repair order.")

    @api.multi
    def action_repair_done(self):
        """ Creates stock move for operation and stock move for final product of repair order.
        @return: Move ids of final products

        """
        if self.filtered(lambda repair: not repair.repaired):
            raise UserError(_("Repair must be repaired in order to make the product moves."))
        res = {}
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        Move = self.env['stock.move']
        for repair in self:
            # Try to create move with the appropriate owner
            owner_id = False
            # available_qty_owner = self.env['stock.quant']._get_available_quantity(repair.product_id, repair.location_id, repair.lot_id, owner_id=repair.partner_id, strict=True)
            # if float_compare(available_qty_owner, repair.product_qty, precision_digits=precision) >= 0:
            owner_id = repair.partner_id.id

            moves = self.env['stock.move']
            for operation in repair.operations:
                print (operation,"Operation")
                move = Move.create({
                    'name': repair.name,
                    'product_id': operation.product_id.id,
                    'product_uom_qty': operation.product_uom_qty,
                    'product_uom': operation.product_uom.id,
                    'partner_id': repair.address_id.id,
                    'location_id': operation.location_id.id,
                    'location_dest_id': operation.location_dest_id.id,
                    'move_line_ids': [(0, 0, {'product_id': operation.product_id.id,
                                           'lot_id': operation.lot_id.id, 
                                           'product_uom_qty': 0,  # bypass reservation here
                                           'product_uom_id': operation.product_uom.id,
                                           'qty_done': operation.product_uom_qty,
                                           'package_id': False,
                                           'result_package_id': False,
                                           'owner_id': owner_id,
                                           'location_id': operation.location_id.id, #TODO: owner stuff
                                           'location_dest_id': operation.location_dest_id.id,})],
                    'repair_id': repair.id,
                    'origin': repair.name,
                })
                print ("move",move)
                moves |= move
                operation.write({'move_id': move.id, 'state': 'done'})
                # move = Move.create({
                #     'name': repair.name,
                #     'product_id': repair.product_id.id,
                #     'product_uom': repair.product_uom.id or repair.product_id.uom_id.id,
                #     'product_uom_qty': repair.product_qty,
                #     'partner_id': repair.address_id.id,
                #     'location_id': repair.location_id.id,
                #     'location_dest_id': repair.location_id.id,
                #     'move_line_ids': [(0, 0, {'product_id': repair.product_id.id,
                #                                'lot_id': repair.lot_id.id, 
                #                                'product_uom_qty': 0,  # bypass reservation here
                #                                'product_uom_id': repair.product_uom.id or repair.product_id.uom_id.id,
                #                                'qty_done': repair.product_qty,
                #                                'package_id': False,
                #                                'result_package_id': False,
                #                                'owner_id': owner_id,
                #                                'location_id': repair.location_id.id, #TODO: owner stuff
                #                                'location_dest_id': repair.location_id.id,})],
                #     'repair_id': repair.id,
                #     'origin': repair.name,
                # })
                consumed_lines = moves.mapped('move_line_ids')
                produced_lines = move.move_line_ids
                moves |= move
                print ("Done")
                moves._action_done()
                produced_lines.write({'consume_line_ids': [(6, 0, consumed_lines.ids)]})
                res[repair.id] = move.id
        return res

    def action_validate(self):
        self.ensure_one()
        return self.action_repair_confirm()
        # precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        # available_qty_owner = self.env['stock.quant']._get_available_quantity(self.product_id, self.location_id, self.lot_id, owner_id=self.partner_id, strict=True)
        # available_qty_noown = self.env['stock.quant']._get_available_quantity(self.product_id, self.location_id, self.lot_id, strict=True)
        # for available_qty in [available_qty_owner, available_qty_noown]:
        #     if float_compare(available_qty, self.product_qty, precision_digits=precision) >= 0:
        #         return self.action_repair_confirm()
        # else:
        #     return {
        #         'name': _('Insufficient Quantity'),
        #         'view_type': 'form',
        #         'view_mode': 'form',
        #         'res_model': 'stock.warn.insufficient.qty.repair',
        #         'view_id': self.env.ref('repair.stock_warn_insufficient_qty_repair_form_view').id,
        #         'type': 'ir.actions.act_window',
        #         'context': {
        #             'default_product_id': self.product_id.id,
        #             'default_location_id': self.location_id.id,
        #             'default_repair_id': self.id
        #             },
        #         'target': 'new'
        #     }

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    service_number = fields.Integer(compute='_compute_service_number', string="Number of Service")

    @api.multi
    def action_service_request(self):
    	value = {}
    	repair_order_obj =self.env['repair.order']
    	repair_order_ids=repair_order_obj.search([('service','=',self.name)])
    	value={'partner_id':self.partner_id.id,
            'contact_name':self.partner_name,
            'phone':self.phone,
            'product_name':self.product,
            'product_brand':self.brand,
            'date_receive':self.date_receive,
            'date_request':self.date_request,
            'assign':self.user_id.name,
            'product_model':self.model,
            'serial':self.serial_number,
            'service':self.name,}	
    	if repair_order_ids:
    	   repair_order_ids.write(value)
    	else : 
    	   repair_order_obj.create(value)

    @api.multi
    def action_get_service_view(self):
        action = self.env.ref('repair.action_repair_order_tree').read()[0]
        services = self.env['repair.order'].search([('service','=',self.name)])
        if len(services) > 1:
            action['domain'] = [('id', 'in', services.ids)]
        elif services:
            action['views'] = [(self.env.ref('repair.view_repair_order_form').id, 'form')]
            action['res_id'] = services.id
        return action

    @api.multi
    def _compute_service_number(self):
        service = self.env['repair.order'].search([('service','=',self.name)])
        if service:
           self.service_number = len(service)
        else:
           self.service_number = 0


#***************************************end****************************************************************************************************************************

class RepairFee(models.Model):
    _inherit = 'repair.fee'

    product_id = fields.Many2one('product.product', 'Product', domain=[('type','=','service')])