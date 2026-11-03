# -*- coding: utf-8 -*-
"""
Acceso a MEDIA_ROOT con URLs firmadas (imágenes) y validación de uploads.

Las URLs firmadas no llevan Bearer: el navegador las usa en <img src>.
El token incluye schema_name + path relativo y caduca en minutos.
"""
from __future__ import annotations

import logging
import mimetypes
import os
import uuid
from typing import Optional

from django.conf import settings
from django.core import signing
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import FileResponse, Http404, HttpResponse
from django.utils._os import safe_join
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)

_SALT = 'jr-media-v1'
_MAX_AGE_SECONDS = int(getattr(settings, 'SIGNED_MEDIA_MAX_AGE', 300))

ALLOWED_IMAGE_EXTENSIONS = frozenset({
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tif', '.tiff',
})
ALLOWED_DOCUMENT_EXTENSIONS = frozenset({
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.txt', '.rtf',
}) | ALLOWED_IMAGE_EXTENSIONS

ACTIVE_CONTENT_EXTENSIONS = frozenset({
    '.html', '.htm', '.xhtml', '.svg', '.xml', '.js', '.mjs', '.css',
    '.php', '.asp', '.aspx', '.jsp', '.cgi', '.exe', '.sh', '.bat',
})

ACTIVE_CONTENT_TYPES = frozenset({
    'text/html',
    'application/xhtml+xml',
    'image/svg+xml',
    'text/xml',
    'application/xml',
    'application/javascript',
    'text/javascript',
})


def current_schema_name() -> str:
    from django.db import connection

    return getattr(connection, 'schema_name', None) or ''


def media_relative_name(file_field_or_name) -> Optional[str]:
    if file_field_or_name is None:
        return None
    name = getattr(file_field_or_name, 'name', None) or file_field_or_name
    if not name:
        return None
    return str(name).lstrip('/')


def resolve_safe_media_path(relative_name: str) -> str:
    """Abs path under MEDIA_ROOT or raise Http404 / ValueError."""
    relative_name = (relative_name or '').replace('\\', '/').lstrip('/')
    if not relative_name or '..' in relative_name.split('/'):
        raise Http404('Not found')
    try:
        full = safe_join(str(settings.MEDIA_ROOT), relative_name)
    except ValueError as exc:
        raise Http404('Not found') from exc
    if not os.path.isfile(full):
        raise Http404('Not found')
    return full


def sign_media_path(relative_name: str, schema_name: Optional[str] = None) -> str:
    schema = schema_name or current_schema_name()
    if not schema:
        raise ValueError('Cannot sign media without a tenant schema.')
    rel = media_relative_name(relative_name)
    if not rel:
        raise ValueError('Empty media path.')
    payload = {'s': schema, 'p': rel}
    return signing.dumps(payload, salt=_SALT)


def unsign_media_token(token: str) -> tuple[str, str]:
    data = signing.loads(token, salt=_SALT, max_age=_MAX_AGE_SECONDS)
    schema = data.get('s')
    path = data.get('p')
    if not schema or not path:
        raise signing.BadSignature('Incomplete media token.')
    return str(schema), str(path)


def build_signed_media_url(request, file_field_or_name) -> Optional[str]:
    """URL absoluta firmada para <img>/fetch sin Bearer."""
    rel = media_relative_name(file_field_or_name)
    if not rel:
        return None
    try:
        token = sign_media_path(rel)
    except ValueError:
        return None
    path = f'/media/s/{token}/'
    if request is not None:
        return request.build_absolute_uri(path)
    return path


def _guess_content_type(full_path: str) -> str:
    ctype, _encoding = mimetypes.guess_type(full_path)
    return ctype or 'application/octet-stream'


def _reject_active_content(full_path: str, content_type: str) -> None:
    ext = os.path.splitext(full_path)[1].lower()
    if ext in ACTIVE_CONTENT_EXTENSIONS:
        raise Http404('Not found')
    base = (content_type or '').split(';', 1)[0].strip().lower()
    if base in ACTIVE_CONTENT_TYPES:
        raise Http404('Not found')


