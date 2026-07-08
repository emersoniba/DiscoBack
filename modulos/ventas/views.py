from modulos.utilitario.viewset import RestViewSet
from .models import Cliente, MetodoPago, Venta, VentaDetalle
from .serializers import ClienteSerializer, MetodoPagoSerializer, VentaSerializer, VentaDetalleSerializer

class ClienteViewSet(RestViewSet):
    queryset = Cliente.objects.filter(fecha_eliminacion__isnull=True)
    serializer_class = ClienteSerializer

class MetodoPagoViewSet(RestViewSet):
    queryset = MetodoPago.objects.filter(fecha_eliminacion__isnull=True, activo=True)
    serializer_class = MetodoPagoSerializer

class VentaViewSet(RestViewSet):
    queryset = Venta.objects.filter(fecha_eliminacion__isnull=True).prefetch_related('detalles')
    serializer_class = VentaSerializer

class VentaDetalleViewSet(RestViewSet):
    queryset = VentaDetalle.objects.filter(fecha_eliminacion__isnull=True)
    serializer_class = VentaDetalleSerializer