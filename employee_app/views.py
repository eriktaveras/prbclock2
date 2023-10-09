from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee, TimeRecord
from django.utils import timezone
from .forms import TimeRecordForm
from django.views.generic import TemplateView, ListView
from datetime import datetime  # Correct import for using datetime.now()
import csv
from datetime import timedelta
from django.http import HttpResponse
from django.db.models import Sum
from django.views import View

from .models import TimeRecord
from django.http import HttpResponseServerError



class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all()
        context['time_record_form'] = TimeRecordForm()
        context['pending_records'] = TimeRecord.objects.filter(time_out__isnull=True)
        context['all_records'] = TimeRecord.objects.all()  # Optimized database query
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if action == 'check_in':
            self.handle_check_in(request)
        elif action == 'check_out':
            self.handle_check_out(request)
        elif action == 'add_lunch':
            self.handle_add_lunch(request)

        return redirect('home')

    def handle_check_in(self, request):
        form = TimeRecordForm(request.POST)
        if form.is_valid():
            # Asegúrate de que la hora de entrada se registre en la zona horaria correcta
            form.instance.time_in = timezone.now().time()
            form.save()

    def handle_check_out(self, request):
        record_id = request.POST.get('record_id')
        record = get_object_or_404(TimeRecord, id=record_id)
        # Asegúrate de que la hora de salida se registre en la zona horaria correcta
        record.time_out = timezone.now().time()
        record.save()


    def handle_add_lunch(self, request):
        try:
            record_id = request.POST.get('record_id')
            employee_id = request.POST.get('employee_id')
            lunch_minutes = int(request.POST.get('lunch_minutes'))
            record = get_object_or_404(TimeRecord, id=record_id, employee_id=employee_id)
            record.lunch_time = timezone.timedelta(minutes=lunch_minutes)
            record.save()
            return HttpResponse("Almuerzo agregado correctamente")
        except Exception as e:
            return HttpResponseServerError(f"Error: {e}")





class WeeklySummaryView(ListView):
    template_name = 'weekly_summary.html'
    context_object_name = 'time_records'
    
    def get_queryset(self):
        today = timezone.now().date()
        last_monday = today - timedelta(days=today.weekday())
        next_sunday = last_monday + timedelta(days=6)
        
        queryset = TimeRecord.objects.filter(date__range=[last_monday, next_sunday])
        for record in queryset:
            record.day_of_week = record.date.strftime('%A')
            record.working_time = record.working_hours()  # Assumes you've added this method to your model
            record.total_hours = record.working_time.total_seconds() / 3600  # Convert to hours
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        queryset = self.get_queryset()
        context['total_hours'] = sum(record.total_hours for record in queryset)
        
        return context
    
    def export_csv(request):
        today = timezone.now().date()
        last_monday = today - timedelta(days=today.weekday())
        next_sunday = last_monday + timedelta(days=6)  # Including Sunday

        queryset = TimeRecord.objects.filter(date__range=[last_monday, next_sunday])

        # Calculate total_hours for each record
        for record in queryset:
            time_in = datetime.combine(datetime.today(), record.time_in)
            time_out = datetime.combine(datetime.today(), record.time_out)
            
            # Check if lunch_time is None and default to zero if it is
            lunch_minutes = 0 if record.lunch_time is None else (record.lunch_time.seconds // 60)
            delta = time_out - time_in - timedelta(minutes=lunch_minutes)
            
            record.total_hours = delta.total_seconds() / 3600  # Convert to hours

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="weekly_summary.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Nombre', 'Fecha', 'Hora de Ingreso', 'Hora de Salida', 'Tiempo de Almuerzo', 'Horas Totales'])

        for record in queryset:
            writer.writerow([record.id, record.employee.name, record.date, record.time_in, record.time_out, lunch_minutes, record.total_hours])

        return response


class MonthlySummaryView(View):
    template_name = 'monthly_summary.html'

    def get(self, request, year, month):
        # Convierte los parámetros de año y mes en números enteros
        year = int(year)
        month = int(month)

        # Calcula la fecha de inicio y fin del mes
        start_date = timezone.make_aware(datetime(year, month, 1))
        end_date = start_date + timedelta(days=32)

        # Obtiene los registros de tiempo dentro del rango de fechas
        time_records = TimeRecord.objects.filter(date__range=[start_date, end_date])

        # Calcula las horas totales por empleado utilizando un diccionario
        summary_data = {}
        for record in time_records:
            if record.employee.name not in summary_data:
                summary_data[record.employee.name] = {
                    'employee': record.employee.name,
                    'total_hours': 0,
                }

            if record.time_in and record.time_out:
                delta = record.working_hours()
                if delta:
                    summary_data[record.employee.name]['total_hours'] += delta.total_seconds() / 3600

        # Convierte el diccionario en una lista para la plantilla
        summary_data_list = list(summary_data.values())

        # Pasa los datos a la plantilla
        context = {
            'year': year,
            'month': month,
            'summary_data': summary_data_list,
        }

        return render(request, self.template_name, context)

def employee_detail(request, employee_id):
    employee = Employee.objects.get(pk=employee_id)
    
    # Obtén la fecha de inicio de la semana (lunes actual)
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())

    # Filtra todos los registros de tiempo para este empleado
    time_records = employee.time_records.order_by('date', 'time_in')
    
    total_hours_week = timedelta()
    start_time = None

    # Calcula el total de horas trabajadas en la semana actual y la hora de inicio
    for record in time_records:
        if record.time_in:
            if not start_time:
                start_time = record.time_in
            total_hours_week += record.working_hours()
    
    context = {
        'employee': employee,
        'total_hours_week': total_hours_week,
        'start_time': start_time,
        'time_records': time_records,  # Pasa todos los registros de tiempo
    }
    
    return render(request, 'employee_detail.html', context)