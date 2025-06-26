from odoo import models, fields, api
import logging
from io import BytesIO
from PIL import Image
import base64
import requests
import os
_logger = logging.getLogger(__name__)

class FotosEquitacon(models.Model):
    _name = 'fotos.equitacion'
    _description = 'Fotos de Equitación'
    
    name = fields.Char(string="Nombre")
    ubicacion = fields.Char(string="Enlace de imagen")
    year = fields.Date(string="Año del Evento")
    image_ids = fields.One2many(
        'fotos.equitacion.image.line',
        'equitacion_id',
        string='Imágenes'
    )

    jump_height = fields.Selection([
        ('0.80', '0.80 m'),
        ('0.90', '0.90 m'),                                                                                                                                                                                                                                                                                                                                             
        ('1.00', '1.00 m')
    ], string="Altura del Salto")
    watermark_image = fields.Binary(string="Marca de Agua")
    
    year = fields.Date(string="Año del Evento")
    original_image_url = fields.Char(string="URL de Imagen Original")
    
    

    '''
    Esta funcion realizaría la carga de las imagenes que vienen desde la carpeta, las comprime, y coloca en el sitio web
    
    '''
    def action_subir_desde_carpeta(self):
        for record in self:
            if not record.ubicacion:
                continue

            folder_path = record.ubicacion.rstrip('/')
            try:
                for filename in os.listdir(folder_path):
                    if filename.lower().endswith('.png'):
                        with open(os.path.join(folder_path, filename), 'rb') as f:
                            image_data = f.read()

                        image = Image.open(BytesIO(image_data)).convert("RGB")

                        # Comprimir
                        compressed_buffer = BytesIO()
                        image.save(compressed_buffer, format='JPEG', quality=60)
                        compressed_image = Image.open(BytesIO(compressed_buffer.getvalue()))

                        # Marca de agua
                        if record.watermark_image:
                            watermark = Image.open(BytesIO(base64.b64decode(record.watermark_image))).convert("RGBA")
                            watermark = watermark.resize((int(compressed_image.width * 0.3), int(compressed_image.height * 0.3)))
                            watermark.putalpha(128)
                            position = (compressed_image.width - watermark.width - 10, compressed_image.height - watermark.height - 10)
                            base_rgba = compressed_image.convert("RGBA")
                            base_rgba.paste(watermark, position, watermark)
                            compressed_image = base_rgba.convert("RGB")

                        final_output = BytesIO()
                        compressed_image.save(final_output, format='JPEG', quality=70)
                        image_encoded = base64.b64encode(final_output.getvalue())

                        # Crear el producto
                        self.env['product.template'].create({
                            'name': filename,
                            'image_1920': image_encoded,
                            'website_published': True,
                            'year': record.year,
                            'jump_height': record.jump_height,
                        })
            except Exception as e:
                _logger.error(f"Error al procesar carpeta {record.ubicacion}: {e}")


    def _process_image_from_url(self, url, watermark_image=False):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                _logger.warning(f"No se pudo descargar la imagen desde {url}")
                return False

            image = Image.open(BytesIO(response.content)).convert("RGB")

            # Comprimir
            compressed_buffer = BytesIO()
            image.save(compressed_buffer, format='JPEG', quality=60)
            compressed_image = Image.open(BytesIO(compressed_buffer.getvalue()))

            # Marca de agua
            if watermark_image:
                watermark = Image.open(BytesIO(base64.b64decode(watermark_image))).convert("RGBA")
                watermark = watermark.resize((int(compressed_image.width * 0.3), int(compressed_image.height * 0.3)))
                watermark.putalpha(128)
                position = (compressed_image.width - watermark.width - 10, compressed_image.height - watermark.height - 10)
                base_rgba = compressed_image.convert("RGBA")
                base_rgba.paste(watermark, position, watermark)
                compressed_image = base_rgba.convert("RGB")

            output = BytesIO()
            compressed_image.save(output, format='JPEG', quality=70)
            return base64.b64encode(output.getvalue())

        except Exception as e:
            _logger.error(f"Error procesando imagen desde URL: {e}")
            return False

    def action_enviar_fotos_como_productos(self):
        for record in self:
            for image_line in record.image_ids:
                try:
                    if not image_line.image_file:
                        continue

                    image = Image.open(BytesIO(base64.b64decode(image_line.image_file))).convert("RGB")

                    # Comprimir
                    compressed_buffer = BytesIO()
                    image.save(compressed_buffer, format='JPEG', quality=60)
                    compressed_image = Image.open(BytesIO(compressed_buffer.getvalue()))

                    # Marca de agua (si existe)
                    if record.watermark_image:
                        watermark = Image.open(BytesIO(base64.b64decode(record.watermark_image))).convert("RGBA")
                        watermark = watermark.resize(
                            (int(compressed_image.width * 0.3), int(compressed_image.height * 0.3))
                        )
                        watermark.putalpha(128)
                        position = (
                            compressed_image.width - watermark.width - 10,
                            compressed_image.height - watermark.height - 10
                        )
                        base_rgba = compressed_image.convert("RGBA")
                        base_rgba.paste(watermark, position, watermark)
                        compressed_image = base_rgba.convert("RGB")

                    final_output = BytesIO()
                    compressed_image.save(final_output, format='JPEG', quality=70)
                    image_encoded = base64.b64encode(final_output.getvalue())

                    # Crear producto publicado
                    self.env['product.template'].create({
                        'name': image_line.filename or record.name or 'Foto de Equitación',
                        'image_1920': image_encoded,
                        'website_published': True,
                        'year': record.year,
                        'jump_height': record.jump_height,
                    })

                except Exception as e:
                    _logger.error(f"Error procesando imagen '{image_line.filename}': {e}")
    