@require_GET
def serve_signed_media(request, token: str):
    """
    Sirve un archivo bajo MEDIA_ROOT si el token es válido para el schema activo.
    Sin autenticación JWT: la firma es la credencial (vida corta).
    """
    try:
        schema, relative = unsign_media_token(token)
    except signing.SignatureExpired:
        return HttpResponse('Gone', status=410)
    except (signing.BadSignature, TypeError, ValueError):
        raise Http404('Not found') from None

    active = current_schema_name()
    if not active or schema != active:
        raise Http404('Not found')

    full_path = resolve_safe_media_path(relative)
    content_type = _guess_content_type(full_path)
    _reject_active_content(full_path, content_type)

    response = FileResponse(open(full_path, 'rb'), content_type=content_type)
    response['X-Content-Type-Options'] = 'nosniff'
    response['Cache-Control'] = 'private, max-age=60'
    return response


def validate_upload_file(uploaded_file, *, images_only: bool = False) -> None:
    """
    Rechaza HTML/SVG/XML y contenido activo.
    Si images_only, exige que Pillow abra un mapa de bits.
    """
    if uploaded_file is None:
        raise ValidationError('No file provided.')

    name = getattr(uploaded_file, 'name', '') or ''
    ext = os.path.splitext(name)[1].lower()
    content_type = (getattr(uploaded_file, 'content_type', None) or '').split(';', 1)[0].strip().lower()

    if ext in ACTIVE_CONTENT_EXTENSIONS or content_type in ACTIVE_CONTENT_TYPES:
        raise ValidationError('This file type is not allowed.')

    if images_only:
        if ext and ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError('Only bitmap images are allowed.')
        try:
            from PIL import Image
        except ImportError as exc:
            raise ValidationError('Image validation unavailable.') from exc
        try:
            uploaded_file.seek(0)
            with Image.open(uploaded_file) as img:
                img.verify()
            uploaded_file.seek(0)
            with Image.open(uploaded_file) as img:
                img.load()
            uploaded_file.seek(0)
        except Exception as exc:
            raise ValidationError('File is not a valid bitmap image.') from exc
        return

    if ext and ext not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError('This file type is not allowed.')
    if ext in ALLOWED_IMAGE_EXTENSIONS or content_type.startswith('image/'):
        validate_upload_file(uploaded_file, images_only=True)


def uuid_upload_filename(filename: str) -> str:
    ext = os.path.splitext(filename or '')[1].lower()
    if ext in ACTIVE_CONTENT_EXTENSIONS:
        ext = ''
    if ext and ext not in (ALLOWED_DOCUMENT_EXTENSIONS | ALLOWED_IMAGE_EXTENSIONS):
        ext = ''
    return f'{uuid.uuid4().hex}{ext}'


def event_image_upload_to(instance, filename: str) -> str:
    name = uuid_upload_filename(filename)
    if instance.work_account_id:
        subdir = f'event_images/work_account_{instance.work_account_id}'
    elif instance.event_id:
        subdir = f'event_images/event_{instance.event_id}'
    else:
        subdir = 'event_images/unassigned'
    full_dir = os.path.join(settings.MEDIA_ROOT, subdir)
    os.makedirs(full_dir, exist_ok=True)
    return f'{subdir}/{name}'


def contract_file_upload_to(instance, filename: str) -> str:
    name = uuid_upload_filename(filename)
    subdir = 'contract'
    full_dir = os.path.join(settings.MEDIA_ROOT, subdir)
    os.makedirs(full_dir, exist_ok=True)
    return f'{subdir}/{name}'


def product_image_upload_to_secure(instance, filename: str) -> str:
    name = uuid_upload_filename(filename)
    product_id = instance.product_id if instance.product_id else 'unknown'
    subdir = f'products/{product_id}'
    full_dir = os.path.join(settings.MEDIA_ROOT, subdir)
    os.makedirs(full_dir, exist_ok=True)
    return f'{subdir}/{name}'


def tenant_logo_upload_to(instance, filename: str) -> str:
    name = uuid_upload_filename(filename)
    subdir = 'tenant_logos'
    full_dir = os.path.join(settings.MEDIA_ROOT, subdir)
    os.makedirs(full_dir, exist_ok=True)
    return f'{subdir}/{name}'


def attachment_file_response(full_path: str, download_name: Optional[str] = None) -> FileResponse:
    content_type = _guess_content_type(full_path)
    _reject_active_content(full_path, content_type)
    filename = download_name or os.path.basename(full_path)
    response = FileResponse(
        open(full_path, 'rb'),
        as_attachment=True,
        filename=filename,
        content_type=content_type,
    )
    response['X-Content-Type-Options'] = 'nosniff'
    response['Cache-Control'] = 'private, no-store'
    return response
