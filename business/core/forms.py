from django import forms
from core.models import TransferOperation, Account


class TransferOperationAdminForm(forms.ModelForm):
    source_accounts = forms.ModelChoiceField(Account.objects.all())
    target_accounts = forms.ModelChoiceField(Account.objects.all())

    class Meta:
        model = TransferOperation
        fields = ('source_accounts', 'target_accounts', 'operation_date', 'amount',)

    def clean_source_accounts(self):
        # Validate unique source/target account
        if self.data['source_accounts'] == self.data.get('target_accounts'):
            self.add_error('source_accounts', 'Las cuentas de origen/destino no pueden ser las mismas')

        # Validate enought founds
        amount = self.data.get('amount', 0)
        source_account_id = self.data.get('source_accounts')
        if Account.objects.get(id=source_account_id).balance < int(amount):
            self.add_error('source_accounts', 'La cuenta seleccionada no cuenta con fondos suficientes')

        return [self.data['source_accounts']]

    def clean_target_accounts(self):
        if self.data['target_accounts'] == self.data.get('source_accounts'):
            self.add_error('target_accounts', 'Las cuentas de origen/destino no pueden ser las mismas')
        return [self.data['target_accounts']]

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        # Update account's balance
        source_account = Account.objects.get(id=self.cleaned_data['source_accounts'][0])
        source_account.register_extract(instance.amount)
        target_account = Account.objects.get(id=self.cleaned_data['target_accounts'][0])
        target_account.register_income(instance.amount)
        return instance
