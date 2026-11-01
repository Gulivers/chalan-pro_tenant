from django.db import models
from django.db.models import ProtectedError, Q, UniqueConstraint
from django.contrib.auth.models import User
from crewsapp.models import Crew, Category
from ctrctsapp.models import Builder, HouseModel, Job
from django.utils import timezone    #OAHP
from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError
import os

    
class AbsenceReason(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Absence Reasons"
        verbose_name_plural = "Absence Reasons"
        # ordering = ['-date', 'title']


class Event(models.Model):
    """
    A model representing an event with details related to a construction job.
    """
    date = models.DateField()
    end_dt = models.DateField()
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE, verbose_name='Crew')
    # WorkAccount es el nuevo campo principal para identificar la obra
    work_account = models.ForeignKey('apptransactions.WorkAccount', on_delete=models.PROTECT, null=True, blank=True, related_name='events')
    # Campos legacy mantenidos por compatibilidad (se sincronizan desde work_account)
    builder = models.ForeignKey(Builder, on_delete=models.CASCADE, related_query_name='events', blank=True, null=True)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, related_query_name='events', blank=True, null=True)
    house_model = models.ForeignKey(HouseModel, on_delete=models.SET_NULL, related_query_name='events', blank=True, null=True)
    lot = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    extended_service = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_absence = models.BooleanField(default=False)
    absence_reason = models.ForeignKey(AbsenceReason, null=True, blank=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title or f"Event #{self.id}"

    def get_deletion_blockers(self):
        """
        Return related records that prevent deleting this event.
        Covers chat, notes, folder (images), and contracts.
        """
        blockers = []

        note = getattr(self, 'note', None)
        if note and (note.notes or "").strip():
            blockers.append(note)

        chat = self.chat_messages.first()
        if chat:
            blockers.append(chat)

        image = self.images.first()
        if image:
            blockers.append(image)

        contracts = getattr(self, 'contracts', None)
        contract = contracts.first() if contracts is not None else None
        if contract:
            blockers.append(contract)

        return blockers

    def raise_if_deletion_blocked(self):
        blockers = self.get_deletion_blockers()
        if blockers:
            raise ProtectedError(
                "Cannot delete event while related records exist.",
                set(blockers),
            )

    def delete(self, *args, **kwargs):
        self.raise_if_deletion_blocked()
        return super().delete(*args, **kwargs)
    
    def clean(self):
        if self.is_absence:
            return

        if not self.lot and not self.address:
            raise ValidationError("Address or lot/job must be provided")

        category = self.crew.category if self.crew else None
        if not category:
            raise ValidationError("Crew category is required")

        qs_ed = EventDraft.objects.filter(crew__category=category)
        qs_e = Event.objects.filter(crew__category=category, deleted=False)

        if self.lot:
            qs_ed = qs_ed.filter(job=self.job, lot=self.lot)
            qs_e = qs_e.filter(job=self.job, lot=self.lot)
        elif self.address:
            qs_ed = qs_ed.filter(address=self.address)
            qs_e = qs_e.filter(address=self.address)

        if self.pk:
            qs_e = qs_e.exclude(pk=self.pk)
        qs_ed = qs_ed.exclude(event_id=self.pk)

        if qs_ed.exists() or qs_e.exists():
            raise ValidationError("Duplicate Event Detected")

    def save(self, *args, **kwargs):
        # Sincronizar campos desde work_account si está presente
        if self.work_account and not self.is_absence:
            self.builder = self.work_account.builder
            self.job = self.work_account.job
            self.house_model = self.work_account.house_model
            self.lot = self.work_account.lot
            self.address = self.work_account.address
            # Sincronizar título desde work_account.title si no es ausencia
            if not self.title or not self.title.strip():
                self.title = self.work_account.title
        
        if self.title:
            self.title = self.title.upper()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        constraints = [
            models.UniqueConstraint(
                fields=['crew', 'date', 'title'],
                name='uniq_event_crew_date_title'
            )
        ]
        indexes = [
            models.Index(fields=['date', 'end_dt']),
            models.Index(fields=['work_account', 'is_absence']),
        ]
        # ordering = ['-date', 'title']
        # Constraint está definido para PostgreSQL 😏
        #constraints = [
        #    models.UniqueConstraint(
        #        fields=['crew', 'job', 'lot'],
        #        condition=models.Q(lot__isnull=False),
        #        name='unique_event_crew_job_lot'
        #    ),
        #    models.UniqueConstraint(
        #        fields=['crew', 'job', 'address'],
        #        condition=models.Q(lot__isnull=True, address__isnull=False),
        #        name='unique_event_crew_job_address'
        #    ),
        #]


class EventDraft(models.Model):
    """
    A model representing an event draft with details related to a construction job.
    """
    event = models.OneToOneField(Event, on_delete=models.CASCADE, verbose_name='events_draft', null=True, blank=True)
    date = models.DateField()
    end_dt = models.DateField()
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE, related_query_name='drafts')
    # WorkAccount es el nuevo campo principal para identificar la obra
    work_account = models.ForeignKey('apptransactions.WorkAccount', on_delete=models.PROTECT, null=True, blank=True, related_name='event_drafts')
    # Campos legacy mantenidos por compatibilidad (se sincronizan desde work_account)
    builder = models.ForeignKey(Builder, on_delete=models.CASCADE, related_query_name='drafts', blank=True, null=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_query_name='drafts', blank=True, null=True)
    house_model = models.ForeignKey(HouseModel, on_delete=models.CASCADE, related_query_name='drafts', blank=True, null=True)
    lot = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    extended_service = models.BooleanField(default=False)
    is_absence = models.BooleanField(default=False)
    absence_reason = models.ForeignKey(AbsenceReason, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title
    
    def clean(self):
        if self.is_absence:
            return

        if not self.lot and not self.address:
            raise ValidationError("Address or lot/job must be provided")

        category = self.crew.category if self.crew else None
        if not category:
            raise ValidationError("Crew category is required")

        qs_ed = EventDraft.objects.filter(crew__category=category)
        qs_e = Event.objects.filter(crew__category=category, deleted=False)

        if self.lot:
            qs_ed = qs_ed.filter(job=self.job, lot=self.lot)
            qs_e = qs_e.filter(job=self.job, lot=self.lot)
        elif self.address:
            qs_ed = qs_ed.filter(address=self.address)
            qs_e = qs_e.filter(address=self.address)

        if self.pk:
            qs_ed = qs_ed.exclude(pk=self.pk)
        if self.event_id:
            qs_e = qs_e.exclude(pk=self.event_id)

        if qs_ed.exists() or qs_e.exists():
            raise ValidationError("Duplicate Event Detected")

    def save(self, *args, **kwargs):
        # Sincronizar campos desde work_account si está presente
        if self.work_account and not self.is_absence:
            self.builder = self.work_account.builder
            self.job = self.work_account.job
            self.house_model = self.work_account.house_model
            self.lot = self.work_account.lot
            self.address = self.work_account.address
            # Sincronizar título desde work_account.title si no es ausencia
            if not self.title or not self.title.strip():
                self.title = self.work_account.title
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Event Draft"
        verbose_name_plural = "Events Draft"
        indexes = [
            models.Index(fields=['date', 'end_dt']),
            models.Index(fields=['work_account', 'is_absence']),
        ]
        # ordering = ['-date', 'title']
        # Constraint está definido para PostgreSQL 😏
        #constraints = [
        #    models.UniqueConstraint(
        #        fields=['crew', 'job', 'lot'],
        #        condition=models.Q(lot__isnull=False),
        #        name='unique_eventdraft_crew_job_lot'
        #    ),
        #    models.UniqueConstraint(
        #        fields=['crew', 'job', 'address'],
        #        condition=models.Q(lot__isnull=True, address__isnull=False),
        #        name='unique_eventdraft_crew_job_address'
        #    ),
        #]


class EventNote(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, verbose_name='event_note', related_name='note', null=True, blank=True)
    # Denormalized reference to the work account (same pattern as chat). Notes are scoped by event.
    work_account = models.ForeignKey('apptransactions.WorkAccount', on_delete=models.CASCADE, verbose_name='work_account_note', related_name='event_notes', null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        if self.notes:
            clean = self.notes.replace('<p>', '').replace('</p>', ' ').strip()
            return f"Note: {clean[:40]}" if clean else "Note"
        return "Note"


class EventChatMessage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name='chat_messages', null=True, blank=True)
    # WorkAccount es el campo principal para identificar los mensajes de chat globales por obra
    work_account = models.ForeignKey('apptransactions.WorkAccount', on_delete=models.PROTECT, related_name='work_account_chat_messages', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}: {self.message[:50]}"
    
    class Meta:
        # Asegurar que haya al menos event o work_account
        constraints = [
            models.CheckConstraint(
                check=Q(event__isnull=False) | Q(work_account__isnull=False),
                name='event_chat_message_requires_event_or_work_account'
            )
        ]


class EventChatReadStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey('EventChatMessage', on_delete=models.CASCADE, related_name='read_statuses', null=False)
    read_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'message')
        verbose_name = "Event Chat Read Status"
        verbose_name_plural = "Event Chat Read Statuses"

    def __str__(self):
        return f"{self.user.username} read message {self.message.id} at {self.read_at}"


