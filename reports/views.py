from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from cars.models import Car
from .forms import ReportForm
from .models import Report


@login_required
def report_car(request, car_id):
    car = get_object_or_404(Car, pk=car_id)

    already_reported = Report.objects.filter(reporter=request.user, car=car).exists()
    if already_reported:
        messages.info(request, 'Ya has enviado un reporte para esta publicación.')
        return redirect('cars:car_detail', car_id)

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.car = car
            report.save()
            messages.success(
                request,
                'Tu reporte fue enviado correctamente. Lo revisaremos a la brevedad.',
            )
            return redirect('cars:car_detail', car_id)
    else:
        form = ReportForm()

    return render(request, 'reports/report_form.html', {'form': form, 'car': car})
