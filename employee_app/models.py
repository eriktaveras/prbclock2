from django.db import models
from django.db.models import Sum
from datetime import datetime, timedelta  # Assuming you are also using timedelta
from django.utils import timezone  # Utiliza timezone para trabajar con zonas horarias


# Represents a temporary external Employee.
class Employee(models.Model):
    name = models.CharField("Name", max_length=100)
    position = models.CharField("Position", max_length=100)

    def calculate_total_hours_week(self):
        # Obtén la fecha de inicio de la semana (lunes actual)
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())

        # Calcula el total de horas trabajadas en la semana actual
        total_hours_week = self.time_records.filter(
            date__gte=start_of_week, date__lte=today
        ).aggregate(total=Sum(models.F('working_hours'), output_field=models.DurationField()))

        return total_hours_week['total'] if total_hours_week['total'] else timedelta()

    def calculate_start_time(self):
        # Obtén el primer registro de tiempo de esta semana (lunes actual)
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())

        # Busca el primer registro de tiempo de esta semana para el empleado
        first_record = self.time_records.filter(
            date__gte=start_of_week, date__lte=today
        ).order_by('date', 'time_in').first()

        if first_record:
            return first_record.time_in
        else:
            return None

    def __str__(self):
        return f"{self.name} ({self.position})"

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"


# Represents a Time Record for an employee.
class TimeRecord(models.Model):
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name="time_records",
        verbose_name="Employee"
    )
    date = models.DateField("Date")
    time_in = models.TimeField("Time In", null=True, blank=True)
    time_out = models.TimeField("Time Out", null=True, blank=True)
    lunch_time = models.DurationField("Lunch Time", null=True, blank=True)

    def working_hours(self):
        if self.time_in and self.time_out:
            # Utiliza timezone.now() para obtener la hora actual en la zona horaria configurada
            now = timezone.now()
            
            # Combina la hora de entrada y salida con la fecha actual
            dt_in = timezone.datetime.combine(now.date(), self.time_in)
            dt_out = timezone.datetime.combine(now.date(), self.time_out)
            
            # Comprueba si time_out es anterior a time_in (cruzando la medianoche)
            if dt_out < dt_in:
                # Ajusta time_out para que sea al día siguiente
                dt_out += timezone.timedelta(days=1)
            
            # Calcula la diferencia de tiempo para las horas de trabajo
            delta = dt_out - dt_in
            
            # Resta lunch_time si existe
            if self.lunch_time:
                delta -= self.lunch_time
            
            return delta
        else:
            return None

    def __str__(self):
        return f"{self.employee.name} - {self.date}"

    class Meta:
        verbose_name = "Time Record"
        verbose_name_plural = "Time Records"
        unique_together = ("employee", "date")
