from django.contrib import admin

from .forms import TransferOperationAdminForm
from .models import (
    Product,
    SellOperation,
    BuyOperation,
    TransferOperation,
    ExtractOperation,
    SellItem,
    BuyItem,
    Account,
    SellOperationAccount,
)


class SellItemAdmin(admin.TabularInline):
    model = SellItem
    readonly_fields = ['cost', 'amount', 'profit']


class ProductAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return super().get_list_display(request) + ['stock_in_boxes']


class SellOperationAccount(admin.TabularInline):
    model = SellOperationAccount


class SellOperationAdmin(admin.ModelAdmin):
    inlines = [SellItemAdmin, SellOperationAccount]
    readonly_fields = ['amount', 'target_accounts', 'source_accounts']

    class Media:
        js = (
            'js/admin.js',
        )

    def save_related(self, request, form, formsets, change):
        super(SellOperationAdmin, self).save_related(request, form, formsets, change)
        form.instance.validations_post_save()


class TransferOperationAdmin(admin.ModelAdmin):
    form = TransferOperationAdminForm

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_delete': False
        })
        return super().render_change_form(request, context, add, change, form_url, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('source_accounts', 'target_accounts', 'operation_date', 'amount')
        return super().get_readonly_fields(request, obj=None)


admin.site.register(Product, Product.get_admin_class(ProductAdmin))

# Sell
admin.site.register(SellItem)
admin.site.register(SellOperation, SellOperation.get_admin_class(SellOperationAdmin))

# Buy
admin.site.register(BuyOperation)
admin.site.register(BuyItem)

admin.site.register(TransferOperation, TransferOperation.get_admin_class(TransferOperationAdmin))
# admin.site.register(TransferOperation)

admin.site.register(ExtractOperation)

admin.site.register(Account, Account.get_admin_class())
