
from openerp.osv import fields, osv, orm

class wizard_report_repairs_aeroo(osv.TransientModel):
    _name='autorepair.wizard_report_repairs_aeroo'
    
    def out_format_get (self, cr, uid, context={}):
        obj = self.pool.get('report.mimetypes')
        ids = []
        list = []
         
        ids = obj.search(cr, uid, ['|', '|',('code','=','oo-xls'), ('code','=','oo-ods'),('code','=','oo-pdf')])
        #only include format pdf that match with ods format.
        for type in obj.browse(cr, uid, ids, context=context):
            if type.code == 'oo-pdf' and type.compatible_types == 'oo-odt':
                list.append(type.id)
            elif type.code == 'oo-xls' or type.code == 'oo-ods':
                list.append(type.id)
 
        # If read method isn't call, the value for out_format "disappear",
        # the value is preserved, but disappears from the screen (a rare bug)
        res = obj.read(cr, uid, list, ['name'], context)
        return [(str(r['id']), r['name']) for r in res] 
    
    _columns={
              'date_from': fields.date(string="Start Date",required=True),
              'date_to': fields.date(string="End Date",required=True),
              'partner_ids':fields.many2many('res.partner',required=True,domain="[('customer','=',True)]",string="Client"),
              'out_format': fields.selection(out_format_get, 'Print Format',required=True),
              }
    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        
        result['date_from'] = 'date_from' in data['form'] and data['form']['date_from'] or False
        result['date_to'] = 'date_to' in data['form'] and data['form']['date_to'] or False
    
        #m2m, m2o fields
        result['partner_ids'] = 'partner_ids' in data['form'] and data['form']['partner_ids'] or False

        return result
    
    def _print_report(self, cr, uid, ids, data, context=None):
        mimetype = self.pool.get('report.mimetypes')
        report_obj = self.pool.get('ir.actions.report.xml')
        report_name = ''
      
        context = context or {}
            
        #=======================================================================
        # onchange_in_format method changes variable out_format depending of 
        # which in_format is choose. 
        # If out_format is pdf -> call record in odt format 
        #
        # If mimetype is PDF -> out_format = PDF (search odt record)
        # If record doesn't exist, return a error.
        #=======================================================================
                
        #1. Find out_format selected
        out_format_obj = mimetype.browse(cr, uid, [int(data['form']['out_format'])], context)[0]

        #2. Check out_format and set report_name for each format
        if out_format_obj.code == 'oo-pdf':
            report_name = 'repairs_odt' 
           
        elif out_format_obj.code == 'oo-xls' or out_format_obj.code == 'oo-ods': 
            report_name = 'repairs_ods'
        
        # If there not exist name, it's because not exist a record for this format   
        if report_name == '':
            raise osv.except_osv(_('Error !'), _('There is no template defined for the selected format. Check if aeroo report exist.'))
                
        else:
            #Search record that match with the name, and get some extra information
            report_xml_id = report_obj.search(cr, uid, [('report_name','=', report_name)],context=context)
            report_xml = report_obj.browse(cr, uid, report_xml_id, context=context)[0]
            data.update({'model': report_xml.model, 'report_type':'aeroo', 'id': report_xml.id})
            
            #Write out_format choose in wizard
            report_xml.write({'out_format': out_format_obj.id}, context=context)
           
            return {
                'type': 'ir.actions.report.xml',
                'report_name': report_name,
                'datas': data,
                'context':context
            }
            
    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        data = {}
        data['form'] = self.read(cr, uid, ids, ['date_from','date_to','partner_ids','out_format'], context=context)[0]
        #Extract ids for m2o and m2m fields
        for field in ['partner_ids']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        
        #Check if the fields exist, otherwise put false in the field.
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['used_context'] = used_context
        
        return self._print_report(cr, uid, ids, data, context=context)
    
        