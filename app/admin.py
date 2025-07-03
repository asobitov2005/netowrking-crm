from datetime import datetime
from django.contrib import admin
from .models import (
    Product,
    Client,
    Inventory,
    Expense,
    ExpenseTransaction,
    SalesTransaction,
    SalesLineTransaction,
    Payment,
    Supplier,
    Purchase,
    PurchaseLine,
    Debt
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email')
    search_fields = ('name', 'phone', 'email')
    ordering = ('name',)


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity')
    search_fields = ('product__name',)
    autocomplete_fields = ('product',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'amount', 'date')
    list_filter = ('date',)
    search_fields = ('title',)


@admin.register(ExpenseTransaction)
class ExpenseTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'expense', 'date', 'comment')
    list_filter = ('date',)
    search_fields = ('expense__title', 'comment')


class SalesLineTransactionInline(admin.TabularInline):
    model = SalesLineTransaction
    extra = 1
    fields = ('product', 'quantity', 'price', 'value')
    readonly_fields = ('price', 'value')
    autocomplete_fields = ('product',)


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('amount', 'method', 'date')
    readonly_fields = ('date',)


@admin.register(SalesTransaction)
class SalesTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'client', 'date')
    search_fields = ('slug', 'client__name')
    list_filter = ('date',)
    inlines = [SalesLineTransactionInline, PaymentInline]
    autocomplete_fields = ('client',)
    readonly_fields = ('slug', 'date')


@admin.register(SalesLineTransaction)
class SalesLineTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'sales_transaction', 'product', 'quantity', 'price', 'value')
    autocomplete_fields = ('product', 'sales_transaction')
    readonly_fields = ('value',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'sales_transaction', 'amount', 'method', 'date')
    list_filter = ('method', 'date')
    autocomplete_fields = ('sales_transaction',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email')
    search_fields = ('name', 'phone', 'email')


class PurchaseLineInline(admin.TabularInline):
    model = PurchaseLine
    extra = 1
    fields = ('product', 'quantity', 'price')
    autocomplete_fields = ('product',)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'date')
    search_fields = ('supplier__name',)
    list_filter = ('date',)
    inlines = [PurchaseLineInline]
    autocomplete_fields = ('supplier',)


@admin.register(PurchaseLine)
class PurchaseLineAdmin(admin.ModelAdmin):
    list_display = ('id', 'purchase', 'product', 'quantity', 'price')
    autocomplete_fields = ('purchase', 'product')


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'sales_transaction', 'amount_due', 'is_paid')
    list_filter = ('is_paid',)
    search_fields = ('client__name', 'sales_transaction__slug')
    autocomplete_fields = ('client', 'sales_transaction')
