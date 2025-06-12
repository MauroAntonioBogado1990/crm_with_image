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

    def _process_image(self, original_image, watermark_image=False):
        """ Reduce el tamaño y peso de la imagen, aplica marca de agua si existe. """
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
                position = (compressed_image.width - watermark.width - 10, compressed_image.height - watermark.height - 10)

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
        """ Al crear el producto, optimiza la imagen si está definida. """
        if 'image_1920' in vals:
            vals['optimized_image'] = self._process_image(vals['image_1920'], vals.get('watermark_image'))
            vals['image_1920'] = vals['optimized_image']  # Reemplazar imagen original
        return super(ProductTemplateWithOptimizedImage, self).create(vals)

    def write(self, vals):
        """ Al actualizar el producto, optimiza la imagen si cambia. """
        if 'image_1920' in vals:
            vals['optimized_image'] = self._process_image(vals['image_1920'], vals.get('watermark_image'))
            vals['image_1920'] = vals['optimized_image']  # Reemplazar imagen original
        return super(ProductTemplateWithOptimizedImage, self).write(vals)