window.onload = function () {

    var _quantity, _price, orderitem_num, delta_quantity, orderitem_quantity, delta_cost;
    var quantity_arr = [];
    var price_arr = [];

    var TOTAL_FORMS = parseInt($('input[name="orderitems-TOTAL_FORMS"]').val());

    var order_total_quantity = parseInt($('.order_total_quantity').text()) || 0;
    var order_total_cost = parseFloat($('.order_total_cost').text().replace(',', '.')) || 0;

    function reload_data() {
        for (var i=0; i < TOTAL_FORMS; i++) {
            _quantity = parseInt($('input[name="orderitems-' + i + '-quantity"]').val());
            _price = parseFloat($('.orderitems-' + i + '-price').text().replace(',', '.'));
            quantity_arr[i] = _quantity;
            if (_price) {
                price_arr[i] = _price;
            } else {
                price_arr[i] = 0;
            }
        }
    }
    reload_data()

    function orderSummaryRecalc() {
        order_total_quantity = 0;
        order_total_cost = 0;

        for (var i=0; i < TOTAL_FORMS; i++) {
            if (quantity_arr[i] != NaN){
                order_total_quantity += quantity_arr[i];
                order_total_cost += quantity_arr[i] * price_arr[i];
            }
            
        }
        $('.order_total_quantity').html(order_total_quantity.toString());
        $('.order_total_cost').html(Number(order_total_cost.toFixed(2)).toString());
    }

    if (!order_total_quantity) {
        orderSummaryRecalc();
    }

//            if (!order_total_quantity) {
//           for (var i=0; i < TOTAL_FORMS; i++) {
//               order_total_quantity += quantity_arr[i];
//               order_total_cost += quantity_arr[i] * price_arr[i];
//           }
//           $('.order_total_quantity').html(order_total_quantity.toString());
//           $('.order_total_cost').html(Number(order_total_cost.toFixed(2)).toString());
//        }

    function orderSummaryUpdate(orderitem_price, delta_quantity) {
        delta_cost = orderitem_price * delta_quantity;

        order_total_cost = Number((order_total_cost + delta_cost).toFixed(2));
        order_total_quantity = order_total_quantity + delta_quantity;

        $('.order_total_cost').html(order_total_cost.toString());
        $('.order_total_quantity').html(order_total_quantity.toString());
    } 

    function orderform_input_click (){
        $('.order_form').on('click', 'input[type="number"]', function () {
            var target = event.target;
            orderitem_num = parseInt(target.name.replace('orderitems-', '').replace('-quantity', ''));
            if (price_arr[orderitem_num]) {
                orderitem_quantity = parseInt(target.value);
                delta_quantity = orderitem_quantity - quantity_arr[orderitem_num];
                quantity_arr[orderitem_num] = orderitem_quantity;
                orderSummaryUpdate(price_arr[orderitem_num], delta_quantity);
            }
        });
    }
    
    orderform_input_click ()

    $('.order_form').on('click', 'input[type="checkbox"]', function () {
        var target = event.target;
        orderitem_num = parseInt(target.name.replace('orderitems-', '').replace('-DELETE', ''));
        if (target.checked) {
            delta_quantity = -quantity_arr[orderitem_num];
        } else {
            delta_quantity = quantity_arr[orderitem_num];
        }
        orderSummaryUpdate(price_arr[orderitem_num], delta_quantity);
    });

    function deleteOrderItem(row) {
        var target_name= row[0].querySelector('input[type="number"]').name;
        orderitem_num = parseInt(target_name.replace('orderitems-', '').replace('-quantity', ''));
        delta_quantity = -quantity_arr[orderitem_num];
        orderSummaryUpdate(price_arr[orderitem_num], delta_quantity);
    }

    function call_formset() {
        $('.formset_row').formset({
                addText: 'добавить продукт',
                deleteText: 'удалить',
                prefix: 'orderitems',
                removed: deleteOrderItem
            });
    }
    
    call_formset()

    function order_select() {
        $('.order_form select').change(function () {

            var target = event.target;
            orderitem_num = parseInt(target.name.replace('orderitems-', '').replace('-product', ''));
            var orderitem_product_pk = target.options[target.selectedIndex].value;

            if (orderitem_product_pk) {
                $.ajax({
                    url: "/orders/product/" + orderitem_product_pk + "/price/",
                    success: function (data) {
                        if (data.price) {
                            price_arr[orderitem_num] = parseFloat(data.price);
                            if (isNaN(quantity_arr[orderitem_num])) {
                                quantity_arr[orderitem_num] = 0;
                            }
                            var price_html = '<span>' + data.price.toString().replace('.', ',') + '</span> руб';
                            var current_tr = $('.order_form table').find('tr:eq(' + (orderitem_num + 1) + ')');

                            current_tr.find('td:eq(2)').html(price_html);

                            if (isNaN(current_tr.find('input[type="number"]').val())) {
                                current_tr.find('input[type="number"]').val(0);
                            }
                            orderform_input_click ()
                            orderSummaryRecalc();
                        }
                    },
                });
            }
        });
    }
    order_select()
    
    let ad_btn = document.querySelector('.add-row');
    ad_btn.addEventListener('click', function(){
        order_select();
        TOTAL_FORMS = parseInt($('input[name="orderitems-TOTAL_FORMS"]').val());
        let mytable = document.querySelector("table");
        let matches_quant = mytable.querySelectorAll("input[type='number']");
        matches_quant[matches_quant.length - 1].value = 0;
    });
}