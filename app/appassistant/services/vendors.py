"""
Vendor (Builder) resolution for Assistant spend tools.

Primary match: Builder.name (case-insensitive).
Fallback: Builder.party.name when a Party is linked.
Documents use Document.builder.

If more than one Builder matches, raise AmbiguousVendorError with candidates
(id + name). Never pick silently.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.db.models import Q

from ctrctsapp.models import Builder


@dataclass(frozen=True)
class VendorCandidate:
    id: int
    name: str


class VendorNotFoundError(Exception):
    def __init__(self, message: str = 'Vendor not found.'):
        self.message = message
        super().__init__(message)


class AmbiguousVendorError(Exception):
    def __init__(self, candidates: list[VendorCandidate], message: str | None = None):
        self.candidates = candidates
        self.message = message or (
            'Multiple vendors match. Please clarify which vendor you mean.'
        )
        super().__init__(self.message)


def _candidate(builder: Builder) -> VendorCandidate:
    return VendorCandidate(id=builder.pk, name=builder.name or f'Builder #{builder.pk}')


def _unique_builders(qs) -> list[Builder]:
    seen: set[int] = set()
    out: list[Builder] = []
    for builder in qs.order_by('name', 'id'):
        if builder.pk in seen:
            continue
        seen.add(builder.pk)
        out.append(builder)
    return out


def resolve_vendor(
    *,
    name: str | None = None,
    vendor_id: int | None = None,
) -> Builder:
    """
    Resolve a single Builder in the current tenant schema.

    - vendor_id: exact pk lookup (tenant-scoped by schema).
    - name: iexact on Builder.name, then icontains on Builder.name,
      then iexact/icontains on party.name.
    """
    if vendor_id is not None:
        try:
            return Builder.objects.select_related('party').get(pk=vendor_id)
        except Builder.DoesNotExist as exc:
            raise VendorNotFoundError(f'Vendor id={vendor_id} not found.') from exc

    if not name or not str(name).strip():
        raise VendorNotFoundError('Vendor name or vendor_id is required.')

    needle = str(name).strip()
    base = Builder.objects.select_related('party')

    # 1) Exact name (case-insensitive)
    exact = _unique_builders(base.filter(name__iexact=needle))
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        raise AmbiguousVendorError([_candidate(b) for b in exact])

    # 2) Partial name
    partial = _unique_builders(base.filter(name__icontains=needle))
    if len(partial) == 1:
        return partial[0]
    if len(partial) > 1:
        raise AmbiguousVendorError([_candidate(b) for b in partial])

    # 3) Fallback: Party.name exact then partial
    party_exact = _unique_builders(
        base.filter(party__isnull=False).filter(party__name__iexact=needle)
    )
    if len(party_exact) == 1:
        return party_exact[0]
    if len(party_exact) > 1:
        raise AmbiguousVendorError([_candidate(b) for b in party_exact])

    party_partial = _unique_builders(
        base.filter(party__isnull=False).filter(party__name__icontains=needle)
    )
    if len(party_partial) == 1:
        return party_partial[0]
    if len(party_partial) > 1:
        raise AmbiguousVendorError([_candidate(b) for b in party_partial])

    raise VendorNotFoundError(f'No vendor matches "{needle}".')


def filter_builders_by_name(name: str):
    """Return Builder queryset matching name or party.name (for diagnostics)."""
    needle = (name or '').strip()
    if not needle:
        return Builder.objects.none()
    return Builder.objects.filter(
        Q(name__icontains=needle)
        | Q(party__isnull=False, party__name__icontains=needle)
    ).distinct()
