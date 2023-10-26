# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

import time
from odoo import models, api, fields, _
from odoo.exceptions import Warning
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta


class inventory_reports(models.TransientModel):
    _name = 'inventory.in.out.reports'

    # @api.one
    # @api.depends('company_id')
    # def _company_id(self):
    #     user_id = self.env.uid
    #     company = self.env['res.users'].browse(user_id).company_id
    #     self.company_id = company
    #     return self.company_id

    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.user.company_id)
    warehouse_ids = fields.Many2many('stock.warehouse', string='warehouse')
    location_id = fields.Many2one('stock.location', string='Location')
    start_date = fields.Date('Beginning Date', required=True, default= lambda *a:(parser.parse(datetime.now().strftime('%Y-%m-%d')) + relativedelta(days=-1)).strftime('%Y-%m-%d'))
    end_date = fields.Date('End Date', required=True, default= lambda *a :  time.strftime('%Y-%m-%d'))
    sort_order = fields.Selection([('warehouse', 'Warehouse'), ('product_category', 'Product Category')], 'Group By', required=True, default='warehouse')
    include_zero = fields.Boolean('Include Zero Movement?', help="True, if you want to see zero movements of products.\nNote: It will consider only movements done in-between dates.")
    filter_product_ids = fields.Many2many('product.product', string='Products')
    filter_product_categ_ids = fields.Many2many('product.category', string='Categories')
    display_all_products = fields.Boolean('Display Products?', help="True, if you want to display only warehouse/categories total.", default=True)
    
    @api.onchange('sort_order')
    def onchange_sortorder(self):
        """
        Set blank values
        """
        if self.sort_order == 'warehouse':
            self.filter_product_categ_ids = False
        elif self.sort_order == 'product_category':
            self.filter_product_ids = False
        else:
            self.filter_product_categ_ids = False
            self.filter_product_ids = False

    @api.onchange('company_id')
    def onchange_company_id(self):
        """
        Make warehouse compatible with company
        """
        warehouse_ids = self.env['stock.warehouse'].sudo().search([])
        if self.company_id:
            warehouse_ids = self.env['stock.warehouse'].sudo().search([('company_id', '=', self.company_id.id)])
        return {
                'domain':
                        {
                         'warehouse_ids': [('id', 'in', [x.id for x in warehouse_ids])]
                         },
                'value':
                        {
                        'warehouse_ids': False
                        }
                }

    @api.onchange('warehouse_ids')
    def onchange_warehouse(self):
        """
        Make warehouse compatible with company
        """
        location_obj = self.env['stock.location']
        location_ids = location_obj.search([('usage', '=', 'internal')])
        total_warehouses = self.warehouse_ids
        if total_warehouses:
            addtional_ids = []
            for warehouse in total_warehouses:
                store_location_id = warehouse.view_location_id.id
                addtional_ids.extend([y.id for y in location_obj.search([('location_id', 'child_of', store_location_id), ('usage', '=', 'internal')])])
            location_ids = addtional_ids
        else:
            location_ids = [p.id for p in location_ids]
        return {
                  'domain':
                            {
                             'location_id': [('id', 'in', location_ids)]
                             },
                  'value':
                        {
                        'location_id': False
                        }
                }

    @api.multi
    def print_report(self):
        """
            Print report either by warehouse or product-category
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        datas = {
                 'form':
                        {
                            'company_id': self.company_id and [self.company_id.id] or [],
                            'warehouse_ids': [y.id for y in self.warehouse_ids],
                            'location_id': self.location_id and self.location_id.id or False,
                            'start_date': self.start_date,
                            'end_date': self.end_date,
                            'include_zero': self.include_zero,
                            'sort_order': self.sort_order,
                            'display_all_products': self.display_all_products,
                            'id': self.id,
                            'filter_product_ids': [p.id for p in self.filter_product_ids],
                            'filter_product_categ_ids': [p.id for p in self.filter_product_categ_ids] 
                        }
                }

        if [y.id for y in self.warehouse_ids] and (not self.company_id):
            self.warehouse_ids = []
            raise Warning(_('Please select company of those warehouses to get correct view.\nYou should remove all warehouses first from selection field.'))
        sort_by = self.sort_order or 'warehouse'
        if sort_by == 'product_category':
            return self.env.ref(
                                'inventory_in_out_report.action_inventory_report_by_category'
                                ).with_context(landscape=True).report_action(self, data=datas)
        return self.env.ref(
                            'inventory_in_out_report.action_inventory_report_by_warehouse'
                            ).with_context(landscape=True).report_action(self, data=datas)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
