from odoo import models, fields, api
import logging
from io import BytesIO
from PIL import Image
import base64
import requests
_logger = logging.getLogger(__name__)

class FotosEquitacon(models.Model):
    _name = 'fotos.equitacion'
    _description = 'Fotos de Equitación'
    
    name = fields.Char(string="Nombre")
    link_folder = fields.Char(string="Enlace de imagen")
    year = fields.Date(string="Año del Evento")
    jump_height = fields.Selection([
        ('0.80', '0.80 m'),
        ('0.90', '0.90 m'),                                                                                                                                                                                                                                                                                                                                             
        ('1.00', '1.00 m')
    ], string="Altura del Salto")
    watermark_image = fields.Binary(string="Marca de Agua")
    #image_filenames = fields.Text(string="Nombres de imágenes (separados por coma)")
    year = fields.Date(string="Año del Evento")
    original_image_url = fields.Char(string="URL de Imagen Original")
    
    

    def _get_image_urls(self):
        if not self.link_folder or not self.image_filenames:
            return []
        base = self.link_folder.rstrip('/')
        names = [name.strip() for name in self.image_filenames.split(',')]  
        return [f"{base}/{name}" for name in names]

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
            urls = record._get_image_urls()
            for url in urls:
                processed = record._process_image_from_url(url, record.watermark_image)
                if processed:
                    self.env['product.template'].create({
                        'name': record.name or 'Foto de Equitación',
                        'image_1920': processed,
                        'website_published': True,
                        'link_folder': url,
                        'original_image_url': url,  # ← Aquí se guarda el enlace original
                        'year': record.year,
                        'jump_height': record.jump_height,
                    })
    


class ImagenEquitacionSeleccion(models.Model):
    _name = 'fotos.equitacion.imagen'
    _description = 'Imagen descargada para revisión'

    foto_id = fields.Many2one('fotos.equitacion', string="Evento")
    image_url = fields.Char("URL de Imagen")
    image_preview = fields.Binary("Previsualización")
    selected = fields.Boolean("Seleccionada para publicar")

    def action_descargar_imagenes(self):
        for record in self:
            urls = record._get_image_urls()
            for url in urls:
                image_data = record._process_image_from_url(url, watermark_image=False)
                if image_data:
                    self.env['fotos.equitacion.imagen'].create({
                        'foto_id': record.id,
                        'image_url': url,
                        'image_preview': image_data,
                    })


                                                                         