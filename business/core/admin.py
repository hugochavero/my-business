from django.contrib import admin

from .forms import (
    TransferOperationAdminForm,
    ExtractOperationAdminForm,
    BuyOperationAdminForm,
    ItemIncomeAdminForm,
    SellItemAdminFormSet,
    SellOperationAccountFormSet,
)
from .models import (
    Product,
    SellOperation,
    BuyOperation,
    TransferOperation,
    ExtractOperation,
    SellItem,
    ItemIncome,
    Account,
    SellOperationAccount,
)
from .models.operation import ExpenseOperation


class ProductAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return super().get_list_display(request) + ["stock_in_boxes"]


class SellItemAdmin(admin.TabularInline):
    model = SellItem
    formset = SellItemAdminFormSet


class SellOperationAccount(admin.TabularInline):
    model = SellOperationAccount
    formset = SellOperationAccountFormSet


class SellOperationAdmin(admin.ModelAdmin):
    inlines = [SellItemAdmin, SellOperationAccount]
    fields = ["operation_date", "amount", "target_accounts"]
    readonly_fields = ["target_accounts"]

    class Media:
        js = ("js/sell_operation_admin.js",)


class TransferOperationAdmin(admin.ModelAdmin):
    form = TransferOperationAdminForm


class ExtractOperationAdmin(admin.ModelAdmin):
    form = ExtractOperationAdminForm

    class Media:
        js = ("js/extract_operation_admin.js",)


class BuyItemAdmin(admin.TabularInline):
    model = ItemIncome
    readonly_fields = ["cost", "profit", "amount", "total"]
    form = ItemIncomeAdminForm

    @staticmethod
    def cost(instance):
        try:
            return instance.product.cost
        except ItemIncome.RelatedObjectDoesNotExist:
            return "-"

    @staticmethod
    def profit(instance):
        try:
            return instance.product.price - instance.product.cost
        except ItemIncome.RelatedObjectDoesNotExist:
            return "-"

    @staticmethod
    def amount(instance):
        try:
            return instance.product.price
        except ItemIncome.RelatedObjectDoesNotExist:
            return "-"

    @staticmethod
    def total(instance):
        if instance.qty:
            try:
                return instance.product.price * instance.qty
            except ItemIncome.RelatedObjectDoesNotExist:
                return "-"
        return "-"


class ExpenseOperationAdmin(admin.TabularInline):
    model = ExpenseOperation


class BuyOperationAdmin(admin.ModelAdmin):
    inlines = [BuyItemAdmin, ExpenseOperationAdmin]
    form = BuyOperationAdminForm

    class Media:
        js = ("js/buy_operation_admin.js",)

    def save_related(self, request, form, formsets, change):
        super(BuyOperationAdmin, self).save_related(request, form, formsets, change)
        form.instance.validations_post_save()


admin.site.register(Product, Product.get_admin_class(ProductAdmin))

# Sell
admin.site.register(SellItem)
admin.site.register(SellOperation, SellOperation.get_admin_class(SellOperationAdmin))

# Buy
admin.site.register(BuyOperation, BuyOperation.get_admin_class(BuyOperationAdmin))
admin.site.register(ItemIncome)

admin.site.register(
    TransferOperation, TransferOperation.get_admin_class(TransferOperationAdmin)
)
admin.site.register(
    ExtractOperation, ExtractOperation.get_admin_class(ExtractOperationAdmin)
)

admin.site.register(Account, Account.get_admin_class())
