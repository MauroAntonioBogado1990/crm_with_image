from odoo import models, fields, api
import logging
from io import BytesIO
from PIL import Image
import base64
import requests
import os
import re
import unicodedata
#from odoo.http import slug

def slug(text):
    """
    Convierte un texto en un slug URL-friendly (solo letras minúsculas, números, guiones).
    """
    if not text:
        return 'evento'
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

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
    
    
    # def slug(text):
    #     """
    #     Convierte un texto en un slug URL-friendly (solo letras minúsculas, números, guiones).
    #     """
    #     if not text:
    #         return 'evento'
    #     text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    #     text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    #     return re.sub(r'[-\s]+', '-', text)


    
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

    # def action_enviar_fotos_como_productos(self):
    #     for record in self:
    #         for image_line in record.image_ids:
    #             try:
    #                 if not image_line.image_file:
    #                     continue

    #                 image = Image.open(BytesIO(base64.b64decode(image_line.image_file))).convert("RGB")

    #                 # Comprimir
    #                 compressed_buffer = BytesIO()
    #                 image.save(compressed_buffer, format='JPEG', quality=60)
    #                 compressed_image = Image.open(BytesIO(compressed_buffer.getvalue()))

    #                 # Marca de agua (si existe)
    #                 if record.watermark_image:
    #                     watermark = Image.open(BytesIO(base64.b64decode(record.watermark_image))).convert("RGBA")
    #                     watermark = watermark.resize(
    #                         (int(compressed_image.width * 0.3), int(compressed_image.height * 0.3))
    #                     )
    #                     watermark.putalpha(128)
    #                     position = (
    #                         compressed_image.width - watermark.width - 10,
    #                         compressed_image.height - watermark.height - 10
    #                     )
    #                     base_rgba = compressed_image.convert("RGBA")
    #                     base_rgba.paste(watermark, position, watermark)
    #                     compressed_image = base_rgba.convert("RGB")

    #                 final_output = BytesIO()
    #                 compressed_image.save(final_output, format='JPEG', quality=70)
    #                 image_encoded = base64.b64encode(final_output.getvalue())

    #                 # Crear producto publicado
    #                 self.env['product.template'].create({
    #                     'name': image_line.filename or record.name or 'Foto de Equitación',
    #                     'image_1920': image_encoded,
    #                     'website_published': True,
    #                     'year': record.year,
    #                     'jump_height': record.jump_height,
    #                 })

    #             except Exception as e:
    #                 _logger.error(f"Error procesando imagen '{image_line.filename}': {e}")



    def action_enviar_fotos_como_productos(self):
        for record in self:
            # Armar nombre de la categoría
            categoria_nombre = f"{record.name or 'Evento'} - {record.year.strftime('%Y') if record.year else 'Sin Año'}"

            # Buscar o crear categoría
            categoria = self.env['product.public.category'].search([('name', '=', categoria_nombre)], limit=1)
            if not categoria:
                categoria = self.env['product.public.category'].create({'name': categoria_nombre})

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

                    # Crear producto publicado asociado a la categoría
                    self.env['product.template'].create({
                        'name': image_line.filename or record.name or 'Foto de Equitación',
                        'image_1920': image_encoded,
                        'website_published': True,
                        'year': record.year,
                        'jump_height': record.jump_height,
                        'public_categ_ids': [(6, 0, [categoria.id])],
                    })

                except Exception as e:
                    _logger.error(f"Error procesando imagen '{image_line.filename}': {e}")
    
    #Con esta función se crea las páginas que contienen las fotos
    # def action_enviar_fotos_como_productos(self):
    #     for record in self:
    #         html_content = f"<h1>{record.name or 'Evento de Equitación'}</h1>"
    #         if record.year:
    #             html_content += f"<h3>{record.year.strftime('%Y')}</h3>"
    #         html_content += "<div style='display: flex; flex-wrap: wrap;'>"

    #         for image_line in record.image_ids:
    #             try:
    #                 if not image_line.image_file:
    #                     continue

    #                 image = Image.open(BytesIO(base64.b64decode(image_line.image_file))).convert("RGB")

    #                 # Comprimir
    #                 compressed_buffer = BytesIO()
    #                 image.save(compressed_buffer, format='JPEG', quality=60)
    #                 compressed_image = Image.open(BytesIO(compressed_buffer.getvalue()))

    #                 # Marca de agua (si existe)
    #                 if record.watermark_image:
    #                     watermark = Image.open(BytesIO(base64.b64decode(record.watermark_image))).convert("RGBA")
    #                     watermark = watermark.resize(
    #                         (int(compressed_image.width * 0.3), int(compressed_image.height * 0.3))
    #                     )
    #                     watermark.putalpha(128)
    #                     position = (
    #                         compressed_image.width - watermark.width - 10,
    #                         compressed_image.height - watermark.height - 10
    #                     )
    #                     base_rgba = compressed_image.convert("RGBA")
    #                     base_rgba.paste(watermark, position, watermark)
    #                     compressed_image = base_rgba.convert("RGB")

    #                 final_output = BytesIO()
    #                 compressed_image.save(final_output, format='JPEG', quality=70)
    #                 image_encoded = base64.b64encode(final_output.getvalue())

    #                 # Crear producto publicado
    #                 self.env['product.template'].create({
    #                     'name': image_line.filename or record.name or 'Foto de Equitación',
    #                     'image_1920': image_encoded,
    #                     'website_published': True,
    #                     'year': record.year,
    #                     'jump_height': record.jump_height,
    #                 })

    #                 # Agregar imagen al contenido HTML del sitio web
    #                 image_url = f"/web/image/fotos.equitacion.image.line/{image_line.id}/image_file"
    #                 html_content += (
    #                     f"<div style='margin: 10px;'>"
    #                     f"<img src='{image_url}' width='300'/><p>{image_line.filename or ''}</p>"
    #                     f"</div>"
    #                 )

    #             except Exception as e:
    #                 _logger.error(f"Error procesando imagen '{image_line.filename}': {e}")

    #         html_content += "</div>"

    #         # Crear página web
    #         self.env['website.page'].create({
    #             'name': f"{record.name} {record.year.strftime('%Y') if record.year else ''}",
    #             'url' : f"/equitacion/{slug(record.name or 'evento')}",
    #             'website_published': True,
    #             'type': 'qweb',
    #             'arch': f"""<t t-name="custom_fotos_equitacion_{record.id}">
    #                             {html_content}
    #                         </t>""",
    #         })
