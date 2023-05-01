from django.contrib import admin

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


class ProductAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return super().get_list_display(request) + ['stock_in_boxes']


admin.site.register(Product, Product.get_admin_class(ProductAdmin))

# Sell
admin.site.register(SellItem)
admin.site.register(SellOperation, SellOperation.get_admin_class(SellOperationAdmin))

# Buy
admin.site.register(BuyOperation)
admin.site.register(BuyItem)

admin.site.register(TransferOperation)
admin.site.register(ExtractOperation)

admin.site.register(Account, Account.get_admin_class())
