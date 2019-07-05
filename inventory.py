# This file is part of trytond-stock_inventory_cost module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Eval, If, Bool
from trytond.transaction import Transaction
from trytond.pool import Pool

__all__ = ['InventoryLine', ]


class InventoryLine(metaclass=PoolMeta):
    __name__ = 'stock.inventory.line'

    _states = {
        'readonly': Eval('inventory_state') != 'draft',
        }
    _depends = ['inventory_state']

    product_uom_category = fields.Function(
        fields.Many2One('product.uom.category', 'Product Uom Category'),
        'on_change_with_product_uom_category')
    quantity_show = fields.Function(fields.Float('Quantity',
        digits=(16, Eval('unit_digits', 2)),
        depends=['unit_digits']), 'get_quantity_show')
    quantity_1 = fields.Float('Qty 1', required=True,
        digits=(16, Eval('unit_1_digits', 2)),
        states=_states, depends=['unit_1_digits'])
    uom_1 = fields.Many2One('product.uom', 'Unit 1',
        states={
            'required': Bool(Eval('product')),
            'readonly': Eval('inventory_state') != 'draft',
            },
        domain=[
            If(Bool(Eval('product_uom_category')),
                ('category', '=', Eval('product_uom_category')),
                ('category', '=', -1)),
            ],
        depends=_depends + ['product', 'product_uom_category'])
    unit_1_digits = fields.Function(fields.Integer('Unit 1 Digits'),
            'get_unit_x_digits')
    quantity_2 = fields.Float('Qty 2',
        digits=(16, Eval('unit_2_digits', 2)),
        states={
            'readonly': Eval('inventory_state') != 'draft',
            'required': Bool(Eval('uom_2')),
        }, depends=_depends + ['uom_2', 'unit_2_digits'])
    uom_2 = fields.Many2One('product.uom', 'Unit 2',
        states={
            'required': Bool(Eval('quantity_2')),
            'readonly': Eval('inventory_state') != 'draft',
            },
        domain=[
            If(Bool(Eval('product_uom_category')),
                ('category', '=', Eval('product_uom_category')),
                ('category', '=', -1)),
            ],
        depends=_depends + ['quantity_2', 'product_uom_category'])
    unit_2_digits = fields.Function(fields.Integer('Unit 2 Digits'),
            'get_unit_x_digits')

    @classmethod
    def __register__(cls, module_name):
        transaction = Transaction()
        cursor = transaction.connection.cursor()
        sql_table = cls.__table__()

        super(InventoryLine, cls).__register__(module_name)

        select = sql_table.select(
            sql_table.id, sql_table.product,
            sql_table.quantity)
        select.where = (sql_table.quantity_1 == None)

        cursor.execute(*select)
        has_update = False
        for id_, product, quantity in cursor.fetchall():
            uom = cls.get_count_uom(product, default_uom=True)
            cursor.execute(*sql_table.update(
                    [sql_table.quantity_1, sql_table.uom_1],
                    [quantity, uom.id],
                    where=sql_table.id == id_))
            has_update = True

        if has_update:
            cursor.execute(
                'ALTER TABLE "stock_inventory_line" ' \
                'ALTER COLUMN "quantity_1" SET NOT NULL')

    @staticmethod
    def default_unit_1_digits():
        return 2

    @staticmethod
    def default_unit_2_digits():
        return 2

    def get_quantity_show(self, name):
        return self.quantity

    @classmethod
    def create(cls, vlist):
        Uom = Pool().get('product.uom')
        for v in vlist:
            default_uom = cls.get_count_uom(
                v['product'], default_uom=True)
            if 'quantity' not in v:
                v['quantity'] = 0.0
            if 'quantity_1' not in v:
                uom_1 = cls.get_count_uom(v['product'])
                if default_uom.id == uom_1.id:
                    v['quantity_1'] = v['quantity']
                else:
                    v['quantity_1'] = Uom.compute_qty(
                        default_uom,
                        v['quantity'],
                        uom_1)
                v['uom_1'] = uom_1.id
        return super(InventoryLine, cls).create(vlist)

    @fields.depends('product')
    def on_change_with_product_uom_category(self, name=None):
        if self.product:
            return self.product.default_uom_category.id

    @fields.depends('product',
        'quantity_1', 'uom_1',
        'quantity_2', 'uom_2')
    def on_change_quantity_1(self):
        self.set_quantity()

    @fields.depends(methods=['on_change_quantity_1'])
    def on_change_quantity_2(self):
        self.on_change_quantity_1()

    @fields.depends(methods=['on_change_quantity_1'])
    def on_change_uom_1(self):
        self.on_change_quantity_1()

    @fields.depends(methods=['on_change_quantity_1'])
    def on_change_uom_2(self):
        self.on_change_quantity_1()

    @fields.depends('uom')
    def on_change_product(self):
        super(InventoryLine, self).on_change_product()
        self.quantity = None
        self.quantity_show = None
        self.quantity_1 = None
        self.quantity_2 = None
        self.uom_1 = None
        self.uom_2 = None
        self.unit_1_digits = 2
        self.unit_2_digits = 2
        if self.product:
            self.uom_1 = self.get_count_uom(self.product.id)
            self.unit_1_digits = self.uom_1.digits

    @classmethod
    def get_count_uom(cls, product_id, default_uom=False):
        uom = None
        product = Pool().get('product.product')(product_id)
        uom = product.default_uom
        if not default_uom and product.template.count_uom:
            uom = product.template.count_uom
        return uom

    def set_quantity(self):
        Uom = Pool().get('product.uom')
        self.quantity = None
        self.quantity_show = None
        if self.product and self.quantity_1 is not None and self.uom_1:
            self.uom = self.product.default_uom
            self.quantity = Uom.compute_qty(
                self.uom_1,
                self.quantity_1,
                self.uom)
            if self.quantity_2 and self.uom_2:
                self.quantity += Uom.compute_qty(
                    self.uom_2,
                    self.quantity_2,
                    self.uom)
            self.quantity_show = self.quantity
            super(InventoryLine, self).on_change_quantity()

    def get_unit_x_digits(self, name):
        digits = 2
        uom = None
        if name == 'unit_1_digits':
            uom = self.uom_1
        else:
            uom = self.uom_2
        if uom:
            digits = uom.digits
        return digits
