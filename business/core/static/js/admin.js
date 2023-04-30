document.addEventListener("DOMContentLoaded", function(event) {
    let $ = django.jQuery

    $(document).ready(function(){

    function updateValues(elementId, productId) {
        let qty = parseFloat($('#sellitem_set-' + elementId).find('.field-qty').children().val())
        if (elementId != null || undefined & productId != NaN & qty != NaN) {
            $.ajax('/core/product/' + productId + '/values-by-qty?qty=' + qty).done(function (response) {
                // Set cost value
                $('#sellitem_set-' + elementId).find('.field-cost').children().html(response.cost);
                // Set amount value
                $('#sellitem_set-' + elementId).find('.field-amount').children().html(response.amount);
                // Set profit value
                $('#sellitem_set-' + elementId).find('.field-profit').children().html(response.profit);
            })
        }
    }

    function getIdFromString(string) {
        return string.match(/\d+/)[0]
    }

    // Bind functions
    $('.field-qty input').change(function () {
        let elementId = getIdFromString(this.id);
        // Get Id of selected product
        let productId = $('#id_sellitem_set-' + elementId + '-product').val()
        updateValues(elementId, productId);
    })
    $('.field-product select').change(function () {
        let elementId = getIdFromString(this.id);
        // Get Id of selected product
        let productId = $('#id_sellitem_set-' + elementId + '-product').val()
        updateValues(elementId, productId);
    })

});
});
