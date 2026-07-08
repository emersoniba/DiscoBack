
from modulos.inventario.models import StockAlmacen
from modulos.utilitario.viewset import RestViewSet
from rest_framework.decorators import action

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

    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        movimiento = self.get_object()
        usuario = request.user

        if not movimiento.estado.afecta_stock:
            return ErrorResponse(message="Solo se pueden anular movimientos que ya están completados.")

        try:
            # Buscamos el estado "Anulado" en tu base de datos
            estado_anulado = EstadoMovimiento.objects.get(nombre__iexact="Anulado")
        except EstadoMovimiento.DoesNotExist:
            return ErrorResponse(message="Debe crear un estado llamado 'Anulado' en los catálogos.")

        with transaction.atomic():
            tipo = movimiento.tipo_movimiento
            
            # 1. Reversión matemática del stock
            for detalle in movimiento.detalles.all():
                producto = detalle.producto
                cantidad = detalle.cantidad

                # Resta Inversa en Origen
                if tipo.requiere_origen and movimiento.almacen_origen and tipo.factor_origen != 0:
                    stock_origen = StockAlmacen.objects.get(almacen=movimiento.almacen_origen, producto=producto)
                    # OJO AQUI: En vez de sumar, RESTAMOS usando el mismo factor para revertir el efecto
                    stock_origen.cantidad = F('cantidad') - (cantidad * tipo.factor_origen)
                    stock_origen.save()

                # Resta Inversa en Destino
                if tipo.requiere_destino and movimiento.almacen_destino and tipo.factor_destino != 0:
                    stock_destino = StockAlmacen.objects.get(almacen=movimiento.almacen_destino, producto=producto)
                    stock_destino.cantidad = F('cantidad') - (cantidad * tipo.factor_destino)
                    stock_destino.save()

            # 2. Cambiamos el estado del movimiento
            movimiento.estado = estado_anulado
            movimiento.modificado_por = usuario
            movimiento.save()

        return SuccessResponse(message="Movimiento anulado y stock revertido exitosamente.")
    
    
class MovimientoDetalleViewSet(RestViewSet):
    queryset = MovimientoDetalle.objects.filter(fecha_eliminacion__isnull=True)
    serializer_class = MovimientoDetalleSerializer