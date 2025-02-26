from django.db import models
from decimal import Decimal

class Medicine(models.Model):
    medicine_name = models.CharField(max_length=255)
    generic_name = models.CharField(max_length=255, blank=True, null=True)
    brand_name = models.CharField(max_length=255, blank=True, null=True)
    dosage = models.CharField(max_length=100, blank=True, null=True)  # NEW field added here
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total_quantity = models.PositiveIntegerField(default=0)
    supplier_name = models.CharField(max_length=255)
    date_last_stock = models.DateField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.medicine_name

class MedicineStock(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="stocks")
    quantity = models.PositiveIntegerField(default=0)
    expiration_date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.medicine.medicine_name} ({self.quantity} units, expires {self.expiration_date:%b %d, %Y})"
    
    @property
    def total_price(self):
        return self.quantity * self.medicine.unit_price
