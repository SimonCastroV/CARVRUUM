from django.db import models
from django.conf import settings


class Report(models.Model):

    REASON_CHOICES = [
        ('fraude',                 'Fraude'),
        ('contenido_inapropiado',  'Contenido inapropiado'),
        ('precio_enganoso',        'Precio engañoso'),
        ('informacion_falsa',      'Información falsa'),
        ('otro',                   'Otro'),
    ]

    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('revisado',  'Revisado'),
        ('resuelto',  'Resuelto'),
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_submitted',
    )
    car = models.ForeignKey(
        'cars.Car',
        on_delete=models.CASCADE,
        related_name='reports',
    )
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['reporter', 'car'],
                name='unique_reporter_car_report',
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Reporte de {self.reporter} sobre {self.car} – {self.get_reason_display()}"
