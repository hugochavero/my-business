class AccountKind:
    CASH = 'Efectivo'
    BANK = 'Banco'
    CHOICES = (('cash', CASH), ('bank', BANK))


class SellOperationErrors:
    MISSING_TARGET_ACCOUNT = 'Se debe indicar una cuenta destino de los ingresos'
    WRONG_TARGET_ACCOUNTS_AMOUNT = 'No coincide el importe de los items vendidos contra el dinero distribuido en las cuentas destino'


class SellItemErrors:
    INSUFFICIENT_STOCK = 'Product {} con stock insuficiente. Requerido: {}, Existente: {}'
