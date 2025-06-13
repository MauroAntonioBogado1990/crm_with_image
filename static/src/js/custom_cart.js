odoo.define('website_sale.photographer_button', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var Dialog = require('web.Dialog');

    $(document).on('click', '#contact_photographer', function (event) {
        event.preventDefault();
        var productId = $('#contact_photographer').data('product-id');

        console.log("📸 Botón 'Contactar Fotógrafo' clickeado. Enviando solicitud...");

        ajax.jsonRpc('/shop/contact_photographer', 'call', { product_id: productId })
            .then(function (data) {
                console.log("✅ Respuesta del backend recibida:", data);
                if (data.error) {
                    Dialog.alert(this, data.error);
                } else {
                    Dialog.alert(this, data.message + 
                        "\n📞 Teléfono del Fotógrafo: " + data.admin_phone);
                }
            });
    });
});
