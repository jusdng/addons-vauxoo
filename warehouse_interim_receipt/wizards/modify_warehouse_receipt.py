# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Katherine Zaoral <kathy@vauxoo.com>
#    planned by: Rafael Silva <rsilvam@vauxoo.com>
############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class ModifyWarehouseReceipt(models.TransientModel):

    _name = 'wizard.modify.warehouse.receipt'
    _description = ('Batch modify warehouse receipt numbers')

    warehouse_receipt_id = fields.Many2one(
        'warehouse.receipt', string="Warehouse Receipt",
        help='Warehouse receipt to be set in the selected move lines')

    @api.model
    def _get_lines(self):
        """
        Get the move lines form current picking
        :return: a list of dictionaries to create the new wizard lines.
        """
        res = []
        self.check_active_model()
        picking = self._context.get('active_id', False)
        if not picking:
            return res
        picking = self.env['stock.picking'].browse(picking)
        res = [(0, 0, {'move_id': line.id, 'product_id': line.product_id.id})
               for line in picking.move_lines
               if line.state != 'done']
        return res

    lines = fields.One2many(
        'wizard.modify.warehouse.receipt.line', 'wizard_id',
        default=_get_lines)

    @api.model
    def check_active_model(self):
        """
        Check that the active model is stock picking if not raise a warning.
        """
        model = self._context.get('active_model', False)
        if model != 'stock.picking':
            raise UserError(
                _('This wizard need to be called from a stock picking model'))

    @api.multi
    def modify(self):
        """ Write the stock moves with the warehouse receipt given in the
        wizard.
        """
        for wizard in self:
            moves_to_update = wizard.lines.mapped('move_id')
            for move in moves_to_update:
                move.warehouse_receipt_id = wizard.warehouse_receipt_id


class ModifyWarehouseReceiptLine(models.TransientModel):

    _name = 'wizard.modify.warehouse.receipt.line'
    _description = 'Modify Warehouse Receipt Line'

    wizard_id = fields.Many2one(
        'wizard.modify.warehouse.receipt', 'Modify Wizard')
    move_id = fields.Many2one('stock.move', 'Move Line')
    product_id = fields.Many2one('product.product', 'Product')
