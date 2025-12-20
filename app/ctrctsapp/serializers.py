from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import serializers, viewsets
from .models import WorkPrice, Contract, ContractDetails, Builder, Job, HouseModel
from appschedule.models import Event
from apptransactions.models import WorkAccount
from crewsapp.models import Crew
from apptransactions.models import PartyType, PartyCategory
from appinventory.models import PriceType

import logging

logger = logging.getLogger(__name__)

# Serializer for the Builder model
# Serializador para el modelo Builder
class BuilderSerializer(serializers.ModelSerializer):
    # Campos booleanos para el frontend
    customer_rank = serializers.BooleanField(write_only=True, required=False, allow_null=True)
    supplier_rank = serializers.BooleanField(write_only=True, required=False, allow_null=True)
    
    # Campos de relaciones
    types = serializers.PrimaryKeyRelatedField(many=True, queryset=PartyType.objects.filter(is_active=True), required=False, allow_null=True)
    category = serializers.PrimaryKeyRelatedField(queryset=PartyCategory.objects.filter(is_active=True), required=False, allow_null=True)
    default_price_type = serializers.PrimaryKeyRelatedField(queryset=PriceType.objects.all(), required=False, allow_null=True)
    
    class Meta:
        model = Builder
        fields = ['id', 'name', 'trim_amount', 'rough_amount', 'travel_price_amount', 
                 'rfc', 'street', 'floor_office', 'city', 'state', 'zipcode', 
                 'country', 'phone', 'email', 'types', 'category', 'default_price_type',
                 'customer_rank', 'supplier_rank', 'is_active']
    
    def to_representation(self, instance):
        """Convierte los enteros a booleanos para el frontend"""
        data = super().to_representation(instance)
        data['customer_rank'] = instance.customer_rank > 0
        data['supplier_rank'] = instance.supplier_rank > 0
        return data
    
    def to_internal_value(self, data):
        """Convierte los booleanos a enteros para el backend y maneja valores nulos"""
        # Crear una copia para no modificar el original
        data_copy = data.copy()
        
        # Manejar campos booleanos
        if 'customer_rank' in data_copy:
            if data_copy['customer_rank'] is None or data_copy['customer_rank'] == '':
                data_copy['customer_rank'] = 0
            else:
                data_copy['customer_rank'] = 1 if data_copy['customer_rank'] else 0
        
        if 'supplier_rank' in data_copy:
            if data_copy['supplier_rank'] is None or data_copy['supplier_rank'] == '':
                data_copy['supplier_rank'] = 0
            else:
                data_copy['supplier_rank'] = 1 if data_copy['supplier_rank'] else 0
        
        # Manejar campos de relaciones que pueden ser nulos
        if 'types' in data_copy:
            if data_copy['types'] is None or data_copy['types'] == '' or data_copy['types'] == []:
                data_copy['types'] = []
            elif isinstance(data_copy['types'], str):
                # Si viene como string, convertir a lista vacía
                data_copy['types'] = []
        
        if 'category' in data_copy:
            if data_copy['category'] is None or data_copy['category'] == '':
                data_copy['category'] = None
            elif isinstance(data_copy['category'], str) and data_copy['category'].strip() == '':
                data_copy['category'] = None
            
        if 'default_price_type' in data_copy:
            if data_copy['default_price_type'] is None or data_copy['default_price_type'] == '':
                data_copy['default_price_type'] = None
            elif isinstance(data_copy['default_price_type'], str) and data_copy['default_price_type'].strip() == '':
                data_copy['default_price_type'] = None
            
        return super().to_internal_value(data_copy)
    
    def create(self, validated_data):
        """Crear Builder con manejo de campos ManyToMany"""
        types_data = validated_data.pop('types', [])
        builder = Builder.objects.create(**validated_data)
        if types_data:
            builder.types.set(types_data)
        return builder
    
    def update(self, instance, validated_data):
        """Actualizar Builder con manejo de campos ManyToMany"""
        types_data = validated_data.pop('types', None)
        
        # Actualizar campos normales
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar ManyToMany si se proporciona
        if types_data is not None:
            instance.types.set(types_data)
        
        return instance
    
    def validate_name(self, value):
        """Validar nombre único"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Must be at least 2 characters.")
        
        # Verificar unicidad
        queryset = Builder.objects.filter(name__iexact=value.strip())
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("A builder with this name already exists.")
        
        return value.strip()
    
    def validate_rfc(self, value):
        """Validar RFC único"""
        if value and value.strip():
            # Verificar unicidad solo si RFC no está vacío
            queryset = Builder.objects.filter(rfc=value.strip())
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError("A builder with this RFC already exists.")
            
            return value.strip()
        return value
    
    def validate_email(self, value):
        """Validar formato de email"""
        if value and value.strip():
            import re
            email_regex = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
            if not email_regex.match(value.strip()):
                raise serializers.ValidationError("Enter a valid email address.")
            return value.strip().lower()
        return value

# Mini serializer de lectura (opcional, para debug/UX)
class CrewMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "name")

class JobSerializer(serializers.ModelSerializer):
    builder = serializers.PrimaryKeyRelatedField(queryset=Builder.objects.all())

    # Acepta escribir crews como lista de IDs
    crews = serializers.PrimaryKeyRelatedField(
        queryset=Crew.objects.all(),
        many=True,
        required=False,
        write_only=True  # solo escritura; si quieres verlo en responses, quítalo
    )

    # Detalle de lectura opcional (no estorba)
    crews_detail = CrewMiniSerializer(source="crews", many=True, read_only=True)

    # (opcional) compatibilidad con tu campo anterior de solo lectura
    crew_leaders = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Job
        fields = [
            "id", "name", "builder", "address", "latitude", "longitude",
            "crews",          # << === escribe M2M
            "crews_detail",   # << === lee M2M (id+name)
            "crew_leaders",   # << === legacy read-only
        ]

    def get_crew_leaders(self, obj):
        return list(obj.crews.values_list("name", flat=True))

    # Blindaje: setear la M2M explícitamente en create/update
    def create(self, validated_data):
        crews = validated_data.pop("crews", [])
        job = super().create(validated_data)
        if crews:
            job.crews.set(crews)
        return job

    def update(self, instance, validated_data):
        crews = validated_data.pop("crews", None)
        job = super().update(instance, validated_data)
        if crews is not None:
            job.crews.set(crews)
        return job

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().select_related('builder').prefetch_related('crews')  # performance
    serializer_class = JobSerializer


# Serializer for the HouseModel model, including related jobs
class HouseModelSerializer(serializers.ModelSerializer):
    jobs = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all(), many=True)

    class Meta:
        model = HouseModel
        fields = ['id', 'name', 'jobs']

    def validate_name(self, value):
        """
        Check that the name is unique within the same builder, allowing updates to the current instance.
        The validation works through the relationship: HouseModel -> Jobs -> Builder
        """
        name = value
        instance_pk = self.instance.pk if self.instance else None
        
        # Get the builder_id from the context (passed from the view)
        builder_id = self.context.get('builder_id')
        
        # Debug: Print builder_id to see if it's being passed correctly
        print(f"DEBUG: builder_id = {builder_id}")
        print(f"DEBUG: context = {self.context}")
        
        # Filter HouseModels that have jobs belonging to the same builder
        if builder_id:
            qs = HouseModel.objects.filter(
                name__iexact=name,
                jobs__builder_id=builder_id
            ).distinct()

            if instance_pk:
                # If we are updating an existing object, exclude it from the uniqueness check
                qs = qs.exclude(pk=instance_pk)

            if qs.exists():
                # Get the builder name for a more descriptive error message
                from .models import Builder
                try:
                    builder = Builder.objects.get(id=builder_id)
                    builder_name = builder.name or "Unknown Builder"
                except Builder.DoesNotExist:
                    builder_name = "Unknown Builder"
                
                raise serializers.ValidationError(f"A House Model with this name already exists for builder {builder_name}. ⚠")
        else:
            # If no builder_id is provided, fall back to global uniqueness
            qs = HouseModel.objects.filter(name__iexact=name)
            if instance_pk:
                qs = qs.exclude(pk=instance_pk)
            if qs.exists():
                raise serializers.ValidationError("A house with this name already exists. ⚠")
        
        return value

    def create(self, validated_data):
        # Extract jobs from validated data
        jobs = validated_data.pop('jobs', [])
        # Create the HouseModel instance
        house_model = HouseModel.objects.create(**validated_data)
        # Add the jobs to the ManyToMany field
        house_model.jobs.set(jobs)
        return house_model

    def update(self, instance, validated_data):
        # Extract jobs from validated data
        jobs = validated_data.pop('jobs', [])
        # Update the HouseModel instance
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        # Update the ManyToMany field
        instance.jobs.set(jobs)
        return instance

# Serializer for the ContractDetails model
# Serializador para el modelo ContractDetails
class ContractDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractDetails
        fields = ['id', 'cdname', 'cdtrim', 'cdrough', 'cdunit_price', 'cdwork_price', 'contract_details', 'cdtrim_qty', 'cdrough_qty']

# Serializer for the WorkPrice model
# Serializador para el modelo WorkPrice
class WorkPriceSerializer(serializers.ModelSerializer):
    builders = serializers.PrimaryKeyRelatedField(many=True, queryset=Builder.objects.all())

    class Meta:
        model = WorkPrice
        fields = ['id', 'name', 'trim', 'rough', 'unit_price', 'builders']

    # Create a new WorkPrice instance and set its builders
    # Crear una nueva instancia de WorkPrice y asignar sus builders
    def create(self, validated_data):
        builders_data = validated_data.pop('builders')
        work_price = WorkPrice.objects.create(**validated_data)
        work_price.builders.set(builders_data)
        return work_price

    # Update an existing WorkPrice instance and set its builders
    # Actualizar una instancia existente de WorkPrice y asignar sus builders
    def update(self, instance, validated_data):
        builders_data = validated_data.pop('builders', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if builders_data is not None:
            instance.builders.set(builders_data)
        return instance

# Serializer for the Contract model
# Serializador para el modelo Contract
class ContractSerializer(serializers.ModelSerializer):
    contract_details = ContractDetailsSerializer(many=True)
    house_model = HouseModelSerializer(read_only=True)
    builder = BuilderSerializer(read_only=True)
    job = JobSerializer(read_only=True)
    house_model_id = serializers.PrimaryKeyRelatedField(queryset=HouseModel.objects.all(), source='house_model', write_only=True)
    builder_id = serializers.PrimaryKeyRelatedField(queryset=Builder.objects.all(), source='builder', write_only=True)
    job_id = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all(), source='job', write_only=True)
    # Nuevos campos para enlazar Work Account y Schedule (Event)
    work_account_id = serializers.PrimaryKeyRelatedField(queryset=WorkAccount.objects.all(), source='work_account', write_only=True, required=False, allow_null=True)
    schedule_id = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all(), source='schedule', write_only=True, required=False, allow_null=True)

    class Meta:
        model = Contract
        fields = [
            'id', 'created_by', 'date_created', 'last_updated', 'type', 'builder', 'builder_id',
            'job', 'job_id', 'house_model', 'house_model_id', 'lot', 'sqft', 'address', 'job_price', 'travel_price', 
            'total_options', 'total', 'comment', 'file', 'contract_details', 'needs_reprint', 'doc_type',
            # FK ids de solo lectura para edición/visualización
            'work_account', 'schedule',
            # write-only para crear/actualizar
            'work_account_id', 'schedule_id',
        ]
        read_only_fields = ['id', 'date_created', 'last_updated']

    # Create a new Contract instance with validated data
    # Crear una nueva instancia de Contract con datos validados
    def create(self, validated_data):
        contract_details_data = validated_data.pop('contract_details')

        # Permite crear el contrato solo con work_account_id, completando campos legacy
        work_account = validated_data.get('work_account')
        builder = validated_data.pop('builder', None)
        job = validated_data.pop('job', None)
        house_model = validated_data.pop('house_model', None)

        if work_account:
            builder = builder or getattr(work_account, 'builder', None)
            job = job or getattr(work_account, 'job', None)
            house_model = house_model or getattr(work_account, 'house_model', None)

        # Validaciones explícitas para evitar IntegrityError de DB
        errors = {}
        if not builder:
            errors['builder_id'] = 'Required (or provide work_account_id with builder).'
        if not job:
            errors['job_id'] = 'Required (or provide work_account_id with job).'
        if not house_model:
            errors['house_model_id'] = 'Required (or provide work_account_id with house_model).'
        if errors:
            raise serializers.ValidationError(errors)

        # Travel price sincronizado con el builder
        validated_data['travel_price'] = builder.travel_price_amount

        with transaction.atomic():
            # Create the contract with validated data
            # Crear el contrato con los datos validados
            contract = Contract.objects.create(
                **validated_data,
                builder=builder,
                job=job,
                house_model=house_model
            )

            for detail_data in contract_details_data:
                detail_data['contract_details_id'] = contract.id

                ContractDetails.objects.create(**detail_data)

        return contract

    # Update an existing Contract instance with validated data
    # Actualizar una instancia existente de Contract con datos validados
    def update(self, instance, validated_data):
        # Extract nested data
        # Extraer datos anidados
        contract_details_data = validated_data.pop('contract_details', None)
        builder_id = validated_data.pop('builder_id', None)
        job_id = validated_data.pop('job_id', None)
        house_model_id = validated_data.pop('house_model_id', None)

        with transaction.atomic():
            # Update foreign key relationships if they exist
            # Actualizar relaciones de clave foránea si existen
            if builder_id:
                instance.builder = Builder.objects.get(id=builder_id)
                instance.travel_price = instance.builder.travel_price_amount  # Usa el travel_price_amount del builder

            if job_id:
                instance.job = Job.objects.get(id=job_id)

            if house_model_id:
                instance.house_model = HouseModel.objects.get(id=house_model_id)

            # Update other contract fields
            # Actualizar otros campos del contrato
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Handle contract details
            # Manejar los detalles del contrato
            if contract_details_data is not None:
                # Delete existing details
                # Eliminar detalles existentes
                ContractDetails.objects.filter(contract_details=instance).delete()
                # Create new details
                # Crear nuevos detalles
                for detail_data in contract_details_data:
                    # Ensure the 'contract_details' field is not passed twice
                    # Asegúrate de no pasar el campo 'contract_details' dos veces
                    ContractDetails.objects.create(contract_details=instance, **detail_data)

        return instance

# Serializer for the Job model filtered by builder
# Serializador para el modelo Job filtrado por builder
class JobFilteredByBuilderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'name', 'builder', 'address', 'latitude', 'longitude']

# Serializer for the HouseModel model filtered by job
# Serializador para el modelo HouseModel filtrado por job
class HouseModelFilteredByJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseModel
        fields = ['id', 'name', 'jobs']


# Serializers for list options
class BuilderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Builder
        fields = ['id', 'name', 'phone', 'email', 'city', 'customer_rank', 'supplier_rank', 'is_active']


class JobListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'name', 'address', 'builder']


class HouseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseModel
        fields = ['id', 'name', 'jobs']

class ContractListSerializer(serializers.ModelSerializer):
    builder = BuilderSerializer(allow_null=True)
    job = JobSerializer(allow_null=True)
    house_model = HouseModelSerializer(allow_null=True)

    class Meta:
        model = Contract
        fields = ['id', 'type', 'builder', 'job', 'house_model', 'lot', 'address', 'sqft', 'job_price', 'total_options', 'total', 'needs_reprint', 'doc_type', 'date_created']


class ContractListLiteSerializer(serializers.ModelSerializer):
    builder = serializers.SerializerMethodField()
    job = serializers.SerializerMethodField()
    house_model = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = ['id', 'type', 'builder', 'job', 'house_model', 'lot', 'address', 'sqft', 'job_price', 'total_options', 'total', 'needs_reprint', 'doc_type', 'date_created']

    def get_builder(self, obj):
        b = getattr(obj, 'builder', None)
        if not b:
            return None
        return { 'id': b.id, 'name': b.name }

    def get_job(self, obj):
        j = getattr(obj, 'job', None)
        if not j:
            return None
        return { 'id': j.id, 'name': j.name }

    def get_house_model(self, obj):
        h = getattr(obj, 'house_model', None)
        if not h:
            return None
        return { 'id': h.id, 'name': h.name }
