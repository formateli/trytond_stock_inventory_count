# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import unittest
#import doctest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
#from trytond.tests.test_tryton import doctest_teardown
#from trytond.tests.test_tryton import doctest_checker


class InventoryCountTestCase(ModuleTestCase):
    'Test Stock Inventory Count'
    module = 'stock_inventory_count'

    @with_transaction()
    def test_stock_inventory_count(self):
        pool = Pool()
        Product = pool.get('product.product')
        Inventory = pool.get('stock.inventory')
        Line = pool.get('stock.inventory.line')


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        InventoryCountTestCase))
    return suite

#def suite():
#    suite = trytond.tests.test_tryton.suite()
#    suite.addTests(doctest.DocFileSuite(
#        'scenario_stock_inventory.rst',
#        tearDown=doctest_teardown, encoding='utf-8',
#        checker=doctest_checker,
#        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
#    )
#    return suite
