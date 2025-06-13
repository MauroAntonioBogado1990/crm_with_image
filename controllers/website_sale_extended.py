import logging
from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)

class WebsiteSaleExtended(http.Controller):
    @http.route(['/shop/contact_photographer'], type='json', auth="public", methods=['POST'], csrf=False)
    def create_lead_for_photographer(self, product_id, **kwargs):
        _logger.info("📸 Se ha llamado al endpoint /shop/contact_photographer")
        
        user = request.env.user
        customer = request.env['res.partner'].search([('id', '=', user.partner_id.id)], limit=1)
        product = request.env['product.product'].search([('id', '=', int(product_id))], limit=1)
        admin = request.env['res.users'].browse(1)  # Admin por defecto (ID 1)

        if not customer or not product:
            _logger.warning("⚠️ No se pudo registrar la oportunidad. Cliente o producto no encontrados.")
            return {'error': _("No se pudo registrar la oportunidad. Verifica los datos.")}

        # Obtener datos del administrador
        admin_phone = admin.partner_id.phone or _("No disponible")

        # Crear oportunidad en CRM
        crm_lead = request.env['crm.lead'].sudo().create({
            'name': f"Solicitud Fotografía - {customer.name}",
            'partner_id': customer.id,
            'contact_name': customer.name,
            'phone': customer.phone,
            'email_from': customer.email,
            'description': f"Interés en fotografía del producto: {product.name}",
            'user_id': admin.id,
        })

        _logger.info(f"✅ Oportunidad creada con ID: {crm_lead.id}")

        return {
            'message': _("Gracias por tu interés. Hemos enviado la solicitud al fotógrafo."),
            'admin_phone': admin_phone,
            'crm_lead_id': crm_lead.id
        }