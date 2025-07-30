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
    
  
    
    # @http.route('/photographer/info', type='http', auth='public', website=True)
    # def photographer_info(self):
    #     user = request.env.user

    #     # Crear la oportunidad si el usuario está autenticado (o adaptarla a 'public' si es necesario)
    #     if user and user.id != request.env.ref('base.public_user').id:
    #         lead_vals = {
    #             'name': f'Consulta Fotógrafo - {user.name}',
    #             'partner_id': user.partner_id.id,
    #             'email_from': user.partner_id.email,
    #             'phone': user.partner_id.phone,
    #             'description': 'El usuario ha visitado la sección de información del fotógrafo.',
    #         }
    #         request.env['crm.lead'].sudo().create(lead_vals)

    #     values = {
    #         'name': 'Juan Pérez',
    #         'bank': 'N° de Cuenta Banco Santader: XXXX-XXXX',
    #         'alias': 'abrojo.enjambre.playa',
    #         'tel': 'Whatsapp: 351 8967896 ',
    #         'shop_url': '/shop',
    #     }
    #     return request.render('crm_with_image.photographer_info_template', values)



    @http.route('/photographer/info', auth='user', website=True)
    def photographer_info(self):
        partner = request.env.user.partner_id

        # if not partner or not partner.is_photographer:
        #     return request.render("crm_with_image.photographer_not_found_template")

        return request.render("crm_with_image.photographer_info_template", {
            'name': partner.name,
            'email': partner.email,
            'tel': partner.phone,
            'instagram': partner.instagram_account,
            'bank': partner.bank_account_info,
            'alias': partner.bank_alias,
            'cbu_cvu': partner.bank_cbu_cvu,
            'shop_url': '/shop',
        })

    @http.route('/photographer/save', type='http', auth='user', methods=['POST'], csrf=False, website=True)
    def photographer_save(self, **post):
        partner = request.env.user.partner_id

        # Solo si es fotógrafo
        #if partner and partner.is_photographer:
        partner.name = post.get('name')
        partner.email = post.get('email')
        partner.phone = post.get('tel')
        partner.instagram_account = post.get('instagram')
        partner.bank_account_info = post.get('bank')
        partner.bank_alias = post.get('alias')
        partner.bank_cbu_cvu = post.get('cbu_cvu')

        return request.redirect('/photographer/info')