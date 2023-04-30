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



admin.site.register(Product, Product.get_admin_class())

admin.site.register(SellItem)
admin.site.register(SellOperation, SellOperationAdmin)


admin.site.register(BuyOperation)
admin.site.register(BuyItem)

admin.site.register(TransferOperation)
admin.site.register(ExtractOperation)

admin.site.register(Account)
