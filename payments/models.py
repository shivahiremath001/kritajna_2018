from django.db import models
from users.models import User


class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('subscription', 'Farmer Subscription'),
        ('order', 'Order Payment'),
        ('delivery_earning', 'Delivery Earning'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.amount} by {self.user.username}"
    
    class Meta:
        ordering = ['-date']
