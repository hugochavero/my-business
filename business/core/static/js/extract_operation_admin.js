document.addEventListener("DOMContentLoaded", function(event) {
    let $ = django.jQuery

    $(document).ready(function(){
        let default_buttons = $('.submit-row').html()
        let values_button = '<input type="button" value="Get Values" id="get_values_btn">'
        $('.submit-row').html(values_button + default_buttons);

        function getValues() {
            let dateFrom = $("#id_period_from").val();
            let dateTo = $("#id_period_to").val();

            if (dateFrom != '' & dateTo != '') {
                $.get('/core/sell-operation/values-by-date-range?date_from=' + dateFrom + '&date_to=' + dateTo).done(function (response) {
                    let message = 'Valores calculados para el periodo: ' + dateFrom + ' - ' + dateTo + '\n\n\n' +
                        'Costo: ' + response.cost + '\n' +
                        'Ganancia: ' + response.profit + '\n' +
                        'Bruto: ' + response.amount
                    alert(message);

                    $('#id_amount').val(response.amount);
                    $('#id_cost').val(response.cost);
                    $('#id_profit').val(response.profit);
                })
            }else {
                alert("Debe ingresar fecha desde / hasta")
            }
        }

        $('#get_values_btn').click(getValues);
    });
});