@deconstructible
class EventImageUploadTo:
    def __call__(self, instance, filename):
        from django.conf import settings
        # Guarda en: event_images/<work_account_id o event_id o 'unassigned'>/filename
        if instance.work_account_id:
            work_account_id = instance.work_account_id
            base, ext = os.path.splitext(filename)
            subdir = f'event_images/work_account_{work_account_id}'
        elif instance.event_id:
            event_id = instance.event_id
            base, ext = os.path.splitext(filename)
            subdir = f'event_images/event_{event_id}'
        else:
            base, ext = os.path.splitext(filename)
            subdir = f'event_images/unassigned'
        
        # Crear el directorio si no existe
        full_path = os.path.join(settings.MEDIA_ROOT, subdir)
        os.makedirs(full_path, exist_ok=True)
        
        return f'{subdir}/{base}{ext}'

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name='images', null=True, blank=True)
    # WorkAccount es el campo principal para identificar las imágenes globales por obra
    work_account = models.ForeignKey('apptransactions.WorkAccount', on_delete=models.PROTECT, related_name='images', null=True, blank=True)
    image = models.ImageField(upload_to=EventImageUploadTo())
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        if self.work_account_id:
            return f"Image for WorkAccount {self.work_account_id} ({self.id})"
        return f"Image for Event {self.event_id} ({self.id})"
    
    class Meta:
        # Asegurar que haya al menos event o work_account
        constraints = [
            models.CheckConstraint(
                check=Q(event__isnull=False) | Q(work_account__isnull=False),
                name='event_image_requires_event_or_work_account'
            )
        ]


