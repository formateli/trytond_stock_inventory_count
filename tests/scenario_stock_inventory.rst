========================
Inventory Count Scenario
========================

Imports::

    >>> import datetime
    >>> from decimal import Decimal
    >>> from proteus import Model
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> today = datetime.date.today()

Install stock Module::

    >>> config = activate_modules('stock_inventory_count')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Get stock locations::

    >>> Location = Model.get('stock.location')
    >>> supplier_loc, = Location.find([('code', '=', 'SUP')])
    >>> storage_loc, = Location.find([('code', '=', 'STO')])
    >>> customer_loc, = Location.find([('code', '=', 'CUS')])

Uom's::
    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> kg, = ProductUom.find([('name', '=', 'Kilogram')])
    >>> unit_12 = ProductUom()
    >>> unit_12.name = '12u Pack'
    >>> unit_12.symbol = '12u'
    >>> unit_12.category = unit.category
    >>> unit_12.factor = 12.0
    >>> unit_12.rate = round(1.0 / 12.0, 12)
    >>> unit_12.rounding = 1.0
    >>> unit_12.digits = 0
    >>> unit_12.save()

Create products::

    >>> ProductTemplate = Model.get('product.template')
    >>> template = ProductTemplate()
    >>> template.name = 'Product'
    >>> template.default_uom = unit
    >>> template.count_uom = unit_12
    >>> template.type = 'goods'
    >>> template.list_price = Decimal('300')
    >>> template.cost_price = Decimal('80')
    >>> template.cost_price_method = 'average'
    >>> template.save()
    >>> product, = template.products

    >>> template2 = ProductTemplate()
    >>> template2.name = 'Product'
    >>> template2.default_uom = kg
    >>> template2.type = 'goods'
    >>> template2.list_price = Decimal('140')
    >>> template2.cost_price = Decimal('60')
    >>> template2.cost_price_method = 'average'
    >>> template2.save()
    >>> product2, = template2.products

Fill storage::

    >>> StockMove = Model.get('stock.move')
    >>> incoming_move = StockMove()
    >>> incoming_move.product = product
    >>> incoming_move.uom = unit
    >>> incoming_move.quantity = 24
    >>> incoming_move.from_location = supplier_loc
    >>> incoming_move.to_location = storage_loc
    >>> incoming_move.planned_date = today
    >>> incoming_move.effective_date = today
    >>> incoming_move.company = company
    >>> incoming_move.unit_price = Decimal('100')
    >>> incoming_move.currency = company.currency
    >>> incoming_moves = [incoming_move]

    >>> incoming_move = StockMove()
    >>> incoming_move.product = product2
    >>> incoming_move.uom = kg
    >>> incoming_move.quantity = 2.5
    >>> incoming_move.from_location = supplier_loc
    >>> incoming_move.to_location = storage_loc
    >>> incoming_move.planned_date = today
    >>> incoming_move.effective_date = today
    >>> incoming_move.company = company
    >>> incoming_move.unit_price = Decimal('70')
    >>> incoming_move.currency = company.currency
    >>> incoming_moves.append(incoming_move)
    >>> StockMove.click(incoming_moves, 'do')

Create an inventory::

    >>> Inventory = Model.get('stock.inventory')
    >>> inventory = Inventory()
    >>> inventory.location = storage_loc
    >>> inventory.save()
    >>> inventory.click('complete_lines')
    >>> line_by_product = {l.product.id: l for l in inventory.lines}
    >>> line_p1 = line_by_product[product.id]
    >>> line_p1.expected_quantity
    24.0
    >>> line_p1.diff_quantity
    0.0
    >>> line_p1.quantity_1
    2.0
    >>> line_p1.uom_1.symbol
    u'12u'
    >>> line_p1.quantity_1 = 6
    >>> line_p1.quantity
    72.0
    >>> line_p1.diff_quantity
    48.0
    >>> line_p1.uom_1 = unit
    >>> line_p1.quantity
    6.0
    >>> line_p1.quantity_1
    6.0
    >>> line_p1.diff_quantity
    -18.0
    >>> line_p1.uom_1 = unit_12
    >>> line_p1.quantity
    72.0
    >>> line_p1.quantity_1
    6.0
    >>> line_p1.diff_quantity
    48.0

    >>> line_p2 = line_by_product[product2.id]
    >>> line_p2.expected_quantity
    2.5
    >>> line_p2.quantity
    2.5
    >>> line_p2.diff_quantity
    0.0
    >>> inventory.save()

Fill storage with more quantities::

    >>> incoming_move = StockMove()
    >>> incoming_move.product = product
    >>> incoming_move.uom = unit
    >>> incoming_move.quantity = 60
    >>> incoming_move.from_location = supplier_loc
    >>> incoming_move.to_location = storage_loc
    >>> incoming_move.planned_date = today
    >>> incoming_move.effective_date = today
    >>> incoming_move.company = company
    >>> incoming_move.unit_price = Decimal('100')
    >>> incoming_move.currency = company.currency
    >>> incoming_moves = [incoming_move]

    >>> incoming_move = StockMove()
    >>> incoming_move.product = product2
    >>> incoming_move.uom = kg
    >>> incoming_move.quantity = 1.3
    >>> incoming_move.from_location = supplier_loc
    >>> incoming_move.to_location = storage_loc
    >>> incoming_move.planned_date = today
    >>> incoming_move.effective_date = today
    >>> incoming_move.company = company
    >>> incoming_move.unit_price = Decimal('70')
    >>> incoming_move.currency = company.currency
    >>> incoming_moves.append(incoming_move)
    >>> StockMove.click(incoming_moves, 'do')

Update the inventory::

    >>> inventory.click('complete_lines')
    >>> line_p1.reload()
    >>> line_p1.quantity
    72.0
    >>> line_p1.quantity_1
    6.0
    >>> line_p1.expected_quantity
    84.0
    >>> line_p1.diff_quantity
    -12.0
    >>> line_p2.reload()
    >>> line_p2.expected_quantity
    3.8
    >>> line_p2.quantity
    3.8

Set quantity_2::

    >>> line_p1.uom_2 = unit
    >>> line_p1.quantity
    72.0
    >>> line_p1.quantity_2 = 10.0
    >>> line_p1.quantity
    82.0
    >>> line_p1.uom_2 = None
    >>> line_p1.quantity
    72.0
    >>> line_p1.uom_2 = unit
    >>> line_p1.quantity
    82.0
    >>> line_p1.save()

More moves::

    >>> incoming_move = StockMove()
    >>> incoming_move.product = product
    >>> incoming_move.uom = unit
    >>> incoming_move.quantity = 12
    >>> incoming_move.from_location = supplier_loc
    >>> incoming_move.to_location = storage_loc
    >>> incoming_move.planned_date = today
    >>> incoming_move.effective_date = today
    >>> incoming_move.company = company
    >>> incoming_move.unit_price = Decimal('100')
    >>> incoming_move.currency = company.currency
    >>> incoming_moves = [incoming_move]
    >>> StockMove.click(incoming_moves, 'do')

Update the inventory::

    >>> inventory.click('complete_lines')
    >>> line_p1.reload()
    >>> line_p1.expected_quantity
    96.0
    >>> line_p1.quantity_1
    6.0
    >>> line_p1.quantity_2
    10.0
    >>> line_p1.quantity
    82.0
    >>> line_p1.diff_quantity
    -14.0
