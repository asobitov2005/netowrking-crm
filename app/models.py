from datetime import datetime
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Product(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __str__(self):
        return self.name


class Client(TimeStampedModel):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')

    def __str__(self):
        return self.name


class Inventory(TimeStampedModel):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Inventory')
        verbose_name_plural = _('Inventories')

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class Expense(TimeStampedModel):
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = _('Expense')
        verbose_name_plural = _('Expenses')

    def __str__(self):
        return f"{self.title} - {self.amount}"


class ExpenseTransaction(TimeStampedModel):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Expense Transaction')
        verbose_name_plural = _('Expense Transactions')

    def __str__(self):
        return f"Transaction for {self.expense}"


class SalesTransaction(TimeStampedModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True)
    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.client.name}-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.slug


class SalesLineTransaction(TimeStampedModel):
    sales_transaction = models.ForeignKey(SalesTransaction, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    value = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    class Meta:
        verbose_name = _('Sale Transaction Line')
        verbose_name_plural = _('Sale Transaction Lines')

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        self.value = self.quantity * self.price

        # Inventory kamaytirish
        inventory = Inventory.objects.get(product=self.product)
        inventory.quantity -= self.quantity
        inventory.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Payment(TimeStampedModel):
    sales_transaction = models.ForeignKey(SalesTransaction, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50, choices=[
        ('cash', _('Cash')),
        ('card', _('Card')),
        ('transfer', _('Bank Transfer')),
    ])

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    def __str__(self):
        return f"{self.sales_transaction} - {self.amount}"


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        verbose_name = _('Supplier')
        verbose_name_plural = _('Suppliers')

    def __str__(self):
        return self.name


class Purchase(TimeStampedModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = _('Purchase')
        verbose_name_plural = _('Purchases')

    def __str__(self):
        return f"Purchase from {self.supplier.name} on {self.date}"


class PurchaseLine(TimeStampedModel):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        inventory, created = Inventory.objects.get_or_create(product=self.product)
        inventory.quantity += self.quantity
        inventory.save()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} @ {self.price}"


class Debt(TimeStampedModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    sales_transaction = models.OneToOneField(SalesTransaction, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Debt')
        verbose_name_plural = _('Debts')

    def __str__(self):
        return f"{self.client.name} owes {self.amount_due}"
