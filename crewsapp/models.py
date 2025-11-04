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
    plate_number = models.CharField(max_length=20, unique=True, verbose_name='Plate Number')
    model = models.CharField(max_length=255, verbose_name='Model')
    year = models.IntegerField(verbose_name='Year')
    status = models.BooleanField(default=True, verbose_name='Active')  # Campo para indicar si está activa o inactiva

    class Meta:
        verbose_name = 'Truck'
        verbose_name_plural = 'Trucks'

    def __str__(self):
        return f"{self.model} - {self.plate_number}"


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
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE, verbose_name='Assigned Truck')
    assigned_at = models.DateTimeField(auto_now_add=False, verbose_name='Assigned At')
    unassigned_at = models.DateTimeField(auto_now_add=False, null=True, blank=True, verbose_name='Unassigned At')

    def __str__(self):
        return f"{self.truck} assigned to {self.crew}"

