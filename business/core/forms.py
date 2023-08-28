from decimal import Decimal

from django import forms

from core.constants import SellOperationErrors, SellItemErrors
from core.models import (
    TransferOperation,
    Account,
    ExtractOperation,
    BuyOperation,
    ItemIncome,
    Product,
)


class TransferOperationAdminForm(forms.ModelForm):
    source_accounts = forms.ModelChoiceField(Account.objects.filter(is_business=True))
    target_accounts = forms.ModelChoiceField(Account.objects.filter(is_business=True))

    class Meta:
        model = TransferOperation
        fields = (
            "source_accounts",
            "target_accounts",
            "operation_date",
            "amount",
        )

    def clean_source_accounts(self):
        # Validate unique source/target account
        if self.data["source_accounts"] == self.data.get("target_accounts"):
            self.add_error(
                "source_accounts",
                "Las cuentas de origen/destino no pueden ser las mismas",
            )

        # Validate enought founds
        amount = self.data.get("amount", 0)
        source_account_id = self.data.get("source_accounts")
        if Account.objects.get(id=source_account_id).balance < int(amount):
            self.add_error(
                "source_accounts",
                "La cuenta seleccionada no cuenta con fondos suficientes",
            )

        return [self.data["source_accounts"]]

    def clean_target_accounts(self):
        if self.data["target_accounts"] == self.data.get("source_accounts"):
            self.add_error(
                "target_accounts",
                "Las cuentas de origen/destino no pueden ser las mismas",
            )
        return [self.data["target_accounts"]]

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        # Update account's balance
        source_account = Account.objects.get(id=self.cleaned_data["source_accounts"][0])
        source_account.register_extract(instance.amount)
        target_account = Account.objects.get(id=self.cleaned_data["target_accounts"][0])
        target_account.register_income(instance.amount)
        return instance


class ExtractOperationAdminForm(forms.ModelForm):
    source_accounts = forms.ModelChoiceField(Account.objects.filter(is_business=True))
    target_accounts = forms.ModelChoiceField(Account.objects.filter(is_business=False))

    class Meta:
        model = ExtractOperation
        fields = (
            "source_accounts",
            "target_accounts",
            "operation_date",
            "period_from",
            "period_to",
            "amount",
            "cost",
            "profit",
            "observations",
        )

    def clean_amount(self):
        if not self.data.get("amount"):
            self.add_error(
                "amount", 'Debe obtener valores, presione el boton "Get Values"'
            )

    def clean_profit(self):
        if not self.data.get("profit"):
            self.add_error(
                "profit", 'Debe obtener valores, presione el boton "Get Values"'
            )

    def clean_cost(self):
        if not self.data.get("cost"):
            self.add_error(
                "cost", 'Debe obtener valores, presione el boton "Get Values"'
            )

    def clean_source_accounts(self):
        # Validate unique source/target account
        if self.data["source_accounts"] == self.data.get("target_accounts"):
            self.add_error(
                "source_accounts",
                "Las cuentas de origen/destino no pueden ser las mismas",
            )

        # Validate enought founds
        try:
            amount = int(self.data["amount"])
        except ValueError:
            amount = 0
        source_account_id = self.data.get("source_accounts")
        if Account.objects.get(id=source_account_id).balance < amount:
            self.add_error(
                "source_accounts",
                "La cuenta seleccionada no cuenta con fondos suficientes",
            )

        return [self.data["source_accounts"]]

    def clean_target_accounts(self):
        if self.data["target_accounts"] == self.data.get("source_accounts"):
            self.add_error(
                "target_accounts",
                "Las cuentas de origen/destino no pueden ser las mismas",
            )
        return [self.data["target_accounts"]]

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        # Update account's balance
        source_account = Account.objects.get(id=self.cleaned_data["source_accounts"][0])
        source_account.register_extract(instance.amount)
        target_account = Account.objects.get(id=self.cleaned_data["target_accounts"][0])
        target_account.register_income(instance.amount)
        return instance


class ItemIncomeAdminForm(forms.ModelForm):
    class Meta:
        model = ItemIncome
        fields = (
            "qty",
            "product",
            "operation",
        )

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        # Update product's stock
        instance.product.increase_stock(instance.qty)
        return instance


class BuyOperationAdminForm(forms.ModelForm):
    source_accounts = forms.ModelChoiceField(Account.objects.filter())

    class Meta:
        model = BuyOperation
        fields = (
            "operation_date",
            "source_accounts",
            "amount",
            "observations",
        )

    def clean_source_accounts(self):
        # Validate enough founds
        try:
            amount = int(self.data["amount"])
        except ValueError:
            amount = 0
        source_account_id = self.data.get("source_accounts")
        if Account.objects.get(id=source_account_id).balance < amount:
            self.add_error(
                "source_accounts",
                "La cuenta seleccionada no cuenta con fondos suficientes",
            )
        return [self.data["source_accounts"]]

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        # Update source_account balance
        source_account = Account.objects.get(id=self.cleaned_data["source_accounts"][0])
        source_account.register_extract(instance.amount)
        return instance


class SellItemAdminFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        all_cleaned_data = []
        amount = Decimal(0)
        cost = Decimal(0)
        profit = Decimal(0)

        for form in self.forms:
            if form.cleaned_data:
                all_cleaned_data += form.cleaned_data
                # Check if there is available stock
                if form.cleaned_data["qty"] > form.cleaned_data["product"].stock:
                    raise forms.ValidationError(
                        SellItemErrors.INSUFFICIENT_STOCK.format(
                            form.cleaned_data["product"].title,
                            form.cleaned_data["qty"],
                            form.cleaned_data["product"].stock,
                        )
                    )
                item_amount = Product.get_total_price(
                    form.cleaned_data["qty"], form.cleaned_data["product"].id
                )
                item_cost = Product.get_total_cost(
                    form.cleaned_data["qty"], form.cleaned_data["product"].id
                )
                amount += item_amount
                cost += item_cost
                profit += item_amount - item_cost

        self.instance.cost = cost
        self.instance.profit = profit

        if not all_cleaned_data:
            raise forms.ValidationError("No se selecciono ningun producto")


class SellOperationAccountFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        all_form_amounts = Decimal(0)
        for form in self.forms:
            all_form_amounts += (
                form.cleaned_data["amount"]
                if form.cleaned_data.get("amount")
                else Decimal(0)
            )
        if all_form_amounts != self.instance.amount:
            raise forms.ValidationError(
                SellOperationErrors.WRONG_TARGET_ACCOUNTS_AMOUNT
            )
