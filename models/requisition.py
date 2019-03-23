from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    requisition_number = fields.Char('PO Requisition')

class Requisition(models.Model):
    _name = "po.requisition"
    
    name = fields.Char('PO Requisition')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True)
    delivery_date = fields.Datetime(string='Delivery Date', required=True, index=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    order_line = fields.One2many('requisition.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)

    @api.multi
    def action_approve_po_requisition(self):

        import pdb;pdb.set_trace()

        return True

    
    @api.model
    def create(self, values):
        record = super(Requisition, self).create(values)
        
        record.name = "REQ0"+str(record.id)

        return record


class RequisitionOrderLine(models.Model):
    _name = 'requisition.order.line'
    _description = 'Requisition Order Line'


    order_id = fields.Many2one('po.requisition', string='Order Reference', index=True, required=True, ondelete='cascade')
    name = fields.Text(string='Description')
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, required=True)
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True)
    
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure', required=True)

    