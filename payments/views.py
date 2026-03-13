from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Payment


@login_required(login_url='login')
def payment_history(request):
    """Payment history view"""
    payments = Payment.objects.filter(user=request.user)
    total_amount = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'payments': payments,
        'total_amount': total_amount,
    }
    
    return render(request, 'payments/history.html', context)
