# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import unittest
#import doctest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.modules.company.tests import create_company, set_company
import datetime
from decimal import Decimal
#from trytond.tests.test_tryton import doctest_teardown
#from trytond.tests.test_tryton import doctest_checker


class InventoryCountTestCase(ModuleTestCase):
    'Test Stock Inventory Count'
    module = 'stock_inventory_count'

    @with_transaction()
    def test_stock_inventory_count(self):
        pool = Pool()
        Inventory = pool.get('stock.inventory')
        Line = pool.get('stock.inventory.line')
        Location = pool.get('stock.location')

        today = datetime.date.today()

        company = create_company()
        with set_company(company):
            supplier_loc, = Location.search([('code', '=', 'SUP')])
            storage_loc, = Location.search([('code', '=', 'STO')])
            customer_loc, = Location.search([('code', '=', 'CUS')])

            unit, unit_12, kg, product, product2 = self._create_products()

            # Fill stock
            self._create_stock_move(company, today, product, unit, 24,
                Decimal('100.0'), supplier_loc, storage_loc)
            self._create_stock_move(company, today, product2, kg, 2.5,
                Decimal('70.0'), supplier_loc, storage_loc)

            # Create Inventory
            inventory = Inventory(
                location=storage_loc,
            )
            inventory.save()

            Inventory.complete_lines([inventory])
            line_by_product = {l.product.id: l for l in inventory.lines}

            line_p1 = line_by_product[product.id]
            line_p1.on_change_product()
            line_p1.on_change_quantity_1()
            self.assertEqual(24.0, line_p1.expected_quantity)
            self.assertEqual(-24.0, line_p1.diff_quantity)
            self.assertEqual(None, line_p1.quantity)
            self.assertEqual(None, line_p1.quantity_1)
            self.assertEqual('12u', line_p1.uom_1.symbol)

            line_p1.quantity_1 = 6
            line_p1.on_change_quantity_1()
            self.assertEqual(72.0, line_p1.quantity)
            self.assertEqual(48.0, line_p1.diff_quantity)

            line_p1.uom_1 = unit
            line_p1.on_change_uom_1()
            self.assertEqual(6.0, line_p1.quantity)
            self.assertEqual(-18.0, line_p1.diff_quantity)

            line_p1.uom_1 = unit_12
            line_p1.on_change_uom_1()
            self.assertEqual(72.0, line_p1.quantity)
            self.assertEqual(48.0, line_p1.diff_quantity)

            inventory.save()

            # More stock moves
            self._create_stock_move(company, today, product, unit, 60,
                Decimal('100.0'), supplier_loc, storage_loc)
            self._create_stock_move(company, today, product2, kg, 1.3,
                Decimal('70.0'), supplier_loc, storage_loc)

            # Update Inventory
            Inventory.complete_lines([inventory])

            line_p1.on_change_quantity_1()
            self.assertEqual(72.0, line_p1.quantity)
            self.assertEqual(6.0, line_p1.quantity_1)
            self.assertEqual(84.0, line_p1.expected_quantity)
            self.assertEqual(-12.0, line_p1.diff_quantity)

    def _create_stock_move(self, company, today, product, unit, quantity,
                unit_price, from_location, to_location):
        pool = Pool()
        StockMove = pool.get('stock.move')

        move = StockMove(
            product=product,
            uom=unit,
            quantity=quantity,
            from_location=from_location,
            to_location=to_location,
            planned_date=today,
            effective_date=today,
            company=company,
            unit_price=unit_price,
            currency=company.currency,
        )
        move.save()
        StockMove.do([move])

    def _create_products(self):
        pool = Pool()
        ProductUom = pool.get('product.uom')

        unit, = ProductUom.search([('name', '=', 'Unit')])
        kg, = ProductUom.search([('name', '=', 'Kilogram')])
        unit_12 = ProductUom(
            name='12u Pack',
            symbol='12u',
            category=unit.category,
            factor=12.0,
            rate=round(1.0 / 12.0, 12),
            rounding=1.0,
            digits=0,
        )
        unit_12.save()

        product = self._create_product(
            'Product', unit, unit_12)

        product2 = self._create_product(
            'Product 2', kg, None)

        return unit, unit_12, kg, product, product2

    @classmethod
    def _create_product(self, name, uom, uom_count):
        pool = Pool()
        Template = pool.get('product.template')
        Product = pool.get('product.product')

        template=Template(
            name=name,
            default_uom=uom,
            type='goods',
            count_uom = uom_count,
            list_price=Decimal('0.0'),
            cost_price=Decimal('0.0'),
            cost_price_method='average')
        template.save()

        product = Product(
            template=template
        )
        product.save()
        return product

def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        InventoryCountTestCase))
    return suite
