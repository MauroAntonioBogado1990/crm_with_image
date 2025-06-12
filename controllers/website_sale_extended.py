from odoo import http, _
from odoo.http import request

class WebsiteSaleExtended(http.Controller):
    @http.route(['/shop/cart/add'], type='json', auth="public", methods=['POST'])
    def add_to_crm_instead_of_cart(self, product_id, **kwargs):
        user = request.env.user
        customer = request.env['res.partner'].search([('id', '=', user.partner_id.id)], limit=1)
        product = request.env['product.product'].search([('id', '=', int(product_id))], limit=1)

        if not customer or not product:
            return {'error': _("No se pudo registrar la oportunidad. Verifica los datos.")}

        # Obtener datos del administrador
        admin = request.env.ref('base.user_admin')
        admin_phone = admin.partner_id.phone or "No disponible"
        admin_alias = admin.partner_id.x_account_number or "No disponible"

        # Crear oportunidad en CRM
        crm_lead = request.env['crm.lead'].sudo().create({
            'name': f"Oportunidad - {customer.name}",
            'partner_id': customer.id,
            'user_id': admin.id,
            'description': f"Compra potencial: {product.name}",
        })

        # Retornar datos para mostrarlos en la ventana emergente
        return {
            'message': _("Gracias por tu interés. Aquí están los datos del administrador:"),
            'user_name': customer.name,
            'phone': admin_phone,
            'alias': admin_alias,
            'crm_lead_id': crm_lead.id
        }