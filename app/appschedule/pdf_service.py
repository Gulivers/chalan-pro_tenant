"""WeasyPrint builders for schedule PDF reports."""
from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from typing import Optional

from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration

from appauth.services.tenant import resolve_request_tenant
from utils.tenant_branding import get_tenant_logo_url

from .models import Crew, Event


def build_schedule_pdf(
    start_at: str,
    end_at: str,
    request=None,
    *,
    logo_url: Optional[str] = None,
) -> tuple[bytes, str]:
    """
    Return (pdf_bytes, filename) for a schedule date range.
    `start_at` / `end_at` are ISO date strings (end exclusive, same as sync API).
    """
    if not start_at or not end_at:
        raise ValueError('start_at and end_at are required')

    start_date = parse_date(start_at)
    end_date = parse_date(end_at)
    if not start_date or not end_date:
        raise ValueError('Invalid start_at or end_at')

    days = []
    current = start_date
    while current < end_date:
        days.append(current)
        current += timedelta(days=1)

    q = Q()
    q &= (
        Q(date__lte=start_date, end_dt__gte=start_date)
        | Q(date__gte=start_date, date__lt=end_date)
        | Q(date__lte=start_date, end_dt__lt=end_date)
    )
    q &= (
        Q(date__lte=end_date, end_dt__gte=end_date)
        | Q(date__gte=start_date, date__lte=end_date)
        | Q(end_dt__gte=start_date, end_dt__lte=end_date)
    )

    events = Event.objects.select_related(
        'crew', 'crew__category', 'absence_reason'
    ).filter(q, deleted=False)

    tenant = resolve_request_tenant(request) if request is not None else None
    # When called from a job thread, connection.tenant is already set via schema_context
    if tenant is None:
        from django.db import connection

        tenant = getattr(connection, 'tenant', None)

    show_crew_resources = (
        bool(getattr(tenant, 'schedule_show_crew_resources', True))
        if tenant is not None
        else True
    )

    if logo_url is None and request is not None:
        logo_url = get_tenant_logo_url(request)

    date_range = (
        f"{start_date.strftime('%b %d')} – "
        f"{(end_date - timedelta(days=1)).strftime('%b %d, %Y')}"
    )

    if show_crew_resources:
        all_crews = Crew.objects.select_related('category').filter(status=True)
        categorized_events = defaultdict(
            lambda: defaultdict(lambda: defaultdict(list))
        )

        for crew in all_crews:
            if crew.category:
                categorized_events[crew.category.name][crew.name]

        for event in events:
            if not event.crew or not event.crew.category:
                continue

            crew_name = event.crew.name
            category_name = event.crew.category.name
            current = event.date
            while current < event.end_dt:
                if start_date <= current <= end_date:
                    if event.is_absence and event.absence_reason:
                        absence_text = f"🛑 Absence: {event.absence_reason.name}"
                        if event.description:
                            absence_text += f" – {event.description}"
                        categorized_events[category_name][crew_name][current].append(
                            absence_text
                        )
                    else:
                        if current == event.date:
                            categorized_events[category_name][crew_name][current].append(
                                event
                            )
                        else:
                            categorized_events[category_name][crew_name][current].append(
                                "Finishing up work"
                            )
                current += timedelta(days=1)

        categorized_events_clean = {
            cat: {
                crew: dict(day_map)
                for crew, day_map in crews.items()
            }
            for cat, crews in categorized_events.items()
        }
        template_name = 'schedule_pdf.html'
        context = {
            'categorized_events': categorized_events_clean,
            'date_range': date_range,
            'days': days,
            'logo_url': logo_url,
        }
    else:
        categorized_by_day = defaultdict(lambda: defaultdict(list))
        category_order = []

        all_crews = Crew.objects.select_related('category').filter(status=True)
        for crew in all_crews:
            if crew.category and crew.category.name not in category_order:
                category_order.append(crew.category.name)
                categorized_by_day[crew.category.name]

        for event in events:
            if not event.crew or not event.crew.category:
                continue

            crew_name = event.crew.name
            category_name = event.crew.category.name
            if category_name not in category_order:
                category_order.append(category_name)

            current = event.date
            while current < event.end_dt:
                if start_date <= current <= end_date:
                    if event.is_absence and event.absence_reason:
                        absence_text = f"🛑 Absence: {event.absence_reason.name}"
                        if event.description:
                            absence_text += f" – {event.description}"
                        categorized_by_day[category_name][current].append({
                            'crew_name': crew_name,
                            'kind': 'absence',
                            'text': absence_text,
                        })
                    elif current == event.date:
                        categorized_by_day[category_name][current].append({
                            'crew_name': crew_name,
                            'kind': 'event',
                            'title': event.title,
                            'description': event.description or '',
                            'extended_service': bool(event.extended_service),
                        })
                    else:
                        categorized_by_day[category_name][current].append({
                            'crew_name': crew_name,
                            'kind': 'finishing',
                            'text': 'Finishing up work',
                        })
                current += timedelta(days=1)

        categorized_events_clean = {
            cat: dict(categorized_by_day[cat])
            for cat in category_order
        }
        template_name = 'schedule_pdf_no_crew.html'
        context = {
            'categorized_events': categorized_events_clean,
            'date_range': date_range,
            'days': days,
            'logo_url': logo_url,
        }

    html = render_to_string(template_name, context)
    pdf_bytes = HTML(string=html).write_pdf(font_config=FontConfiguration())
    filename = f'schedule_{start_at}_to_{end_at}.pdf'
    return pdf_bytes, filename
