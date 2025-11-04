from django.core.management.base import BaseCommand
from django.db import transaction
from appinventory.models import Product, ProductBrand
from difflib import SequenceMatcher
import re
from collections import defaultdict


class Command(BaseCommand):
    help = 'Analyze products to find similar ones with brand prefixes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--threshold',
            type=float,
            default=0.8,
            help='Similarity threshold (0.0 to 1.0) for grouping products'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show analysis without making changes'
        )

    def handle(self, *args, **options):
        threshold = options['threshold']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('[INFO] Analyzing products for unification...'))
        
        # Obtener todas las marcas activas
        brands = ProductBrand.objects.filter(is_active=True)
        brand_names = [brand.name.lower() for brand in brands]
        
        self.stdout.write(f'[INFO] Found {len(brand_names)} active brands: {", ".join(brand_names)}')
        
        # Obtener todos los productos activos
        products = Product.objects.filter(is_active=True).order_by('name')
        
        self.stdout.write(f'[INFO] Found {products.count()} active products')
        
        # Analizar productos
        similar_groups = self.find_similar_products(products, brand_names, threshold)
        
        if not similar_groups:
            self.stdout.write(self.style.WARNING('[WARNING] No similar product groups found'))
            return
            
        # Mostrar resultados
        self.display_analysis(similar_groups)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('[INFO] DRY RUN - No changes made'))
        else:
            self.stdout.write(self.style.SUCCESS('[SUCCESS] Analysis complete. Use unify_products command to proceed.'))

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

    def display_analysis(self, groups):
        """Muestra el análisis de grupos similares"""
        self.stdout.write(f'\n[INFO] Found {len(groups)} groups of similar products:\n')
        
        for i, group in enumerate(groups, 1):
            self.stdout.write(self.style.SUCCESS(f'Group {i}: "{group["clean_name"]}"'))
            self.stdout.write(f'  Brands: {", ".join(group["brands"])}')
            self.stdout.write(f'  Products ({len(group["products"])}):')
            
            for product in group['products']:
                brand, _ = self.extract_brand_from_name(product.name, [b for b in group['brands']])
                self.stdout.write(f'    - ID {product.id}: {product.name} (Brand: {brand})')
            
            self.stdout.write('')
        
        total_products = sum(len(group['products']) for group in groups)
        self.stdout.write(f'[INFO] Total products to be unified: {total_products}')
        self.stdout.write(f'[INFO] Products after unification: {len(groups)}')
        self.stdout.write(f'[INFO] Space saved: {total_products - len(groups)} products')
