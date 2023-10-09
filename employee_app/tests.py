from django.test import TestCase
from datetime import date, time, timedelta
from .models import Employee, TimeRecord
from .forms import TimeRecordForm

# Tests for Employee model
class EmployeeModelTest(TestCase):
    def test_string_representation(self):
        employee = Employee(name="John Doe", position="Developer")
        self.assertEqual(str(employee), "John Doe (Developer)")

    def test_create_multiple_employees(self):
        Employee.objects.create(name="John Doe", position="Developer")
        Employee.objects.create(name="Jane Doe", position="Manager")
        self.assertEqual(Employee.objects.count(), 2)

# Tests for TimeRecord model
class TimeRecordModelTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(name="John Doe", position="Developer")

    def test_string_representation(self):
        time_record = TimeRecord(employee=self.employee, date=date.today())
        self.assertEqual(str(time_record), "John Doe - {}".format(date.today()))

    def test_create_multiple_time_records(self):
        TimeRecord.objects.create(employee=self.employee, date=date.today())
        TimeRecord.objects.create(employee=self.employee, date=date.today() - timedelta(days=1))
        self.assertEqual(TimeRecord.objects.count(), 2)

# Tests for TimeRecordForm
class TimeRecordFormTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(name="John Doe", position="Developer")

    def test_valid_form(self):
        data = {
            'employee': self.employee.id,
            'date': date.today(),
            'time_in': time(hour=9, minute=0),
            'time_out': time(hour=17, minute=0),
            'lunch_time': '01:00:00'  # 1 hour lunch break
        }
        form = TimeRecordForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_date(self):
        data = {
            'employee': self.employee.id,
            'date': '',
            'time_in': time(hour=9, minute=0),
            'time_out': time(hour=17, minute=0),
            'lunch_time': '01:00:00'
        }
        form = TimeRecordForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['date'], ['This field is required.'])

    def test_invalid_form_time_out_before_time_in(self):
        data = {
            'employee': self.employee.id,
            'date': date.today(),
            'time_in': time(hour=17, minute=0),
            'time_out': time(hour=9, minute=0),
            'lunch_time': '01:00:00'
        }
        form = TimeRecordForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['time_out'], ['Time Out must be after Time In.'])

    def test_invalid_form_negative_lunch_time(self):
        data = {
            'employee': self.employee.id,
            'date': date.today(),
            'time_in': time(hour=9, minute=0),
            'time_out': time(hour=17, minute=0),
            'lunch_time': '-01:00:00'
        }
        form = TimeRecordForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['lunch_time'], ['Lunch time cannot be negative.'])
