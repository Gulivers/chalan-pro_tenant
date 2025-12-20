from django.core.management.base import BaseCommand
from django.db import transaction
from appinventory.models import Product


class Command(BaseCommand):
    help = 'Delete all inactive products that were unified'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm the deletion process'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        confirm = options['confirm']
        dry_run = options['dry_run']
        
        if not confirm and not dry_run:
            self.stdout.write(self.style.WARNING(
                '[WARNING] This will permanently delete inactive products. Use --confirm to proceed.'
            ))
            self.stdout.write('[INFO] Use --dry-run to see what would be deleted.')
            return
        
        # Obtener productos inactivos
        inactive_products = Product.objects.filter(is_active=False)
        
        self.stdout.write(f'[INFO] Found {inactive_products.count()} inactive products')
        
        if inactive_products.count() == 0:
            self.stdout.write(self.style.WARNING('[WARNING] No inactive products found'))
            return
        
        # Mostrar productos que serán eliminados
        self.stdout.write('\n[INFO] Products to be deleted:')
        for product in inactive_products[:10]:  # Mostrar solo los primeros 10
            self.stdout.write(f'  - ID {product.id}: {product.name}')
        
        if inactive_products.count() > 10:
            self.stdout.write(f'  ... and {inactive_products.count() - 10} more products')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('[INFO] DRY RUN - No products were deleted'))
            return
        
        # Confirmar eliminación
        if not confirm:
            self.stdout.write(self.style.WARNING('[WARNING] Use --confirm to proceed with deletion'))
            return
        
        # Eliminar productos inactivos
        with transaction.atomic():
            deleted_count = 0
            
            for product in inactive_products:
                product_id = product.id
                product_name = product.name
                product.delete()
                deleted_count += 1
                
                if deleted_count % 50 == 0:
                    self.stdout.write(f'  [INFO] Deleted {deleted_count}/{inactive_products.count()} products...')
        
        self.stdout.write(f'\n[SUCCESS] Deletion complete!')
        self.stdout.write(f'[INFO] Products deleted: {deleted_count}')
        
        # Verificar productos activos restantes
        active_count = Product.objects.filter(is_active=True).count()
        self.stdout.write(f'[INFO] Active products remaining: {active_count}')
