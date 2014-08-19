from osv import fields,osv

class report_wizard_webkit(osv.TransientModel):
    _name='autorepair.wizard_report_repairs_webkit'
    _columns={
              'date_from': fields.date(string="Start Date",required=True),
              'date_to': fields.date(string="End Date",required=True),
              'client_ids':fields.many2many('res.partner',required=True,domain="[('customer','=',True)]",string="Client"),
              }
    
    def pre_print_report_webkit(self, cr, uid, ids, data, context=None):       
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from','date_to','client_ids'], context=context)[0]
        for field in ['client_ids']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]         
        return data

    
    def _print_report_webkit(self, cr, uid, ids, data, context={}):
        data = self.pre_print_report_webkit(cr, uid, ids, data, context=context)
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'test_1',
            'datas': data
            }

    def action_go_report(self, cr, uid, ids, context={}):        
            data={}
            report=self.read(cr,uid,ids,['report_type'],context=context)[0]
            return self._print_report_webkit(cr, uid, ids, data, context=context)
           
            
    
 