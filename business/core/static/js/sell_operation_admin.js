document.addEventListener("DOMContentLoaded", function(event) {
    let $ = django.jQuery

    $(document).ready(function(){
        // Set saved operation date
        let saved_operation_date = window.localStorage.getItem("selloperation_operation_date")
        $("#id_operation_date").val(saved_operation_date);

        function getIdFromString(string) {
            return parseInt(string.match(/\d+/)[0])
        }

        function updateTotalItemsAmount(){
            let total_sellitem_amount = 0;
            $('.dynamic-sellitem_set .field-amount input').each(function(index){
                let item_amount = parseFloat($('#id_sellitem_set-'+index+'-amount').val());
                if (!isNaN(item_amount)){
                    total_sellitem_amount = total_sellitem_amount + item_amount;
                }
            })
            $('#id_amount').val(total_sellitem_amount);
        }

        function updateValues(elementId, productId) {
            let qty = parseFloat($('#sellitem_set-' + elementId).find('.field-qty').children().val())
            if (!isNaN(elementId) & !isNaN(productId) & !isNaN(qty)) {
                $.ajax('/core/product/' + productId + '/values-by-qty/?qty=' + qty).done(function (response) {
                    // Set cost value
                    $('#id_sellitem_set-' + elementId + '-cost').val(response.cost);
                    $('#id_sellitem_set-' + elementId + '-cost').attr('readonly', true);


                    // Set amount value
                    $('#id_sellitem_set-' + elementId + '-amount').val(response.amount);
                    $('#id_sellitem_set-' + elementId + '-amount').attr('readonly', true);


                    // Set profit value
                    $('#id_sellitem_set-' + elementId + '-profit').val(response.profit);
                    $('#id_sellitem_set-' + elementId + '-profit').attr('readonly', true);

                    // increate Total Amount
                    updateTotalItemsAmount();
                })
            }

        }

        // Bind functions
        $('.field-qty input').on('keyup change',function (event) {
            let elementId = getIdFromString(this.id);
            // Get Id of selected product
            let productId = parseInt($('#id_sellitem_set-' + elementId + '-product').val())
            updateValues(elementId, productId);
        })
        $('.field-product select').change(function () {
            let elementId = getIdFromString(this.id);
            // Get Id of selected product
            let productId = parseInt($('#id_sellitem_set-' + elementId + '-product').val())
            updateValues(elementId, productId);
        })

        $('.dynamic-sellitem_set .inline-deletelink').click(function(){
            updateTotalItemsAmount();
        })

        // Save operation date in storage
        $('input[type="submit"]').click(function(){
            window.localStorage.setItem("selloperation_operation_date", $("#id_operation_date").val())
        })
    });
});
