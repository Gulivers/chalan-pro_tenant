"""
Management command para configurar dominios para el schema public.
Este comando crea los dominios necesarios para acceder al admin global.
"""
from django.core.management.base import BaseCommand
from tenants.models import Tenant, Domain
from django_tenants.utils import get_public_schema_name


class Command(BaseCommand):
    help = 'Configura dominios para el schema public (admin global)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--domains',
            nargs='+',
            default=[
                'api.jobrhythm.net',
                'api.chalanpro.net',
                'www.jobrhythm.net',
                'jobrhythm.net',
                'chalanpro.net',
                'api.jobrithm.net',
                'www.jobrithm.net',
            ],
            help='Lista de dominios a configurar (default: API public JobRhythm + legacy chalanpro/jobrithm)',
        )

    def _ensure_public_tenant(self, public_schema: str) -> Tenant:
        tenant = Tenant.objects.filter(schema_name=public_schema).first()
        if tenant:
            return tenant
        tenant = Tenant(
            schema_name=public_schema,
            name='Public',
            tenant_id='public_001',
            on_trial=False,
            is_active=True,
        )
        tenant.auto_create_schema = False
        tenant.save()
        self.stdout.write(
            self.style.SUCCESS(f'✅ Tenant "{public_schema}" creado (id={tenant.pk})')
        )
        return tenant

    def handle(self, *args, **options):
        public_schema = get_public_schema_name()
        tenant = self._ensure_public_tenant(public_schema)
        
        domains = options['domains']
        primary_domain = domains[0] if domains else 'api.jobrhythm.net'
        
        self.stdout.write(
            self.style.SUCCESS(f'📋 Configurando dominios para schema "{public_schema}" (tenant: {tenant.name})')
        )
        self.stdout.write('')
        
        created_count = 0
        existing_count = 0
        
        for i, domain_name in enumerate(domains):
            is_primary = (domain_name == primary_domain)
            
            domain, created = Domain.objects.get_or_create(
                domain=domain_name,
                defaults={
                    'tenant': tenant,
                    'is_primary': is_primary
                }
            )
            
            # Si el dominio ya existía pero no estaba asociado al tenant correcto, actualizarlo
            if not created and domain.tenant != tenant:
                domain.tenant = tenant
                domain.is_primary = is_primary
                domain.save()
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  {domain_name}: Actualizado (estaba asociado a otro tenant)')
                )
            elif created:
                created_count += 1
                status_icon = '⭐' if is_primary else '  '
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ {status_icon} {domain_name}: Creado (primary: {is_primary})')
                )
            else:
                existing_count += 1
                status_icon = '⭐' if is_primary else '  '
                self.stdout.write(
                    self.style.SUCCESS(f'  ℹ️  {status_icon} {domain_name}: Ya existía (primary: {is_primary})')
                )
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'📊 Resumen: {created_count} creados, {existing_count} ya existían')
        )
        self.stdout.write('')
        
        # Mostrar todos los dominios del schema public
        all_domains = Domain.objects.filter(tenant=tenant).order_by('-is_primary', 'domain')
        if all_domains.exists():
            self.stdout.write(self.style.SUCCESS('🌐 Dominios configurados para schema public:'))
            for d in all_domains:
                primary_marker = '⭐ (PRIMARY)' if d.is_primary else ''
                self.stdout.write(f'   - {d.domain} {primary_marker}')
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  No se encontraron dominios configurados')
            )

