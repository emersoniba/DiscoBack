
from modulos.utilitario.viewset import RestViewSet

from .models import Proveedor, TipoMovimiento, EstadoMovimiento, Movimiento, MovimientoDetalle
from .serializers import (
    ProveedorSerializer, TipoMovimientoSerializer, EstadoMovimientoSerializer,
    MovimientoSerializer, MovimientoDetalleSerializer
)

class ProveedorViewSet(RestViewSet):
    queryset = Proveedor.objects.filter(fecha_eliminacion__isnull=True)
    serializer_class = ProveedorSerializer

class TipoMovimientoViewSet(RestViewSet):
    queryset = TipoMovimiento.objects.filter(fecha_eliminacion__isnull=True)
    serializer_class = TipoMovimientoSerializer

class EstadoMovimientoViewSet(RestViewSet):
    queryset = EstadoMovimiento.objects.filter(fecha_eliminacion__isnull=True)
    serializer_class = EstadoMovimientoSerializer

class MovimientoViewSet(RestViewSet):
    queryset = Movimiento.objects.filter(fecha_eliminacion__isnull=True).prefetch_related('detalles')
    serializer_class = MovimientoSerializer

class MovimientoDetalleViewSet(RestViewSet):
    queryset = MovimientoDetalle.objects.filter(fecha_eliminacion__isnull=True)
    serializer_class = MovimientoDetalleSerializer