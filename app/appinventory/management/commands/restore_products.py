from django.core.management.base import BaseCommand
from django.db import transaction
from appinventory.models import Product, ProductBrand, ProductCategory, UnitOfMeasure
import json


class Command(BaseCommand):
    help = 'Restore products from backup file'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_file',
            type=str,
            help='Path to the backup JSON file'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm the restoration process'
        )

    def handle(self, *args, **options):
        backup_file = options['backup_file']
        confirm = options['confirm']
        
        if not confirm:
            self.stdout.write(self.style.WARNING(
                '⚠️  This will modify your database. Use --confirm to proceed.'
            ))
            self.stdout.write('💡 Run with --confirm to execute the restoration.')
            return
        
        self.stdout.write(self.style.SUCCESS(f'🔄 Restoring from backup: {backup_file}...'))
        
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ Backup file not found: {backup_file}'))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'❌ Invalid JSON file: {e}'))
            return
        
        self.stdout.write(f'📦 Found backup with {backup_data["total_products"]} products')
        self.stdout.write(f'🕒 Backup timestamp: {backup_data["timestamp"]}')
        
        with transaction.atomic():
            restored_count = 0
            
            for product_data in backup_data['products']:
                # Crear o actualizar producto
                product, created = Product.objects.get_or_create(
                    id=product_data['id'],
                    defaults={
                        'name': product_data['name'],
                        'sku': product_data['sku'],
                        'model_number': product_data.get('model_number', '') or '',
                        'reorder_level': product_data['reorder_level'],
                        'is_active': product_data['is_active']
                    }
                )
                
                if not created:
                    # Actualizar producto existente
                    product.name = product_data['name']
                    product.sku = product_data['sku']
                    product.model_number = product_data.get('model_number', '') or ''
                    product.reorder_level = product_data['reorder_level']
                    product.is_active = product_data['is_active']
                    product.save()
                
                # Restaurar categoría si existe
                if product_data['category_id']:
                    try:
                        category = ProductCategory.objects.get(id=product_data['category_id'])
                        product.category = category
                        product.save()
                    except ProductCategory.DoesNotExist:
                        self.stdout.write(f'  ⚠️  Category {product_data["category_id"]} not found for product {product.id}')
                
                # Restaurar unidad por defecto si existe
                if product_data['unit_default_id']:
                    try:
                        unit = UnitOfMeasure.objects.get(id=product_data['unit_default_id'])
                        product.unit_default = unit
                        product.save()
                    except UnitOfMeasure.DoesNotExist:
                        self.stdout.write(f'  ⚠️  Unit {product_data["unit_default_id"]} not found for product {product.id}')
                
                # Restaurar marca (FK única; compat con backups con lista brands)
                brand_data = product_data.get('brand')
                if not brand_data and product_data.get('brands'):
                    brand_data = product_data['brands'][0]
                if brand_data:
                    try:
                        product.brand = ProductBrand.objects.get(id=brand_data['id'])
                        product.save(update_fields=['brand'])
                    except ProductBrand.DoesNotExist:
                        self.stdout.write(
                            f'  ⚠️  Brand {brand_data["id"]} not found for product {product.id}'
                        )
                
                restored_count += 1
                
                if restored_count % 10 == 0:
                    self.stdout.write(f'  📦 Restored {restored_count}/{backup_data["total_products"]} products...')
        
        self.stdout.write(f'\n🎉 Restoration complete!')
        self.stdout.write(f'📦 Products restored: {restored_count}')
        self.stdout.write(f'📁 From backup: {backup_file}')
