from datetime import timedelta
from django.db.models import Q
from django.contrib.auth.models import User
from django.db import IntegrityError            # oahp
import logging                                  # oahp
from rest_framework import serializers
from rest_framework.exceptions import ValidationError           # oahp
from rest_framework.validators import ValidationError, UniqueTogetherValidator  # oahp
from .models import (
    Event, EventDraft, EventNote, EventChatMessage, 
    AbsenceReason,EventImage 
)

logger = logging.getLogger("appschedule") 

class EventSerializer(serializers.ModelSerializer):
    """Serializer for events objects"""
    crew_title = serializers.SerializerMethodField()
    crew_category = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    work_account_title = serializers.SerializerMethodField()

    def get_crew_title(self, obj):
        return obj.crew.name
    
    def get_crew_category(self, obj):
        if obj.crew and obj.crew.category:
            return obj.crew.category.name
        return None 
    
    def get_work_account_title(self, obj):
        if obj.work_account:
            return obj.work_account.title
        return None

    def get_images(self, obj):
        images = obj.images.all()
        return EventImageSerializer(images, many=True, context=self.context).data

    class Meta:
        model = Event
        fields = '__all__'
        extra_fields = ['crew_title', 'crew_category', 'images']
        validators = [
            UniqueTogetherValidator(
                queryset=Event.objects.all(),
                fields=['crew', 'date', 'title'],
                message='Duplicate (crew, date, title) not allowed.'
            )
        ]

    #  atrapa Integridad en create/update y loggea
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            logger.warning(
                "integrity_error_event_create crew=%s date=%s title=%s err=%s",
                validated_data.get('crew'),
                validated_data.get('date'),
                validated_data.get('title'),
                e
            )
            raise ValidationError({'non_field_errors': ['Duplicate (crew, date, title) not allowed.']})

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as e:
            logger.warning(
                "integrity_error_event_update id=%s crew=%s date=%s title=%s err=%s",
                getattr(instance, 'id', None),
                validated_data.get('crew', getattr(instance, 'crew', None)),
                validated_data.get('date', getattr(instance, 'date', None)),
                validated_data.get('title', getattr(instance, 'title', None)),
                e
            )
            raise ValidationError({'non_field_errors': ['Duplicate (crew, date, title) not allowed.']})
        
        
class EventDraftSerializer(serializers.ModelSerializer):
    """Serializer for events draft objects"""

    crew_title = serializers.SerializerMethodField()
    work_account_title = serializers.SerializerMethodField()

    def get_crew_title(self, obj):
        return obj.crew.name
    
    def get_work_account_title(self, obj):
        if obj.work_account:
            return obj.work_account.title
        return None

    class Meta:
        model = EventDraft
        fields = '__all__'
        extra_kwargs = {
            'end_dt': {'required': False, 'allow_null': True},
            'title': {'required': True, 'allow_null': False, 'allow_blank': False},
        }

    def create(self, validated_data):
        date = validated_data.get('date')
        end_dt = validated_data.get('end_dt')
        if date:
            if not end_dt or end_dt <= date:
                validated_data['end_dt'] = date + timedelta(days=1)

        return super().create(validated_data)


    def validate(self, data):
        is_absence = data.get('is_absence', getattr(self.instance, 'is_absence', False))
        if is_absence:
            return data
        
        # Tomar valores del instance si no están en data (caso PATCH parcial)
        work_account = data.get('work_account', getattr(self.instance, 'work_account', None))
        
        # Si viene work_account, extraer sus datos para la validación
        # (los campos se sincronizarán automáticamente en el save() del modelo)
        if work_account:
            lot = work_account.lot
            address = work_account.address
            job = work_account.job
        else:
            # Fallback a campos individuales (compatibilidad con código legacy)
            lot = data.get('lot', getattr(self.instance, 'lot', None))
            address = data.get('address', getattr(self.instance, 'address', None))
            job = data.get('job', getattr(self.instance, 'job', None))
        
        crew = data.get('crew', getattr(self.instance, 'crew', None))
        event = data.get('event', getattr(self.instance, 'event', None))
        event_id = event.pk if event else None
        start_at = data.get('date', getattr(self.instance, 'date', None))
        end_at = data.get('end_dt', getattr(self.instance, 'end_dt', None))

        if not crew:
            raise ValidationError("Crew is required")

        category = crew.category

        if start_at and (not end_at or end_at <= start_at):
            end_at = start_at + timedelta(days=1)
            data['end_dt'] = end_at

        # Validar que se haya proporcionado work_account o al menos job/lot/address
        if not work_account and not (lot or address or job):
            raise ValidationError("Work Account or Address/Lot/Job must be provided")

        # Validación de duplicados usando lot o address
        qs_ed = EventDraft.objects.filter(crew__category=category)
        qs_e = Event.objects.filter(crew__category=category, deleted=False)

        if lot:
            qs_ed = qs_ed.filter(job=job, lot=lot)
            qs_e = qs_e.filter(job=job, lot=lot)
        elif address:
            qs_ed = qs_ed.filter(address=address)
            qs_e = qs_e.filter(address=address)

        if self.instance:
            qs_ed = qs_ed.exclude(pk=self.instance.pk)
        if event_id:
            qs_ed = qs_ed.exclude(event_id=event_id)
            qs_e = qs_e.exclude(pk=event_id)

        if qs_ed.exists() or qs_e.exists():
            raise ValidationError("Duplicate Event Detected")

        return data


class EventNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventNote
        fields = ['notes', 'updated_at', 'updated_by', 'event']
        read_only_fields = ['updated_at', 'updated_by']

    def create(self, validated_data):
        print('create validated_data', validated_data)
        event = validated_data['event']
        validated_data['updated_by'] = self.context['request'].user
        print('create validated_data', validated_data)
        try:
            event_note, created = EventNote.objects.update_or_create(
                event=event,
                defaults=validated_data
            )
            return event_note
        except Exception as e:
            raise serializers.ValidationError(f"Error creating EventNote: {e}")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class EventChatMessageSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = EventChatMessage
        fields = ['id', 'event', 'author', 'message', 'timestamp']
        read_only_fields = ['id', 'timestamp', 'author']
        extra_kwargs = {'event': {'write_only': True}}

    def create(self, validated_data):
        event = validated_data.pop('event')
        author = self.context['request'].user
        return EventChatMessage.objects.create(event=event, author=author, **validated_data)
    
class AbsenceReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsenceReason
        fields = ['id', 'name', 'description']


class EventImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = EventImage
        fields = ['id', 'event', 'image', 'image_url', 'uploaded_at', 'uploaded_by']
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url
        return None
