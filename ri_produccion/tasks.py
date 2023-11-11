from celery import shared_task
from django.utils import timezone
from .models import Pieza, HistorialPieza

@shared_task
def mover_piezas_finalizadas():
    # obtén las piezas finalizadas del día anterior
    fecha_ayer = timezone.now().date() - timezone.timedelta(days=1)
    piezas_finalizadas = Pieza.objects.filter(procesos__estatus='realizado', procesos__finProceso__date=fecha_ayer)

    # mueve las piezas finalizadas al historial
    for pieza in piezas_finalizadas:
        historial_pieza = HistorialPieza.objects.create(
            consecutivo=pieza.consecutivo,
            ordenCompra=pieza.ordenCompra,
            piezas=pieza.piezas,
            piezasTotales=pieza.piezasTotales,
            material=pieza.material,
            placas=pieza.placas.all(),
            procesos=pieza.procesos.all(),
            creadoPor=pieza.creadoPor,
            archivo_pdf=pieza.archivo_pdf,
            prioridad=pieza.prioridad,
            fecha_finalizacion=timezone.now()
        )
        pieza.delete()