# ---------------------------------------------------------------------------
# Work Order Status & Progress (tenant-scoped catalog + per-Event tracking)
# ---------------------------------------------------------------------------


class WorkOrderStatus(models.Model):
    """
    Single catalog of Work Order statuses per tenant (not per crew category).

    Operative users change Event tracking via the API; only admins maintain
    this catalog (Django Admin / catalog endpoints).
    """

    code = models.CharField(max_length=64)
    name = models.CharField(max_length=120)
    sequence = models.PositiveIntegerField()
    is_initial = models.BooleanField(
        default=False,
        help_text='Assigned automatically when a Work Order is published.',
    )
    is_terminal = models.BooleanField(
        default=False,
        help_text='Marks the Work Order as completed (e.g. Passed & Closed).',
    )
    requires_inspection_ready = models.BooleanField(
        default=False,
        help_text=(
            'Entering this status requires all progress items marked '
            'required for inspection to be completed.'
        ),
    )
    requires_completion_ready = models.BooleanField(
        default=False,
        help_text=(
            'Entering this status requires all progress items marked '
            'required for completion to be completed.'
        ),
    )
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['sequence', 'id']
        verbose_name = 'Work Order Status'
        verbose_name_plural = 'Work Order Statuses'
        constraints = [
            UniqueConstraint(fields=['code'], name='uniq_work_order_status_code'),
            UniqueConstraint(fields=['sequence'], name='uniq_work_order_status_sequence'),
        ]

    def __str__(self):
        return f'{self.sequence}. {self.name}'

    def _is_referenced(self):
        if not self.pk:
            return False
        return (
            self.current_work_orders.exists()
            or self.history_from.exists()
            or self.history_to.exists()
        )

    def clean(self):
        super().clean()
        if self.is_initial:
            qs = WorkOrderStatus.objects.filter(is_initial=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({
                    'is_initial': 'Only one initial Work Order status is allowed.',
                })
        if self.pk:
            previous = WorkOrderStatus.objects.filter(pk=self.pk).first()
            if (
                previous is not None
                and previous.code != self.code
                and self._is_referenced()
            ):
                raise ValidationError({
                    'code': (
                        'This status is already referenced and its code cannot '
                        'be changed. Deactivate it instead.'
                    ),
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self._is_referenced():
            raise ProtectedError(
                'This status is referenced by Work Orders or history and cannot '
                'be deleted. Set is_active=False instead.',
                {self},
            )
        return super().delete(*args, **kwargs)


class WorkOrderTracking(models.Model):
    """Current operative status of a published Work Order (Event)."""

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name='work_order_tracking',
    )
    current_status = models.ForeignKey(
        WorkOrderStatus,
        on_delete=models.PROTECT,
        related_name='current_work_orders',
    )
    status_changed_at = models.DateTimeField(default=timezone.now)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_order_status_changes',
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Work Order Tracking'
        verbose_name_plural = 'Work Order Tracking'

    def __str__(self):
        return f'{self.event_id} → {self.current_status.code}'


class WorkOrderStatusHistory(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='work_order_status_history',
    )
    from_status = models.ForeignKey(
        WorkOrderStatus,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='history_from',
    )
    to_status = models.ForeignKey(
        WorkOrderStatus,
        on_delete=models.PROTECT,
        related_name='history_to',
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_order_status_history',
    )
    changed_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['changed_at', 'id']
        verbose_name = 'Work Order Status History'
        verbose_name_plural = 'Work Order Status History'

    def __str__(self):
        origin = self.from_status.code if self.from_status_id else '—'
        return f'{self.event_id} {origin} → {self.to_status.code}'


class WorkOrderProgressTemplate(models.Model):
    """
    Progress checklist template for a crew category (phase), or a general
    template when category is null.
    """

    name = models.CharField(max_length=120)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_order_progress_templates',
        help_text='Crew category this template applies to (e.g. Rough, Trim).',
    )
    is_active = models.BooleanField(default=True)
    is_expected_for_work_account = models.BooleanField(
        default=True,
        help_text=(
            'When True, Work Account rollup treats this phase as expected '
            'for project completion (even if no Work Order exists yet).'
        ),
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name', 'id']
        verbose_name = 'Work Order Progress Template'
        verbose_name_plural = 'Work Order Progress Templates'
        constraints = [
            UniqueConstraint(
                fields=['category'],
                condition=Q(category__isnull=False),
                name='uniq_wo_progress_template_category',
            ),
        ]

    def __str__(self):
        if self.category_id:
            return f'{self.name} ({self.category.name})'
        return self.name


class WorkOrderProgressItem(models.Model):
    """Configurable checkpoint definition inside a progress template."""

    template = models.ForeignKey(
        WorkOrderProgressTemplate,
        on_delete=models.CASCADE,
        related_name='items',
    )
    code = models.CharField(max_length=64)
    name = models.CharField(max_length=160)
    sequence = models.PositiveIntegerField()
    is_required_for_inspection = models.BooleanField(
        default=False,
        help_text='Must be completed before entering an inspection-ready status.',
    )
    is_required_for_completion = models.BooleanField(
        default=False,
        help_text='Must be completed before entering a completion/terminal status.',
    )
    is_informational = models.BooleanField(
        default=False,
        help_text='Shown for awareness only; never blocks transitions.',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['template', 'sequence', 'id']
        verbose_name = 'Work Order Progress Item'
        verbose_name_plural = 'Work Order Progress Items'
        constraints = [
            UniqueConstraint(
                fields=['template', 'code'],
                name='uniq_wo_progress_item_template_code',
            ),
            UniqueConstraint(
                fields=['template', 'sequence'],
                name='uniq_wo_progress_item_template_sequence',
            ),
        ]

    def __str__(self):
        return f'{self.template_id}:{self.code}'

    def clean(self):
        super().clean()
        if self.is_informational and (
            self.is_required_for_inspection or self.is_required_for_completion
        ):
            raise ValidationError({
                'is_informational': (
                    'Informational items cannot also be required for '
                    'inspection or completion.'
                ),
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class WorkOrderProgressCheck(models.Model):
    """Per-Work-Order instance of a progress checkpoint."""

    SOURCE_MANUAL = 'manual'
    SOURCE_TRANSACTION = 'transaction'
    SOURCE_CHOICES = (
        (SOURCE_MANUAL, 'Manual'),
        (SOURCE_TRANSACTION, 'Transaction'),
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='progress_checks',
    )
    item = models.ForeignKey(
        WorkOrderProgressItem,
        on_delete=models.PROTECT,
        related_name='checks',
    )
    is_done = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_order_progress_completions',
    )
    notes = models.TextField(blank=True)
    source = models.CharField(
        max_length=32,
        choices=SOURCE_CHOICES,
        default=SOURCE_MANUAL,
    )
    source_document = models.ForeignKey(
        'apptransactions.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_order_progress_checks',
        help_text='Optional link for future transaction-driven suggestions.',
    )

    class Meta:
        ordering = ['item__sequence', 'id']
        verbose_name = 'Work Order Progress Check'
        verbose_name_plural = 'Work Order Progress Checks'
        constraints = [
            UniqueConstraint(
                fields=['event', 'item'],
                name='uniq_wo_progress_check_event_item',
            ),
        ]

    def __str__(self):
        state = 'done' if self.is_done else 'pending'
        return f'{self.event_id}:{self.item.code} ({state})'
