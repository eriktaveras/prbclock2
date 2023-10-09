import os
import django
import random
from datetime import date, time, timedelta

# Configura la configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EmployeeManagement.settings')
django.setup()

from employee_app.models import Employee, TimeRecord

# Función para crear empleados
def create_employees():
    employees_data = [
        {"name": "Empleado 1", "position": "Puesto 1"},
        {"name": "Empleado 2", "position": "Puesto 2"},
        {"name": "Empleado 3", "position": "Puesto 3"},
        # Agrega más empleados según sea necesario
    ]

    for data in employees_data:
        Employee.objects.create(**data)

# Función para crear registros de tiempo para una semana
def create_time_records(employee, start_date):
    # Genera registros de tiempo para una semana
    for i in range(7):
        day = start_date + timedelta(days=i)
        time_in = time(random.randint(8, 10), random.randint(0, 59))
        time_out = time(random.randint(16, 18), random.randint(0, 59))
        lunch_minutes = random.randint(0, 60)

        TimeRecord.objects.create(
            employee=employee,
            date=day,
            time_in=time_in,
            time_out=time_out,
            lunch_time=timedelta(minutes=lunch_minutes)
        )

def main():
    create_employees()

    employees = Employee.objects.all()
    start_date = date(2023, 1, 2)  # Lunes de la primera semana

    for employee in employees:
        create_time_records(employee, start_date)
        start_date += timedelta(weeks=1)  # Avanza a la siguiente semana

if __name__ == "__main__":
    main()
