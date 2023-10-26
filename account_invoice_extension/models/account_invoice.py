# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.tools import float_is_zero
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice','discount_type', 'discount_rate','tax_type' , 'invoice_line_ids')
    def _compute_amount(self):
        # self.amount_tax = sum(line.amount for line in self.tax_line_ids)
        for inv in self:
            amt_total = amount_untaxed =  amount_discount = self.amount_discount = self.amount_tax = line_discount= 0.0
            for line in inv.invoice_line_ids:
                if line.discount_line_type == 'fixed':
                    line_discount += (line.dis_amount*line.quantity)
                elif line.discount_line_type == 'percent':
                    line_discount += ((line.quantity * line.price_unit) * line.dis_amount)/100
                else:
                    line_discount = line_discount
                if inv.discount_type == 'fixed':
                    amount_untaxed  += line.price_subtotal 
                    self.amount_untaxed = amount_untaxed 
                    line.discount = 0.0
                    amount_discount = self.discount_rate
                elif inv.discount_type == 'percent':
                    amount_untaxed += line.quantity * line.price_unit
                    self.amount_untaxed = amount_untaxed
                    amount_discount += ((line.quantity * line.price_unit) * self.discount_rate)/100
                else:
                    amount_untaxed  += line.price_subtotal 
                    self.amount_untaxed = amount_untaxed
                    self.amount_discount = 0.0
                    self.discount_rate = 0.0  
        amount_tax = 0.0
        self.amount_discount = amount_discount + line_discount
        # self.total = self.amount_untaxed - self.amount_discount
        self.disc_sub_total = self.amount_untaxed - self.amount_discount
        self.amount_total = self.amount_untaxed - self.amount_discount
        if self.company_id.global_tax == True and self.is_tax == True:
            if self.company_id.account_sale_tax_id.account_id:
                if self.tax_type == 'exclude_tax':
                    self.amount_total = 0
                    amount_tax = (self.disc_sub_total*self.company_id.account_sale_tax_id.amount)/100
                    self.amount_tax = amount_tax
                    amt_total = self.amount_untaxed - self.amount_discount + self.amount_tax
                    self.amount_total = amt_total
                elif self.tax_type == 'include_tax':
                    self.amount_total = 0
                    amount_tax =  self.disc_sub_total - (self.disc_sub_total / (1 + self.company_id.account_sale_tax_id.amount/ 100))
                    self.disc_sub_total = 0
                    self.disc_sub_total = self.amount_untaxed - self.amount_discount
                    self.amount_tax = amount_tax
                    amt_total = self.amount_untaxed - self.amount_discount + self.amount_tax
                    self.amount_total = amt_total
                else:
                    self.amount_total = 0
                    amt_total = self.amount_untaxed - self.amount_discount
                    self.amount_total = amt_total
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        residual = 0.0
        residual_company_signed = 0.0
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        for line in self.sudo().move_id.line_ids:
            if line.account_id == self.account_id:
                residual_company_signed += line.amount_residual
                if line.currency_id == self.currency_id:
                    residual += line.amount_residual_currency  if line.currency_id else line.amount_residual
                
                else:
                    from_currency = line.currency_id or line.company_id.currency_id
                    residual += from_currency._convert(line.amount_residual, self.currency_id, line.company_id, line.date or fields.Date.today())
        self.residual_company_signed = abs(residual_company_signed) * sign
        self.residual_signed = abs(residual) * sign
        self.residual = abs(residual)
        digits_rounding_precision = self.currency_id.rounding
        if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False

    discount_type = fields.Selection([('percent','Percentage'),('fixed', 'Fixed')], string='Type',readonly=True, states={'draft': [('readonly', False)]}, default='fixed')
    discount_rate = fields.Float('Amount', digits=(16, 1), readonly=True,states={'draft': [('readonly', False)]}, default=0.0)
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_compute_amount',track_visibility='always')
    # total = fields.Monetary(string='Total', store=True, readonly=True, compute='_compute_amount',track_visibility='always', currency_field='company_currency_id')
    disc_sub_total = fields.Monetary(string='After Discount Total', store=True, readonly=True, compute='_compute_amount',track_visibility='always')
    amount_total = fields.Monetary(string='Net Total',store=True, readonly=True, compute='_compute_amount')
    tax = fields.Boolean(string = "Global Tax", related="company_id.global_tax", store=True)
    is_tax = fields.Boolean(string="Is Tax", default=False, store=True)
    tax_type = fields.Selection([('include_tax',"Include Tax"),('exclude_tax',"Exclude Tax")],string="Tax Payment Type")

    @api.onchange('discount_type', 'discount_rate', 'invoice_line_ids','tax_type')
    def supply_rate(self):
        for inv in self:
            amount_total =amount_untaxed =  amount_discount = line_discount = total = 0.0
            for line in inv.invoice_line_ids:
                if line.discount_line_type == 'fixed':
                    line_discount += (line.dis_amount * line.quantity)
                elif line.discount_line_type == 'percent':
                    line_discount += ((line.quantity * line.price_unit) * line.dis_amount)/100
                else:
                    line_discount = line_discount
                if inv.discount_type == 'fixed':
                    amount_untaxed += line.price_subtotal 
                    self.amount_untaxed = amount_untaxed
                    line.discount = 0.0
                    amount_discount = self.discount_rate
                elif inv.discount_type == 'percent':
                    amount_untaxed += line.quantity * line.price_unit
                    self.amount_untaxed = amount_untaxed
                    amount_discount += ((line.quantity * line.price_unit) * self.discount_rate)/100
                else:
                    amount_untaxed += line.price_subtotal 
                    self.amount_untaxed = amount_untaxed
                    self.amount_discount = 0.0
                    self.discount_rate = 0.0
        amount_tax = 0.0
        self.amount_discount = amount_discount + line_discount
        self.disc_sub_total =  self.amount_untaxed - self.amount_discount
        amt_total = self.amount_untaxed - self.amount_discount
        self.amount_total = amt_total
        if self.company_id.global_tax == True and self.is_tax == True:
            # if self.company_id.account_purchase_tax_id.account_id:
            #     amount_tax = (self.disc_sub_total*self.company_id.account_purchase_tax_id.amount)/100
            if self.company_id.account_sale_tax_id.account_id:
                if self.tax_type == 'exclude_tax':
                    self.amount_total = amt_total = 0
                    amount_tax = (self.disc_sub_total*self.company_id.account_sale_tax_id.amount)/100
                    self.amount_tax = amount_tax
                    amt_total = (self.amount_untaxed - self.amount_discount) + self.amount_tax
                    self.amount_total = amt_total
                elif self.tax_type == 'include_tax':
                    self.amount_total = amt_total = 0
                    amount_tax =  self.disc_sub_total - (self.disc_sub_total / (1 + self.company_id.account_sale_tax_id.amount/ 100))
                    self.disc_sub_total = 0
                    self.disc_sub_total = (self.amount_untaxed - self.amount_discount) - amount_tax
                    self.amount_tax = amount_tax
                    amt_total = self.amount_untaxed - self.amount_discount
                    self.amount_total = amt_total
                else:
                    self.amount_total = amt_total = 0
                    amt_total = self.amount_untaxed - self.amount_discount
                    self.amount_total = amt_total
        

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.is_tax = self.company_id.global_tax

    # @api.onchange('tax_type')
    # def onchange_tax_type(self):
    #     residual = 0
    #     if self.tax_type == 'include_tax':
    #         print ("Hello")
    #         residual = self.residual - self.amount_tax
    #         self.residual = 0
    #     p
    #     self.residual = residual

    @api.multi
    def compute_invoice_totals(self, company_currency, invoice_move_lines):
        total = 0
        total_currency = 0
        for line in invoice_move_lines:
            if self.currency_id != company_currency:
                currency = self.currency_id
                date = self._get_currency_rate_date() or fields.Date.context_today(self)
                if not (line.get('currency_id') and line.get('amount_currency')):
                    line['currency_id'] = currency.id
                    line['amount_currency'] = currency.round(line['price'])
                    line['price'] = currency._convert(line['price'], company_currency, self.company_id, date)
            else:
                line['currency_id'] = False
                line['amount_currency'] = False
                line['price'] = self.currency_id.round(line['price'])
            if self.type in ('out_invoice', 'in_refund'):
                total += line['price']
                total_currency += line['amount_currency'] or line['price']
                line['price'] = - line['price']
            else:
                total -= line['price']
                total_currency -= line['amount_currency'] or line['price']
        dis_type = None
        for inv_line in self.invoice_line_ids:
            if self.discount_type == 'fixed' or inv_line.discount_line_type == 'fixed':
                dis_type = 'fixed'      
            if self.discount_type == 'percent' or inv_line.discount_line_type == 'percent':
                dis_type = 'percent'
        if dis_type == 'fixed' or dis_type == 'percent':
             total -= self.amount_discount
        else:
            total = total
        return total, total_currency, invoice_move_lines

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids.filtered(lambda line: line.account_id):
                raise UserError(_('Please add at least one invoice line.'))
            if inv.move_id:
                continue
            if not inv.date_invoice:
                inv.write({'date_invoice': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.write({'date_due': inv.date_invoice})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            # iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.compute_invoice_totals(company_currency, iml)

            name = inv.name or ''
            amount = 0
            l_dis_type = None
            if inv.payment_term_id:
                totlines = inv.payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency._convert(t[1], inv.currency_id, inv.company_id, inv._get_currency_rate_date() or fields.Date.today())
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency
                    for inv_l in inv.invoice_line_ids:
                        if inv_l.discount_line_type == 'fixed':
                            l_dis_type = 'fixed'
                        if inv_l.discount_line_type == 'percent':
                            l_dis_type = 'percent'
                    if inv.discount_type == 'fixed' or l_dis_type == 'fixed' and inv.partner_id.supplier != True:
                        tax = 0.0
                        if inv.is_tax == True and inv.tax_type =='include_tax':
                            tax = inv.amount_tax
                            tax_id = self.company_id.account_sale_tax_id.account_id.id
                            if not tax_id:
                                raise UserError(_('Please check purchase account tax.')) 
                            iml.append({
                                'type': 'dest',
                                'name': 'Global Tax',
                                'price': - tax,
                                'account_id': tax_id,
                                'amount_currency': diff_currency and total_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id
                            })
                            amount += t[1]
                            amount = amount + tax
                        elif inv.is_tax == True and inv.tax_type =='exclude_tax':
                            tax = inv.amount_tax
                            tax_id = self.company_id.account_sale_tax_id.account_id.id
                            if not tax_id:
                                raise UserError(_('Please check purchase account tax.')) 
                            iml.append({
                                'type': 'dest',
                                'name': 'Global Tax',
                                'price': -tax,
                                'account_id': tax_id,
                                'amount_currency': diff_currency and total_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id
                            })
                            amount += t[1]
                            amount += tax
                        else:
                            tax = 0.0
                            amount += t[1]
                            amount += tax
                        # amount += inv.amount_discount
                        sale_discount = self.env['res.company'].search([]).sale_discount
                        if not sale_discount:
                            raise UserError(_('Please check sale account ID')) 
                        dis_account_id = sale_discount.id
                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': amount,
                            'account_id': inv.account_id.id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                        iml.append({
                            'type': 'dest',
                            'name': "Discount",
                            'price': inv.amount_discount,
                            'account_id': dis_account_id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                        print ("line",iml)
                    elif inv.discount_type == 'percent' or l_dis_type == 'percent' and inv.partner_id.supplier != True:
                        tax = 0.0
                        if inv.is_tax == True and inv.tax_type =='include_tax':
                            tax = inv.amount_tax
                            tax_id = self.company_id.account_sale_tax_id.account_id.id
                            if not tax_id:
                                raise UserError(_('Please check Sale account tax.'))
                            iml.append({
                                'type': 'dest',
                                'name': 'Global Tax',
                                'price': -tax,
                                'account_id': tax_id,
                                'amount_currency': diff_currency and total_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id})
                            amount = t[1]
                            amount = amount + tax
                        elif inv.is_tax == True and inv.tax_type =='exclude_tax':
                            tax = inv.amount_tax
                            tax_id = self.company_id.account_sale_tax_id.account_id.id
                            if not tax_id:
                                raise UserError(_('Please check purchase account tax.')) 
                            iml.append({
                                'type': 'dest',
                                'name': 'Global Tax',
                                'price': -tax,
                                'account_id': tax_id,
                                'amount_currency': diff_currency and total_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id
                            })
                            amount = t[1] 
                            amount += tax
                        else:
                            tax = 0.0
                            amount += tax
                            amount = t[1]
                        # amount += inv.amount_discount
                        sale_discount = self.env['res.company'].search([]).sale_discount
                        if not sale_discount:
                            raise UserError(_('Please check sale account ID')) 
                        dis_account_id = sale_discount.id
                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': amount,
                            'account_id': inv.account_id.id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                        iml.append({
                            'type': 'dest',
                            'name': "Discount",
                            'price': inv.amount_discount,
                            'account_id': dis_account_id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                    elif inv.discount_type == 'fixed' and inv.partner_id.customer != True:
                        journal = self.env['res.company'].browse(self.company_id.id).purchase_discount_journal
                        if not journal:
                            raise UserError(_('Please check purchase Account ID'))
                        dis_account_id = journal.default_debit_account_id.id
                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': total,
                            'account_id': inv.account_id.id,
                            'date_maturity': inv.date_due,
                            'amount_currency': diff_currency and total_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                        iml.append({
                            'type': 'dest',
                            'name': 'Discount',
                            'price': -inv.amount_discount,
                            'account_id': dis_account_id,
                            'date_maturity': inv.date_due,
                            'amount_currency': diff_currency and total_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                    elif inv.discount_type == 'percent' and inv.partner_id.customer != True:
                        # total += inv.amount_discount
                        journal = self.env['res.company'].browse(self.company_id.id).purchase_discount_journal
                        if not journal:
                            raise UserError(_('Please check purchase Account ID'))
                        dis_account_id = journal.default_debit_account_id.id
                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': total,
                            'account_id': inv.account_id.id,
                            'date_maturity': inv.date_due,
                            'amount_currency': diff_currency and total_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                        iml.append({
                            'type': 'dest',
                            'name': 'Discount',
                            'price': -inv.amount_discount,
                            'account_id': dis_account_id,
                            'date_maturity': inv.date_due,
                            'amount_currency': diff_currency and total_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                    else:
                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': t[1],
                            'account_id': inv.account_id.id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
            else:
                if inv.discount_type == 'fixed' or l_dis_type == 'fixed' and inv.partner_id.supplier != True:
                    tax = 0.0
                    if inv.is_tax == True and inv.tax_type == 'include_tax':
                        tax = inv.amount_tax
                        tax_id = self.company_id.account_sale_tax_id.account_id.id
                        if not tax_id:
                            raise UserError(_('Please check Sale account tax.'))
                        iml.append({
                            'type': 'dest',
                            'name': 'Global Tax',
                            'price': -tax,
                            'account_id': tax_id,
                            'amount_currency': diff_currency and total_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                        total = total
                        total = total + tax
                    elif inv.is_tax == True and inv.tax_type == 'exclude_tax':
                        tax = inv.amount_tax
                        tax_id = self.company_id.account_sale_tax_id.account_id.id
                        if not tax_id:
                            raise UserError(_('Please check Sale account tax.'))
                        iml.append({
                            'type': 'dest',
                            'name': 'Global Tax',
                            'price': -tax,
                            'account_id': tax_id,
                            'amount_currency': diff_currency and total_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                        total += tax
                    else:
                        tax = 0.0
                        total += tax
                    # total += inv.amount_discount
                    sale_discount = self.env['res.company'].browse(self.company_id.id).sale_discount
                    if not sale_discount:
                        raise UserError(_('Please check sale journal'))
                    dis_account_id = sale_discount.id
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total,
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                    iml.append({
                        'type': 'dest',
                        'name': 'Discount',
                        'price': inv.amount_discount,
                        'account_id': dis_account_id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                elif inv.discount_type == 'percent' or l_dis_type == 'percent' and inv.partner_id.supplier != True:
                    tax = 0.0
                    if inv.is_tax == True and inv.tax_type == 'include_tax':
                        tax = inv.amount_tax
                        tax_id = self.company_id.account_sale_tax_id.account_id.id
                        if not tax_id:
                            raise UserError(_('Please check Sale account tax.'))
                        iml.append({
                            'type': 'dest',
                            'name': 'Global Tax',
                            'price': -tax,
                            'account_id': tax_id,
                            'amount_currency': diff_currency and total_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                        amount = total + tax
                    if inv.is_tax == True and inv.tax_type == 'exclude_tax':
                        tax = inv.amount_tax
                        tax_id = self.company_id.account_sale_tax_id.account_id.id
                        if not tax_id:
                            raise UserError(_('Please check Sale account tax.'))
                        iml.append({
                            'type': 'dest',
                            'name': 'Global Tax',
                            'price': -tax,
                            'account_id': tax_id,
                            'amount_currency': diff_currency and total_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                        total += tax
                    else:
                        tax = 0.0
                        total += tax
                    # total += inv.amount_discount
                    sale_discount = self.env['res.company'].browse(self.company_id.id).sale_discount
                    if not sale_discount:
                        raise UserError(_('Please check sale Account ID'))
                    dis_account_id = sale_discount.id
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total,
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                    iml.append({
                        'type': 'dest',
                        'name': 'Discount',
                        'price': inv.amount_discount,
                        'account_id': dis_account_id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                elif inv.discount_type == 'fixed' and inv.partner_id.customer != True:
                    total += inv.amount_discount
                    purchase_discount = self.env['res.company'].browse(self.company_id.id).purchase_discount
                    if not purchase_discount:
                        raise UserError(_('Please check purchase account ID'))
                    dis_account_id = purchase_discount.id
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total + inv.amount_discount,
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                    iml.append({
                        'type': 'dest',
                        'name': 'Discount',
                        'price': -inv.amount_discount,
                        'account_id': dis_account_id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                elif inv.discount_type == 'percent' and inv.partner_id.customer != True:
                    purchase_discount = self.env['res.company'].browse(self.company_id.id).purchase_discount
                    if not purchase_discount:
                        raise UserError(_('Please check purchase account ID'))
                    dis_account_id = purchase_discount.id
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total + inv.amount_discount,
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                    iml.append({
                        'type': 'dest',
                        'name': 'Discount',
                        'price': -inv.amount_discount,
                        'account_id': dis_account_id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                else:
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total,
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            print ("IML",iml)
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)
            line = inv.finalize_invoice_move_lines(line)
            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': inv.journal_id.id,
                'date': date,
                'narration': inv.comment,
            }
            move = account_move.create(move_vals)
            # Pass invoice in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post(invoice = inv)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.write(vals)
        return True

    @api.multi
    def button_dummy(self):
        self.supply_rate()
        return True

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    discount_line_type = fields.Selection([('fixed',"Fixed"),('percent',"Percentage")], string="Discount Type", default='percent')
    dis_amount = fields.Float(string='Discount', digits=(16, 2), invisible="[('discount_line_type','=','fixed')]",  store=True)

    # @api.one
    # @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
    #     'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
    #     'invoice_id.date_invoice', 'invoice_id.date')
    # def _compute_price(self):
    #     currency = self.invoice_id and self.invoice_id.currency_id or None
    #     price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
    #     tax = 0
    #     # # if self.invoice_line_tax_ids:
    #     # #     taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
    #     self.price_subtotal = price_subtotal_signed =  self.quantity * price
    #     if self.invoice_id.tax_type == 'include_tax':
    #         tax = self.price_subtotal - (self.price_subtotal / (1 + self.company_id.account_sale_tax_id.amount/ 100))
    #         self.price_subtotal = 0.0
    #         self.price_subtotal = (self.quantity * price) - tax
    #         print ("Sub Total",self.price_subtotal)
    #     self.price_total = self.price_subtotal
    #     if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
    #         currency = self.invoice_id.currency_id
    #         date = self.invoice_id._get_currency_rate_date()
    #         price_subtotal_signed = currency._convert(price_subtotal_signed, self.invoice_id.company_id.currency_id, self.company_id or self.env.user.company_id, date or fields.Date.today())
    #     sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
    #     self.price_subtotal_signed = price_subtotal_signed * sign

class res_company(models.Model):
    _inherit = "res.company"

    sale_discount = fields.Many2one("account.account",string="Sale Discount")
    purchase_discount= fields.Many2one("account.account",string="Purchase Discount")
    global_tax = fields.Boolean("Global Tax", default=False, store=True)


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'
    _inherit = 'res.config.settings'

    @api.one
    @api.depends('company_id')
    def _get_sale_journal_id(self):
        self.sale_discount = self.company_id.sale_discount

    @api.one
    @api.depends('company_id')
    def _get_purchase_journal_id(self):
        self.purchase_discount = self.company_id.purchase_discount

    @api.one
    @api.depends('company_id')
    def _get_global_tax(self):
        self.global_tax = self.company_id.global_tax


    sale_discount = fields.Many2one('account.account', related="company_id.sale_discount", readonly=False,string='Sale Journal', help="Sale Discount of the company.")
    purchase_discount = fields.Many2one('account.account', related="company_id.purchase_discount", readonly=False,string='Sale Journal', help="Sale Discount of the company.")
    global_tax = fields.Boolean(readonly=False, string='Global Tax', related="company_id.global_tax", help="Global Tax of the company.")

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.sale_discount = self.company_id.sale_discount
        self.sale_disconnt = self.company_id.purchase_discount
        self.global_tax = self.company_id.global_tax


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.multi
    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        # Empty self can happen if the user tries to reconcile entries which are already reconciled.
        # The calling method might have filtered out reconciled lines.
        if not self:
            return True

        #Perform all checks on lines
        company_ids = set()
        all_accounts = []
        partners = set()
        for line in self:
            company_ids.add(line.company_id.id)
            all_accounts.append(line.account_id)
            if (line.account_id.internal_type in ('receivable', 'payable')):
                partners.add(line.partner_id.id)
            if line.reconciled:
                raise UserError(_('You are trying to reconcile some entries that are already reconciled.'))
        if len(company_ids) > 1:
            raise UserError(_('To reconcile the entries company should be the same for all entries.'))
        if len(set(all_accounts)) > 2:
            raise UserError(_('Entries are not from the same account.'))
        if not (all_accounts[0].reconcile or all_accounts[0].internal_type == 'liquidity'):
            raise UserError(_('Account %s (%s) does not allow reconciliation. First change the configuration of this account to allow it.') % (all_accounts[0].name, all_accounts[0].code))

        #reconcile everything that can be
        remaining_moves = self.auto_reconcile_lines()

        writeoff_to_reconcile = self.env['account.move.line']
        #if writeoff_acc_id specified, then create write-off move with value the remaining amount from move in self
        if writeoff_acc_id and writeoff_journal_id and remaining_moves:
            all_aml_share_same_currency = all([x.currency_id == self[0].currency_id for x in self])
            writeoff_vals = {
                'account_id': writeoff_acc_id.id,
                'journal_id': writeoff_journal_id.id
            }
            if not all_aml_share_same_currency:
                writeoff_vals['amount_currency'] = False
            writeoff_to_reconcile = remaining_moves._create_writeoff([writeoff_vals])
            #add writeoff line to reconcile algorithm and finish the reconciliation
            remaining_moves = (remaining_moves + writeoff_to_reconcile).auto_reconcile_lines()
        # Check if reconciliation is total or needs an exchange rate entry to be created
        (self+writeoff_to_reconcile).check_full_reconcile()
        return True
