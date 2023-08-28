class AccountKind:
    CASH = "Efectivo"
    BANK = "Transferencia"
    CHOICES = (("cash", CASH), ("bank", BANK))


class SellOperationErrors:
    MISSING_TARGET_ACCOUNT = "Se debe indicar una cuenta destino de los ingresos"
    WRONG_TARGET_ACCOUNTS_AMOUNT = "No coincide el importe de los items vendidos contra el dinero distribuido en las cuentas destino"


class SellItemErrors:
    INSUFFICIENT_STOCK = (
        "Product {} con stock insuficiente. Requerido: {}, Existente: {}"
    )


class TransferOperationErrors:
    INSUFFICIENT_FOUNDS = "Fondos insuficientes en cuenta de origen"


class ExtractOperationErrors:
    INSUFFICIENT_AMOUNT = "No existen operaciones para el rango de fecha dado"


class ExpenseOperationCategory:
    TRANSPORT = "Transporte"
    OTHER = "Otros"
    CHOICES = (("transport", TRANSPORT), ("other", OTHER))


class BuyOperationErrors:
    WRONG_SOURCE_ACCOUNT_AMOUNT = "No coincide el importe de los items comprados contra el dinero a descontar en la cuenta origen"
