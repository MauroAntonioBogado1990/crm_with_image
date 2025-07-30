odoo.define('crm_with_image.mass_image_upload', function (require) {
    "use strict";

    const Widget = require('web.Widget');
    const ajax = require('web.ajax');
    const registry = require('web.form_widget_registry');

    const MassImageUploader = Widget.extend({
        start: function () {
            const button = document.getElementById("btn_send_to_website");
            const input = document.getElementById("multiple_image_upload_input");
            const previewContainer = document.getElementById("multiple_image_previews");

            if (!button || !input || !previewContainer) {
                console.warn("Elementos necesarios no encontrados en el DOM.");
                return;
            }

            
            input.addEventListener('change', function () {
                previewContainer.innerHTML = ''; 

                [...this.files].forEach(file => {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        previewContainer.appendChild(img);
                    };
                    reader.readAsDataURL(file);
                });
            });

            // envio de imágenes al backend
            button.addEventListener("click", async () => {
                const name = document.querySelector('input[name="name"]').value;
                const year = document.querySelector('input[name="year"]').value;
                const jumpHeight = document.querySelector('input[name="jump_height"]').value;
                const watermarkInput = document.querySelector('input[name="watermark_image"]');
                const watermarkImage = watermarkInput?.files?.[0];
                const files = input?.files || [];

                const imagesData = await Promise.all([...files].map(file => new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        resolve({
                            filename: file.name,
                            image_file: e.target.result.split(',')[1],
                        });
                    };
                    reader.onerror = reject;
                    reader.readAsDataURL(file);
                })));

                let watermarkImageB64 = '';
                if (watermarkImage) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        watermarkImageB64 = e.target.result.split(',')[1];
                        _send();
                    };
                    reader.readAsDataURL(watermarkImage);
                } else {
                    _send();
                }

                function _send() {
                    ajax.jsonRpc('/equitacion/upload_mass_images', 'call', {
                        form_data: {
                            name,
                            year,
                            jump_height: jumpHeight,
                            watermark_image: watermarkImageB64
                        },
                        images_data: imagesData
                    }).then(response => {
                        alert(response.message);
                        if (response.success) location.reload();
                    }).catch(err => {
                        console.error("Error al enviar imágenes:", err);
                        alert("Error al enviar imágenes");
                    });
                }
            });

            return this._super(...arguments);
        }
    });

    registry.add('mass_image_uploader', MassImageUploader);
    return MassImageUploader;
});
