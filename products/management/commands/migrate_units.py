from django.core.management.base import BaseCommand
from products.models import Unit, Product


class Command(BaseCommand):
    help = 'Create Unit rows for common legacy units and map existing Product.unit to product.unit_obj'

    COMMON_UNITS = [
        ('kg', 'kg'),
        ('liter', 'L'),
        ('bundle', 'bundle'),
        ('piece', 'pcs'),
    ]

    def handle(self, *args, **options):
        created = 0
        mapped = 0

        # Ensure common units exist
        for name, code in self.COMMON_UNITS:
            unit, was_created = Unit.objects.get_or_create(name=name.capitalize(), defaults={'code': code, 'slug': name})
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'Created unit: {unit.name}'))

        # Map existing products that don't have unit_obj
        products = Product.objects.filter(unit_obj__isnull=True)
        for p in products:
            legacy = (p.unit or '').lower()
            if not legacy:
                continue
            unit = Unit.objects.filter(slug=legacy).first() or Unit.objects.filter(name__iexact=legacy).first()
            if unit:
                p.unit_obj = unit
                p.save(update_fields=['unit_obj'])
                mapped += 1
                self.stdout.write(self.style.SUCCESS(f'Mapped product {p.id} ({p.name}) -> unit {unit.name}'))

        self.stdout.write(self.style.NOTICE(f'Units created: {created}, products mapped: {mapped}'))
