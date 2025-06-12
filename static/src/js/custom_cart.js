odoo.define('website_sale.custom_cart', function (require) {
    'use strict';

    var ajax = require('web.ajax');

    $(document).on('click', '.oe_website_sale .add_to_cart', function (event) {
        event.preventDefault();
        
        var product_id = $(this).data('product-id');

        ajax.jsonRpc("/shop/cart/add", 'call', {'product_id': product_id}).then(function (data) {
            if (data.error) {
                alert(data.error);
            } else {
                var popupContent = `<div style="padding: 20px; text-align: center;">
                    <h3>${data.message}</h3>
                    <p><strong>Cliente:</strong> ${data.user_name}</p>
                    <p><strong>Teléfono:</strong> ${data.phone}</p>
                    <p><strong>Alias (Cuenta Bancaria):</strong> ${data.alias}</p>
                </div>`;

                $('body').append(`<div id="custom-popup" style="position: fixed; top: 20%; left: 30%; background: white; padding: 20px; border: 2px solid #ccc; z-index: 9999;">${popupContent}<button onclick="$('#custom-popup').remove();">Cerrar</button></div>`);
            }
        });
    });
});