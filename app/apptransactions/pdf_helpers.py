"""Shared helpers for WeasyPrint PDF builders (no imports from pdf_service)."""
from django.core.exceptions import ObjectDoesNotExist

from utils.tenant_branding import file_field_to_pdf_uri


def select_product_image(product, brand_id=None):
    """Primary image of the product, else first available. brand_id is ignored."""
    if product is None:
        return None
    images = list(product.images.all())
    if not images:
        return None
    for image in images:
        if image.is_primary:
            return image
    return images[0]


def line_product_image_pdf_uri(line, request):
    product = getattr(line, 'product', None)
    brand_id = getattr(line, 'brand_id', None)
    image = select_product_image(product, brand_id=brand_id)
    if image is None and brand_id is not None:
        image = select_product_image(product, brand_id=None)
    if image is None or not getattr(image, 'image', None):
        return None
    return file_field_to_pdf_uri(image.image, request=request)


def current_status_for_pdf(document):
    """
    Prefer DocumentTracking.current_status; else latest history to_status.
    """
    tracking = None
    try:
        tracking = document.tracking
    except ObjectDoesNotExist:
        tracking = None

    if tracking is not None and getattr(tracking, 'current_status_id', None):
        return tracking.current_status, tracking.status_changed_at

    history = list(document.tracking_history.all())
    if history:
        last = history[-1]
        return last.to_status, last.changed_at
    return None, None


def phase_name(document):
    event = getattr(document, 'work_order', None)
    if not event or not getattr(event, 'crew_id', None):
        return ''
    crew = event.crew
    category = getattr(crew, 'category', None)
    return category.name if category else ''
