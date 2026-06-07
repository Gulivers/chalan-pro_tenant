import hashlib
from decimal import Decimal

from apptransactions.models import DocumentLine


def _decimal_to_str(value):
    if value is None:
        return ''
    if isinstance(value, Decimal):
        return format(value, 'f')
    return str(value)


def _join_parts(parts):
    return ' | '.join(part.strip() for part in parts if part and str(part).strip())


def build_document_line_chunk(line: DocumentLine) -> tuple[str, dict]:
    """
    Build denormalized search text and filterable metadata for a DocumentLine.
    """
    document = line.document
    document_type = getattr(document, 'document_type', None)
    builder = getattr(document, 'builder', None)
    work_account = getattr(document, 'work_account', None)
    product = line.product
    category = getattr(product, 'category', None) if product else None
    brand = line.brand
    job = getattr(work_account, 'job', None) if work_account else None
    house_model = getattr(work_account, 'house_model', None) if work_account else None

    work_account_parts = []
    if work_account:
        if work_account.title:
            work_account_parts.append(work_account.title)
        if job and job.name:
            work_account_parts.append(job.name)
        if house_model and house_model.name:
            work_account_parts.append(house_model.name)
        if work_account.lot:
            work_account_parts.append(f'Lot {work_account.lot}')
        if work_account.address:
            work_account_parts.append(work_account.address)

    chunk_text = _join_parts([
        getattr(document_type, 'type_code', ''),
        getattr(document_type, 'description', ''),
        getattr(builder, 'name', ''),
        _join_parts(work_account_parts),
        getattr(product, 'name', ''),
        getattr(product, 'sku', ''),
        getattr(product, 'model_number', ''),
        getattr(category, 'name', ''),
        getattr(brand, 'name', ''),
        getattr(document, 'notes', ''),
    ])

    metadata = {
        'document_id': document.id if document else None,
        'document_line_id': line.id,
        'document_type_id': document_type.id if document_type else None,
        'document_type_code': getattr(document_type, 'type_code', None),
        'is_purchase': bool(getattr(document_type, 'is_purchase', False)),
        'is_sales': bool(getattr(document_type, 'is_sales', False)),
        'is_operational': bool(getattr(document_type, 'is_operational', False)),
        'builder_id': builder.id if builder else None,
        'builder_name': getattr(builder, 'name', None),
        'work_account_id': work_account.id if work_account else None,
        'work_account_title': getattr(work_account, 'title', None),
        'job_id': job.id if job else None,
        'job_name': getattr(job, 'name', None),
        'product_id': product.id if product else None,
        'product_name': getattr(product, 'name', None),
        'product_category_id': category.id if category else None,
        'product_category_name': getattr(category, 'name', None),
        'brand_id': brand.id if brand else None,
        'brand_name': getattr(brand, 'name', None),
        'warehouse_id': line.warehouse_id,
        'date': document.date.isoformat() if document and document.date else None,
        'final_price': _decimal_to_str(line.final_price),
        'quantity': _decimal_to_str(line.quantity),
        'unit_price': _decimal_to_str(line.unit_price),
        'is_active': bool(getattr(document, 'is_active', True)),
    }

    return chunk_text, metadata


def content_hash_for_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def get_document_line_queryset():
    return (
        DocumentLine.objects.select_related(
            'document',
            'document__document_type',
            'document__builder',
            'document__work_account',
            'document__work_account__job',
            'document__work_account__house_model',
            'product',
            'product__category',
            'brand',
            'warehouse',
        )
        .order_by('id')
    )
