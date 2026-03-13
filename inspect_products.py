import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','kritajna.settings')
import django
django.setup()
from products.models import Product, Unit
for p in Product.objects.all()[:50]:
    print(p.id, repr(p.name), 'price=', p.price, 'price_per_unit=', p.price_per_unit, 'unit=', p.unit, 'unit_obj=', getattr(p.unit_obj, 'name', None))
print('Units:', list(Unit.objects.values_list('id','name','code')))
