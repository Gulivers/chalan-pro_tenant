from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email as django_validate_email
from django.db.models import Prefetch
from rest_framework import serializers

User = get_user_model()


def permission_label(permission: Permission) -> str:
    """Match Django Admin FilterSelectMultiple labels: App | model | Can …"""
    content_type = permission.content_type
    app_label = content_type.app_label
    try:
        from django.apps import apps

        app_config = apps.get_app_config(app_label)
        app_name = str(app_config.verbose_name)
    except LookupError:
        app_name = app_label
    return f'{app_name} | {content_type.name} | {permission.name}'


class PermissionCatalogSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    app_label = serializers.CharField(source='content_type.app_label', read_only=True)
    model = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'app_label', 'model', 'label']

    def get_label(self, obj):
        return permission_label(obj)


class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        required=False,
    )
    permission_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'permission_count']

    def get_permission_count(self, obj):
        if hasattr(obj, 'permission_count'):
            return obj.permission_count
        return obj.permissions.count()

    def create(self, validated_data):
        permissions = validated_data.pop('permissions', [])
        group = Group.objects.create(**validated_data)
        if permissions:
            group.permissions.set(permissions)
        return group

    def update(self, instance, validated_data):
        permissions = validated_data.pop('permissions', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        if permissions is not None:
            instance.permissions.set(permissions)
        return instance


class GroupListSerializer(serializers.ModelSerializer):
    permission_count = serializers.IntegerField(read_only=True)
    user_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'permission_count', 'user_count']


class UserAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password_confirm = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )
    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        required=False,
    )
    user_permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        required=False,
    )
    is_superuser = serializers.BooleanField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    group_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
            'date_joined',
            'last_login',
            'group_count',
        ]
        extra_kwargs = {
            'username': {'required': True},
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
        }

    def get_group_count(self, obj):
        if hasattr(obj, 'group_count'):
            return obj.group_count
        return obj.groups.count()

    def validate_first_name(self, value):
        name = (value or '').strip()
        if not name:
            raise serializers.ValidationError('First name is required.')
        return name

    def validate_last_name(self, value):
        name = (value or '').strip()
        if not name:
            raise serializers.ValidationError('Last name is required.')
        return name

    def validate_email(self, value):
        email = (value or '').strip()
        if not email:
            raise serializers.ValidationError('Email address is required.')
        try:
            django_validate_email(email)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        normalized = email.lower()
        qs = User.objects.filter(email__iexact=normalized)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                'A user with this email address already exists.'
            )
        return normalized

    def _user_for_password_validation(self, attrs):
        """Build a user-like object so attribute-similarity checks work on create."""
        if self.instance is not None:
            user = User(
                pk=self.instance.pk,
                username=attrs.get('username', self.instance.username),
                first_name=attrs.get('first_name', self.instance.first_name),
                last_name=attrs.get('last_name', self.instance.last_name),
                email=attrs.get('email', self.instance.email),
            )
            return user
        return User(
            username=attrs.get('username', ''),
            first_name=attrs.get('first_name', ''),
            last_name=attrs.get('last_name', ''),
            email=attrs.get('email', ''),
        )

    def validate(self, attrs):
        creating = self.instance is None
        password = attrs.get('password') or ''
        password_confirm = attrs.pop('password_confirm', None)
        if password_confirm is None:
            password_confirm = ''

        errors = {}
        if creating and not password:
            errors['password'] = 'Password is required for new users.'

        changing = bool(password) or bool(password_confirm)
        if creating or changing:
            if password and not password_confirm:
                errors['password_confirm'] = 'This field is required.'
            elif password_confirm and not password:
                errors['password'] = (
                    'Enter a new password, or leave both password fields blank.'
                )
            elif password and password_confirm and password != password_confirm:
                errors['password_confirm'] = "The two password fields didn’t match."

        if password and 'password' not in errors:
            try:
                validate_password(password, user=self._user_for_password_validation(attrs))
            except DjangoValidationError as exc:
                errors['password'] = list(exc.messages)

        if errors:
            raise serializers.ValidationError(errors)

        # Never accept superuser elevation from the SPA.
        attrs.pop('is_superuser', None)
        if not password:
            attrs.pop('password', None)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        groups = validated_data.pop('groups', [])
        user_permissions = validated_data.pop('user_permissions', [])
        validated_data.pop('password_confirm', None)
        validated_data['is_superuser'] = False
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if groups:
            user.groups.set(groups)
        if user_permissions:
            user.user_permissions.set(user_permissions)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        groups = validated_data.pop('groups', None)
        user_permissions = validated_data.pop('user_permissions', None)
        validated_data.pop('is_superuser', None)
        validated_data.pop('password_confirm', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        if groups is not None:
            instance.groups.set(groups)
        if user_permissions is not None:
            instance.user_permissions.set(user_permissions)
        return instance


class UserAdminListSerializer(serializers.ModelSerializer):
    group_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'is_staff',
            'is_superuser',
            'last_login',
            'date_joined',
            'group_count',
        ]


def permissions_queryset():
    return Permission.objects.select_related('content_type').order_by(
        'content_type__app_label',
        'content_type__model',
        'codename',
    )


def groups_queryset():
    from django.db.models import Count

    return (
        Group.objects.annotate(
            permission_count=Count('permissions', distinct=True),
            user_count=Count('user', distinct=True),
        )
        .prefetch_related(
            Prefetch('permissions', queryset=permissions_queryset()),
        )
        .order_by('name')
    )


def users_queryset():
    from django.db.models import Count

    return (
        User.objects.annotate(group_count=Count('groups', distinct=True))
        .prefetch_related(
            'groups',
            Prefetch('user_permissions', queryset=permissions_queryset()),
        )
        .order_by('username')
    )
