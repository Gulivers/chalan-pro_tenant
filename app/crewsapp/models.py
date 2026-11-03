from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from ctrctsapp.models import Job

class Category (models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Truck(models.Model):
    FLEET_AVAILABLE = 'available'
    FLEET_MAINTENANCE = 'maintenance'
    FLEET_OUT_OF_SERVICE = 'out_of_service'
    FLEET_SOLD = 'sold'
    FLEET_STATUS_CHOICES = [
        (FLEET_AVAILABLE, 'Available'),
        (FLEET_MAINTENANCE, 'Maintenance'),
        (FLEET_OUT_OF_SERVICE, 'Out of Service'),
        (FLEET_SOLD, 'Sold'),
    ]

    unit_number = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='Unit Number',
        help_text='Internal identifier, e.g. TRK-001.',
    )
    plate_number = models.CharField(max_length=20, unique=True, verbose_name='Plate Number')
    vin = models.CharField(
        max_length=17,
        unique=True,
        verbose_name='VIN',
        help_text='17-character vehicle identification number (stored uppercase).',
    )
    make = models.CharField(max_length=100, verbose_name='Make')
    model = models.CharField(max_length=255, verbose_name='Model')
    year = models.IntegerField(verbose_name='Year')
    fleet_status = models.CharField(
        max_length=32,
        choices=FLEET_STATUS_CHOICES,
        default=FLEET_AVAILABLE,
        verbose_name='Status',
    )
    registration_expiration = models.DateField(verbose_name='Registration Expiration')
    insurance_expiration = models.DateField(verbose_name='Insurance Expiration')
    status = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        verbose_name = 'Truck'
        verbose_name_plural = 'Trucks'

    def __str__(self):
        return f"{self.unit_number} · {self.plate_number} ({self.make} {self.model})"

    def clean(self):
        super().clean()
        vin = (self.vin or '').strip().upper()
        if len(vin) != 17 or not vin.isalnum():
            raise ValidationError({
                'vin': 'VIN must be exactly 17 alphanumeric characters.',
            })
        self.vin = vin

    def save(self, *args, **kwargs):
        if self.vin:
            self.vin = self.vin.strip().upper()
        if self.unit_number:
            self.unit_number = self.unit_number.strip()
        super().save(*args, **kwargs)

    def current_mileage(self):
        """
        Latest odometer reading by date across assignment start/return events.
        Editing an older assignment cannot override a later reading.
        """
        readings = []
        links = self.assignment_links.select_related('assignment').all()
        for link in links:
            assignment = link.assignment
            if link.starting_mileage is not None and assignment.assigned_at:
                readings.append((assignment.assigned_at, int(link.starting_mileage)))
            if link.ending_mileage is not None and assignment.unassigned_at:
                readings.append((assignment.unassigned_at, int(link.ending_mileage)))
        if not readings:
            return None
        readings.sort(key=lambda item: item[0], reverse=True)
        return readings[0][1]


class Crew(models.Model):
    name = models.CharField(max_length=255, verbose_name='Crew Name')
    members = models.ManyToManyField(User, related_name='crews', verbose_name='Crew Members', blank=True)
    jobs = models.ManyToManyField(Job, related_name='crews', verbose_name='Assigned Jobs', blank=True)
    status = models.BooleanField(default=True, verbose_name='Active')  # Campo para indicar si está activa o inactiva
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, verbose_name='Category', null=True, blank=True)
    permission_create_event = models.BooleanField(default=False, verbose_name='Can Create/Update Schedule?')

    class Meta:
        verbose_name = 'Crew'
        verbose_name_plural = 'Crews'

    def __str__(self):
        return self.name


class TruckAssignment(models.Model):
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE, verbose_name='Assigned Crew')
    trucks = models.ManyToManyField(
        Truck,
        through='TruckAssignmentTruck',
        related_name='assignments',
        verbose_name='Assigned Trucks',
        blank=True,
    )
    assigned_at = models.DateTimeField(auto_now_add=False, verbose_name='Assigned At')
    unassigned_at = models.DateTimeField(
        auto_now_add=False, null=True, blank=True, verbose_name='Unassigned At'
    )

    def __str__(self):
        trucks_str = ", ".join(str(t) for t in self.trucks.all()) if self.trucks.exists() else "—"
        return f"{trucks_str} assigned to {self.crew}"

    class Meta:
        ordering = ['crew__name', '-assigned_at']


class TruckAssignmentTruck(models.Model):
    """Through model: per-truck odometer readings on an assignment."""

    assignment = models.ForeignKey(
        TruckAssignment,
        on_delete=models.CASCADE,
        related_name='truck_links',
    )
    truck = models.ForeignKey(
        Truck,
        on_delete=models.CASCADE,
        related_name='assignment_links',
    )
    starting_mileage = models.PositiveIntegerField(
        verbose_name='Starting Mileage',
        help_text='Odometer reading in miles when the assignment starts.',
    )
    ending_mileage = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Ending Mileage',
        help_text='Odometer reading in miles when the truck is returned.',
    )

    class Meta:
        verbose_name = 'Truck Assignment Reading'
        verbose_name_plural = 'Truck Assignment Readings'
        constraints = [
            models.UniqueConstraint(
                fields=['assignment', 'truck'],
                name='uniq_truckassignment_truck',
            ),
        ]

    def __str__(self):
        return f"{self.truck} on assignment {self.assignment_id}"

    def clean(self):
        super().clean()
        if self.ending_mileage is not None and self.starting_mileage is not None:
            if self.ending_mileage < self.starting_mileage:
                raise ValidationError({
                    'ending_mileage': (
                        'Ending mileage cannot be less than starting mileage.'
                    ),
                })
