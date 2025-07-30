from odoo import models, fields, api
import logging
from io import BytesIO
from PIL import Image
import base64

_logger = logging.getLogger(__name__)

class ProductTemplateWithOptimizedImage(models.Model):
    _inherit = 'product.template'

    watermark_image = fields.Binary(string="Marca de Agua")
    optimized_image = fields.Binary(string="Imagen Optimizada")
    year = fields.Date(string="Año del Evento")
    jump_height = fields.Selection([('0.80', '0.80 m'), ('0.90', '0.90 m'), ('1.00', '1.00 m')],string="Altura del Salto")
    #campo bono
    #bono = fields.Boolean(String="Bono")
    #se agregae esta campo para poder asociar con las lineas de las fotos
    equitacion_id = fields.Many2one('fotos.equitacion', string='Foto de Equitación', ondelete='cascade')

    def _process_image(self, original_image, watermark_image=False):
        """ Reduce el tamaño y peso de la imagen, aplica una marca de agua con transparencia. """
        if not original_image:
            return False

        try:
            # Convertir imagen original a RGB
            image = Image.open(BytesIO(base64.b64decode(original_image))).convert("RGB")

            # Reducción de tamaño y compresión JPEG
            compressed_buffer = BytesIO()
            image.save(compressed_buffer, format='JPEG', quality=60)
            compressed_image = Image.open(BytesIO(compressed_buffer.getvalue()))

            # Aplicar marca de agua si está definida
            if watermark_image:
                watermark = Image.open(BytesIO(base64.b64decode(watermark_image))).convert("RGBA")
                watermark = watermark.resize((int(compressed_image.width * 0.3), int(compressed_image.height * 0.3)))

                # Ajustar transparencia (0 = completamente invisible, 255 = opaco)
                watermark.putalpha(128)  # Ajusta el nivel de opacidad según lo que necesites

                position = (compressed_image.width - watermark.width - 10, compressed_image.height - watermark.height - 10)

                # Aplicar marca de agua con transparencia
                base_rgba = compressed_image.convert("RGBA")
                base_rgba.paste(watermark, position, watermark)
                compressed_image = base_rgba.convert("RGB")

            # Guardar imagen final
            output = BytesIO()
            compressed_image.save(output, format='JPEG', quality=70)
            return base64.b64encode(output.getvalue())

        except Exception as e:
            _logger.error(f"Error al procesar imagen: {e}")
            return False

    @api.model
    def create(self, vals):
        if 'image_1920' in vals:
            vals['optimized_image'] = self._process_image(vals['image_1920'], vals.get('watermark_image'))
            vals['image_1920'] = vals['optimized_image']  # Reemplazar imagen original
        return super(ProductTemplateWithOptimizedImage, self).create(vals)

    def write(self, vals):
        if 'image_1920' in vals:
            vals['optimized_image'] = self._process_image(vals['image_1920'], vals.get('watermark_image'))
            vals['image_1920'] = vals['optimized_image']  # Reemplazar imagen original
        return super(ProductTemplateWithOptimizedImage, self).write(vals)
    
    

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().website_sale_main_button()

        for order in self:
            if order.website_id:  # Solo si proviene del eCommerce
                _logger.warning('=== CREANDO OPORTUNIDAD DESDE ECOMMERCE ===')
                _logger.warning('Pedido: %s | Cliente: %s', order.name, order.partner_id.name)

                opportunity = order.env['crm.lead'].create({
                    'name': f'Oportunidad desde tienda - {order.name}',
                    'partner_id': order.partner_id.id,
                    'user_id': order.user_id.id,
                    'type': 'opportunity',
                    'team_id': order.team_id.id,
                    'description': f'Pedido generado desde ecommerce. Total: {order.amount_total}',
                })

                _logger.warning('Oportunidad creada: %s', opportunity.id)

        return res