# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pyson import Eval, Equal, Not
from trytond.pool import PoolMeta
from trytond.model import fields

__all__ = ['Template',]


class Template(metaclass=PoolMeta):
    __name__ = "product.template"
    count_uom = fields.Many2One('product.uom', 'Count UOM', states={
            'readonly': ~Eval('active'),
            'invisible': Not(Equal(Eval('type'), 'goods')),
            },
        domain=[('category', '=', Eval('default_uom_category'))],
        depends=['active', 'default_uom_category'])

    @classmethod
    def view_attributes(cls):
        return super(Template, cls).view_attributes() + [
            ('//page[@id="counting"]', 'states', {
                    'invisible': Not(Equal(Eval('type'), 'goods')),
                    })]
