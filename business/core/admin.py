from django.contrib import admin

# Register your models here.
from core.models import Product, SellOperation, BuyOperation, TransferOperation, ExtractOperation, Stock, SellItem, \
    BuyItem, Account


class SellItemAdmin(admin.TabularInline):
    model = SellItem
    readonly_fields = ['cost', 'amount', 'profit']


class SellOperationAdmin(admin.ModelAdmin):
    inlines = [SellItemAdmin]
    readonly_fields = ['amount']


admin.site.register(Product)
admin.site.register(Stock)

# admin.site.register(SellOperation)
admin.site.register(SellItem)
admin.site.register(SellOperation, SellOperationAdmin)


admin.site.register(BuyOperation)
admin.site.register(BuyItem)

admin.site.register(TransferOperation)
admin.site.register(ExtractOperation)

admin.site.register(Account)
