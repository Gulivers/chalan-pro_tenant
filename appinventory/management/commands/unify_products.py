from django.core.management.base import BaseCommand
from django.db import transaction
from appinventory.models import Product, ProductBrand
from difflib import SequenceMatcher
import re
from collections import defaultdict


class Command(BaseCommand):
    help = 'Unify products with similar names but different brand prefixes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--threshold',
            type=float,
            default=0.8,
            help='Similarity threshold (0.0 to 1.0) for grouping products'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm the unification process'
        )

    def handle(self, *args, **options):
        threshold = options['threshold']
        confirm = options['confirm']
        
        if not confirm:
            self.stdout.write(self.style.WARNING(
                '[WARNING] This will modify your database. Use --confirm to proceed.'
            ))
            self.stdout.write('[INFO] Run with --confirm to execute the unification.')
            return
        
        self.stdout.write(self.style.SUCCESS('[INFO] Starting product unification...'))
        
        # Obtener todas las marcas activas
        brands = ProductBrand.objects.filter(is_active=True)
        brand_names = [brand.name.lower() for brand in brands]
        
        self.stdout.write(f'[INFO] Found {len(brand_names)} active brands')
        
        # Obtener todos los productos activos
        products = Product.objects.filter(is_active=True).order_by('name')
        
        self.stdout.write(f'[INFO] Found {products.count()} active products')
        
        # Encontrar grupos similares
        similar_groups = self.find_similar_products(products, brand_names, threshold)
        
        if not similar_groups:
            self.stdout.write(self.style.WARNING('[WARNING] No similar product groups found'))
            return
        
        self.stdout.write(f'[INFO] Found {len(similar_groups)} groups to unify')
        
        # Ejecutar unificación
        with transaction.atomic():
            unified_count = 0
            deactivated_count = 0
            
            for i, group in enumerate(similar_groups, 1):
                self.stdout.write(f'\n[INFO] Processing group {i}/{len(similar_groups)}: "{group["clean_name"]}"')
                
                unified_product, deactivated_ids = self.unify_product_group(group, brand_names)
                
                if unified_product:
                    unified_count += 1
                    deactivated_count += len(deactivated_ids)
                    
                    self.stdout.write(f'  [SUCCESS] Created unified product: ID {unified_product.id}')
                    self.stdout.write(f'  [INFO] Deactivated {len(deactivated_ids)} original products')
        
        self.stdout.write(f'\n[SUCCESS] Unification complete!')
        self.stdout.write(f'  [INFO] Unified products created: {unified_count}')
        self.stdout.write(f'  [INFO] Original products deactivated: {deactivated_count}')

    def find_similar_products(self, products, brand_names, threshold):
        """Encuentra grupos de productos similares con marcas como prefijo"""
        groups = []
        processed_products = set()
        
        for product in products:
            if product.id in processed_products:
                continue
                
            # Extraer marca del nombre del producto
            brand_found, clean_name = self.extract_brand_from_name(product.name, brand_names)
            
            if not brand_found:
                continue
                
            # Buscar productos similares
            similar_products = [product]
            
            for other_product in products:
                if (other_product.id in processed_products or 
                    other_product.id == product.id):
                    continue
                    
                other_brand, other_clean_name = self.extract_brand_from_name(
                    other_product.name, brand_names
                )
                
                if not other_brand:
                    continue
                    
                # Comparar nombres limpios
                similarity = SequenceMatcher(None, clean_name.lower(), other_clean_name.lower()).ratio()
                
                if similarity >= threshold:
                    similar_products.append(other_product)
                    processed_products.add(other_product.id)
            
            if len(similar_products) > 1:
                groups.append({
                    'clean_name': clean_name,
                    'products': similar_products,
                    'brands': [self.extract_brand_from_name(p.name, brand_names)[0] for p in similar_products]
                })
                processed_products.add(product.id)
        
        return groups

    def extract_brand_from_name(self, product_name, brand_names):
        """Extrae la marca del nombre del producto y devuelve el nombre limpio"""
        product_name_lower = product_name.lower()
        
        for brand_name in brand_names:
            if product_name_lower.startswith(brand_name.lower()):
                # Remover marca del inicio y espacios extra
                clean_name = product_name[len(brand_name):].strip()
                return brand_name, clean_name
                
        return None, product_name

    def unify_product_group(self, group, brand_names):
        """Unifica un grupo de productos similares"""
        products = group['products']
        clean_name = group['clean_name']
        
        # Usar el primer producto como base
        base_product = products[0]
        
        # Crear nuevo producto unificado
        unified_product = Product.objects.create(
            name=clean_name,
            sku=f"UNIFIED-{base_product.id}",  # SKU temporal
            category=base_product.category,
            reorder_level=base_product.reorder_level,
            unit_default=base_product.unit_default,
            is_active=True
        )
        
        # Obtener objetos de marca y asignarlos
        brand_objects = []
        for brand_name in group['brands']:
            try:
                brand_obj = ProductBrand.objects.get(name__iexact=brand_name)
                brand_objects.append(brand_obj)
            except ProductBrand.DoesNotExist:
                self.stdout.write(f'  [WARNING] Brand "{brand_name}" not found, skipping')
        
        # Asignar marcas al producto unificado
        if brand_objects:
            unified_product.brands.set(brand_objects)
            
            # Marcar la primera marca como default
            if brand_objects:
                first_brand = brand_objects[0]
                first_brand.is_default = True
                first_brand.save()
        
        # Desactivar productos originales
        deactivated_ids = []
        for product in products:
            product.is_active = False
            product.save()
            deactivated_ids.append(product.id)
        
        return unified_product, deactivated_ids
