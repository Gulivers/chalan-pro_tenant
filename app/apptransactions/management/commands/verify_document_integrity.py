from django.core.management.base import BaseCommand
from django.db import transaction
from apptransactions.models import Document, WorkAccount, Builder


class Command(BaseCommand):
    help = 'Verificar y limpiar referencias rotas en documentos OAHP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Corregir automáticamente las referencias rotas',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar problemas sin corregirlos',
        )

    def handle(self, *args, **options):
        fix = options['fix']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Solo mostrando problemas'))
        
        problems_found = 0
        problems_fixed = 0
        
        # Verificar documentos con work_accounts que no existen
        self.stdout.write('Verificando documentos con work_accounts...')
        docs_with_broken_work_accounts = Document.objects.filter(
            work_account__isnull=False
        ).exclude(
            work_account__in=WorkAccount.objects.all()
        )
        
        for doc in docs_with_broken_work_accounts:
            problems_found += 1
            self.stdout.write(
                self.style.ERROR(
                    f'Documento {doc.id}: work_account_id={doc.work_account_id} no existe'
                )
            )
            
            if fix and not dry_run:
                with transaction.atomic():
                    doc.work_account = None
                    doc.save()
                    problems_fixed += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  -> Corregido: work_account establecido a null')
                    )
        
        # Verificar documentos con builders que no existen
        self.stdout.write('Verificando documentos con builders...')
        docs_with_broken_builders = Document.objects.filter(
            builder__isnull=False
        ).exclude(
            builder__in=Builder.objects.all()
        )
        
        for doc in docs_with_broken_builders:
            problems_found += 1
            self.stdout.write(
                self.style.ERROR(
                    f'Documento {doc.id}: builder_id={doc.builder_id} no existe'
                )
            )
            
            if fix and not dry_run:
                with transaction.atomic():
                    doc.builder = None
                    doc.save()
                    problems_fixed += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  -> Corregido: builder establecido a null')
                    )
        
        # Resumen
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Problemas encontrados: {problems_found}')
        
        if fix and not dry_run:
            self.stdout.write(f'Problemas corregidos: {problems_fixed}')
            if problems_fixed > 0:
                self.stdout.write(
                    self.style.SUCCESS('✅ Datos corregidos exitosamente')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ No se encontraron problemas para corregir')
                )
        elif dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️ Modo dry-run: no se realizaron cambios')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️ Use --fix para corregir automáticamente')
            )
