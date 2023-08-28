document.addEventListener("DOMContentLoaded", function(event) {
    let $ = django.jQuery

    let item_amounts_list = []
    let item_amounts_list_storage = window.localStorage.getItem('item_amounts_list')
    if (item_amounts_list_storage != null){
        item_amounts_list = JSON.parse(item_amounts_list_storage);
    }

    let expense_amounts_list = [];
    let expense_amounts_list_storage = window.localStorage.getItem('expense_amounts_list');
    if (expense_amounts_list_storage != null){
        expense_amounts_list = JSON.parse(expense_amounts_list_storage);
    }

    let selected_product_amount = []
    let selected_product_amount_storage = window.localStorage.getItem('selected_product_amount');
    if (selected_product_amount_storage != null){
        selected_product_amount = JSON.parse(selected_product_amount_storage);
    }

    $(document).ready(function(){
        // Reset local storage if no error
        if (!Boolean($('.errornote').length)){
            window.localStorage.removeItem('item_amounts_list');
            window.localStorage.removeItem('expense_amounts_list');
            window.localStorage.removeItem('selected_product_amount');
        }

        function getIdFromString(string) {
            return parseInt(string.match(/\d+/)[0])
        }

        function increaseTotalAmount(elementId, amount, group){
            let aux = 0;

            switch (group) {
                case 'item_income':
                    item_amounts_list[elementId] = amount;
                    break
                case 'expense':
                    expense_amounts_list[elementId] = amount;
                    break
            }
            for (let currentAmountKey in item_amounts_list) {
                aux += item_amounts_list[currentAmountKey];
            }
            for (let currentAmountKey in expense_amounts_list) {
                aux += expense_amounts_list[currentAmountKey];
            }
            // Update localstorage vars
            window.localStorage.setItem('item_amounts_list', JSON.stringify(item_amounts_list))
            window.localStorage.setItem('expense_amounts_list', JSON.stringify(expense_amounts_list))

            $('#id_amount').val(aux);
        }

        function decreaseTotalAmount(){
            let amount_field = $($(".readonly")[0]);
            let current_amount = parseFloat(amount_field.html());
            if (isNaN(current_amount)) {
                current_amount = 0;
            }
            amount_field.html(current_amount - amount);
        }

        function updateValues(elementId, productId) {
            let qty = parseFloat($('#itemincome_set-' + elementId).find('.field-qty').children().val())
            if (!isNaN(elementId) & !isNaN(productId)) {
                $.ajax('/core/product/' + productId + '/values-by-qty?qty=1').done(function (response) {
                    // Set cost value
                    $('#itemincome_set-' + elementId).find('.field-cost').children().html(response.cost);
                    // Set amount value
                    $('#itemincome_set-' + elementId).find('.field-amount').children().html(response.amount);
                    // Set profit value
                    $('#itemincome_set-' + elementId).find('.field-profit').children().html(response.profit);
                    // Set product_amount prop
                    selected_product_amount[elementId] = response.amount;
                    window.localStorage.setItem('selected_product_amount', JSON.stringify(selected_product_amount));

                    // Set total value
                    if (!isNaN(qty)) {
                        let total = qty * response.amount;
                        // Update product Total
                        $('#itemincome_set-' + elementId).find('.field-total').children().html(total);
                        // Increase Total Amount
                        increaseTotalAmount(elementId, total, 'item_income');
                    }
                })
            }else{
                // Set cost value
                $('#itemincome_set-' + elementId).find('.field-cost').children().html(0);
                // Set amount value
                $('#itemincome_set-' + elementId).find('.field-amount').children().html(0);
                // Set profit value
                $('#itemincome_set-' + elementId).find('.field-profit').children().html(0);
                // Set product_amount prop
                selected_product_amount[elementId] = 0;
                window.localStorage.setItem('selected_product_amount', JSON.stringify(selected_product_amount));

                // Update product Total
                $('#itemincome_set-' + elementId).find('.field-total').children().html(0);
                // Update Total Amount
                increaseTotalAmount(elementId, 0, 'item_income');
            }
        }
        function updateTotalAmount(event, elementId) {
            let product_amount = selected_product_amount[elementId];
            if (product_amount != undefined){
                let total = $(event.target).val() * product_amount
                $('#itemincome_set-' + elementId).find('.field-total').children().html(total);
                increaseTotalAmount(elementId, total, 'item_income');
            }
        }

        // Bind functions
        $('.field-qty input').on('keyup change',function (event) {
            let elementId = getIdFromString(this.id);
            updateTotalAmount(event, elementId);
        })
        $('.field-product select').change(function () {
            let elementId = getIdFromString(this.id);
            // Get Id of selected product
            let productId = parseInt($('#id_itemincome_set-' + elementId + '-product').val())
            updateValues(elementId, productId);
        })
        $('.field-amount input').on('keyup change',function (event) {
            let elementId = getIdFromString(this.id);
            let amount = parseFloat(this.value);
            if (!isNaN(amount)){
                increaseTotalAmount(elementId, amount, 'expense')
            }
        })

        // TODO: Terminar
        $('.dynamic-sellitem_set .delete a').on('click', function(target){
            console.dir(target)
            let elementId = getIdFromString(this.id);
        })
        $('.dynamic-sellitem_set .delete a').click(function(){
            // let elementId = getIdFromString(this.id);
            // let deleted_amount = parseInt($('#id_sellitem_set-' + elementId + '-amount').val())
            //decreaseTotalAmount(deleted_amount);
        })

    });
});
