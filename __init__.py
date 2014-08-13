import autorepair


class part(osv.Model):
    _name='autorepair.part'

    _columns={
              'reference': fields.char(string="Part Number",size=20,required=True),
              'description':fields.text(string="Description",required=True),
              'price':fields.float(string="Price Unit",required=True,digits=(10,2)),
              'stock':fields.integer(string="Stock Level",required=True)
                        }
    _defaults={
        'price':0,
        'stock':1,
        }

    def _check_price_no_negative(self, cr, uid, ids, context={}):
        for part in self.browse(cr, uid, ids, context=context):
            if part.price<0:
                return False
        return True
    def _check_stock_no_negative(self, cr, uid, ids, context={}):
        for part in self.browse(cr, uid, ids, context=context):
            if part.qualify<0:
                return False
        return True

    _constraints = [
        (_check_price_no_negative,'Negatives prices not allowed',['price']
         ),
        (_check_stock_no_negative,'Negatives stock levels not allowed',['stock']
         )      
    ]
    
    _sql_constraints = [
        ('reference_part_unique',
        'UNIQUE(reference)',
        'The part number already exist ')
     ]
    _order="reference,description"