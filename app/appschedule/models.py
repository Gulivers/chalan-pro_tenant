from django.db import models
from django.contrib.auth.models import User
from crewsapp.models import Crew
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
    work_account = models.ForeignKey('apptransactions.WorkAccount', on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
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
    work_account = models.ForeignKey('apptransactions.WorkAccount', on_delete=models.SET_NULL, null=True, blank=True, related_name='event_drafts')
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
    event = models.OneToOneField(Event, on_delete=models.CASCADE, verbose_name='event_note', related_name='note')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.notes


class EventChatMessage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='chat_messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}: {self.message[:50]}"


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
        # Guarda en: event_images/<event_id o 'unassigned'>/filename
        event_id = instance.event.id if instance.event_id else 'unassigned'
        base, ext = os.path.splitext(filename)
        return f'event_images/{event_id}/{base}{ext}'

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=EventImageUploadTo())
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Image for Event {self.event_id} ({self.id})"
