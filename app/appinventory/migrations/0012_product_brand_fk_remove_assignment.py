"""
Replace Product.brands M2M (through ProductBrandAssignment) with Product.brand FK.
Drop ProductImage.assignment; images belong only to the product.

Multi-brand products: keep the first assignment by id (ORDER BY id ASC).
"""
import django.db.models.deletion
from django.db import migrations, models


def forwards_copy_brand(apps, schema_editor):
    Product = apps.get_model('appinventory', 'Product')
    ProductBrandAssignment = apps.get_model('appinventory', 'ProductBrandAssignment')

    # First assignment per product (lowest id wins).
    seen = set()
    for row in (
        ProductBrandAssignment.objects.order_by('id').values_list('product_id', 'brand_id')
    ):
        product_id, brand_id = row
        if product_id in seen:
            continue
        seen.add(product_id)
        Product.objects.filter(pk=product_id, brand_id__isnull=True).update(brand_id=brand_id)


def backwards_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('appinventory', '0011_product_model_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(
                blank=True,
                help_text='Marca del producto (una por producto).',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='products',
                to='appinventory.productbrand',
            ),
        ),
        migrations.RunPython(forwards_copy_brand, backwards_noop),
        migrations.RemoveIndex(
            model_name='productimage',
            name='appinventor_assignm_291eff_idx',
        ),
        migrations.RemoveIndex(
            model_name='productimage',
            name='appinventor_assignm_e20459_idx',
        ),
        migrations.RemoveField(
            model_name='productimage',
            name='assignment',
        ),
        migrations.RemoveField(
            model_name='product',
            name='brands',
        ),
        migrations.DeleteModel(
            name='ProductBrandAssignment',
        ),
        migrations.AddIndex(
            model_name='productimage',
            index=models.Index(fields=['product'], name='appinventor_product_img_p_idx'),
        ),
        migrations.AddIndex(
            model_name='productimage',
            index=models.Index(fields=['product', 'is_primary'], name='appinventor_product_img_pp_idx'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='is_primary',
            field=models.BooleanField(
                default=False,
                help_text='Indica si esta es la imagen principal del producto',
            ),
        ),
    ]
