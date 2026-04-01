#!/usr/bin/env python3
import argparse
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from django.db import transaction
from tenants.models import Domain


def swap_suffix(host: str, old_base: str, new_base: str):
    if host == old_base:
        return new_base
    if host.endswith("." + old_base):
        return host[: -(len(old_base))] + new_base
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-base", default="chalanpro.net")
    parser.add_argument("--new-base", default="jobrithm.net")
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--keep-old-primary", action="store_true")
    args = parser.parse_args()

    query = Domain.objects.select_related("tenant").all().order_by(
        "tenant_id", "-is_primary", "domain"
    )
    actions = []
    for domain_obj in query:
        new_domain = swap_suffix(domain_obj.domain, args.old_base, args.new_base)
        if not new_domain:
            continue
        exists = Domain.objects.filter(domain=new_domain).exists()
        actions.append(
            (
                domain_obj.id,
                domain_obj.tenant_id,
                domain_obj.domain,
                new_domain,
                domain_obj.is_primary,
                exists,
            )
        )

    print(
        f"Encontrados {len(actions)} dominios convertibles de "
        f"{args.old_base} -> {args.new_base}"
    )
    for action in actions:
        print(
            f"tenant={action[1]} | old={action[2]} | new={action[3]} | "
            f"primary_old={action[4]} | new_exists={action[5]}"
        )

    if not args.commit:
        print("\nDRY-RUN. Sin cambios. Usa --commit para aplicar.")
        return

    with transaction.atomic():
        for _, tenant_id, old_domain, new_domain, old_is_primary, exists in actions:
            if not exists:
                Domain.objects.create(
                    tenant_id=tenant_id,
                    domain=new_domain,
                    is_primary=(old_is_primary and not args.keep_old_primary),
                )
            if old_is_primary and not args.keep_old_primary:
                Domain.objects.filter(tenant_id=tenant_id, domain=old_domain).update(
                    is_primary=False
                )

    print("Cambios aplicados correctamente.")


if __name__ == "__main__":
    main()
