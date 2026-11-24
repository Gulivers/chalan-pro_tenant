"""
Async PDF jobs without Celery: Redis status + daemon thread + media file.

Requires REDIS_URL (also used by Channels). Poll GET returns the same
{file, filename, file_type} contract when status=ready.

Builders are callables:
  builder(*builder_args, request, logo_url=...) -> (pdf_bytes, filename)
"""
from __future__ import annotations

import json
import logging
import os
import threading
import uuid
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Optional, Sequence

from django.conf import settings
from django.db import connection
from django_tenants.utils import schema_context

logger = logging.getLogger(__name__)

JOB_TTL_SECONDS = 600
REDIS_KEY_PREFIX = 'jr:pdfjob:'


class PdfJobError(Exception):
    pass


def _redis_client():
    url = getattr(settings, 'REDIS_URL', None) or os.environ.get('REDIS_URL')
    if not url:
        raise PdfJobError('REDIS_URL is not configured; cannot run async PDF jobs.')
    try:
        import redis
    except ImportError as exc:
        raise PdfJobError('redis package is not installed') from exc
    return redis.Redis.from_url(url, decode_responses=True)


def _job_key(job_id: str) -> str:
    return f'{REDIS_KEY_PREFIX}{job_id}'


def _media_job_path(job_id: str) -> Path:
    base = Path(settings.MEDIA_ROOT) / 'pdf_jobs'
    base.mkdir(parents=True, exist_ok=True)
    return base / f'{job_id}.pdf'


def _set_job(job_id: str, payload: dict[str, Any]) -> None:
    client = _redis_client()
    client.setex(_job_key(job_id), JOB_TTL_SECONDS, json.dumps(payload))


def get_job(job_id: str) -> Optional[dict[str, Any]]:
    client = _redis_client()
    raw = client.get(_job_key(job_id))
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _request_proxy(host: str, scheme: str = 'https'):
    """Minimal request stand-in for branding / absolute URLs in background threads."""

    def build_absolute_uri(location: str) -> str:
        if location.startswith('http://') or location.startswith('https://'):
            return location
        if not location.startswith('/'):
            location = '/' + location
        return f'{scheme}://{host}{location}'

    return SimpleNamespace(
        get_host=lambda: host,
        build_absolute_uri=build_absolute_uri,
        scheme=scheme,
        is_secure=lambda: scheme == 'https',
    )


def enqueue_pdf_job(
    *,
    schema_name: str,
    kind: str,
    host: str,
    scheme: str,
    logo_url: Optional[str],
    builder: Callable[..., tuple[bytes, str]],
    builder_args: Sequence[Any] = (),
    ref_id: Any = None,
) -> str:
    """
    Start a background PDF build.

    `builder(*builder_args, request, logo_url=...)` must return (pdf_bytes, filename).
    """
    job_id = str(uuid.uuid4())
    args_tuple = tuple(builder_args)
    _set_job(
        job_id,
        {
            'status': 'pending',
            'kind': kind,
            'ref_id': ref_id,
            'schema': schema_name,
        },
    )

    def _run():
        try:
            with schema_context(schema_name):
                proxy = _request_proxy(host, scheme)
                pdf_bytes, filename = builder(
                    *args_tuple,
                    proxy,
                    logo_url=logo_url,
                )
                path = _media_job_path(job_id)
                path.write_bytes(pdf_bytes)
                _set_job(
                    job_id,
                    {
                        'status': 'ready',
                        'kind': kind,
                        'ref_id': ref_id,
                        'schema': schema_name,
                        'filename': filename,
                        'path': str(path),
                    },
                )
        except Exception as exc:
            logger.exception(
                'PDF job failed job_id=%s kind=%s ref_id=%s',
                job_id,
                kind,
                ref_id,
            )
            try:
                _set_job(
                    job_id,
                    {
                        'status': 'error',
                        'kind': kind,
                        'ref_id': ref_id,
                        'schema': schema_name,
                        'detail': str(exc)[:500],
                    },
                )
            except Exception:
                logger.exception('Could not persist PDF job error state')
        finally:
            try:
                connection.close()
            except Exception:
                pass

    thread = threading.Thread(
        target=_run,
        name=f'pdf-job-{job_id[:8]}',
        daemon=True,
    )
    thread.start()
    return job_id


def job_result_payload(job: dict[str, Any]) -> dict[str, Any]:
    """Build API response for a job record (includes base64 file when ready)."""
    import base64

    status = job.get('status')
    out: dict[str, Any] = {'status': status, 'job_id': job.get('job_id')}
    if status == 'pending':
        return out
    if status == 'error':
        out['detail'] = job.get('detail') or 'PDF generation failed'
        return out
    if status == 'ready':
        path = job.get('path')
        if not path or not os.path.isfile(path):
            out['status'] = 'error'
            out['detail'] = 'PDF file missing'
            return out
        pdf_bytes = Path(path).read_bytes()
        out['file'] = base64.b64encode(pdf_bytes).decode('utf-8')
        out['filename'] = job.get('filename') or 'document.pdf'
        out['file_type'] = 'application/pdf'
        return out
    out['status'] = 'error'
    out['detail'] = f'Unknown job status: {status}'
    return out
