# inventario/views.py
from modulos.utilitario.viewset import RestViewSet, RestViewSetSimple

from .models import (
    UnidadMedida, TipoProducto, Categoria, TipoAlmacen, 
    Almacen, Producto, ProductoImagen, RecetaDetalle, StockAlmacen
)
from .serializers import (
    UnidadMedidaSerializer, TipoProductoSerializer, CategoriaSerializer, 
    TipoAlmacenSerializer, AlmacenSerializer, ProductoSerializer, 
    ProductoImagenSerializer, RecetaDetalleSerializer, StockAlmacenSerializer
)

class UnidadMedidaViewSet(RestViewSet):
    queryset = UnidadMedida.objects.filter(fecha_eliminacion__isnull=True)
    serializer_class = UnidadMedidaSerializer

class TipoProductoViewSet(RestViewSet):
    queryset = TipoProducto.objects.filter(fecha_eliminacion__isnull=True)
    serializer_class = TipoProductoSerializer

class CategoriaViewSet(RestViewSet):
    queryset = Categoria.objects.filter(fecha_eliminacion__isnull=True)
    serializer_class = CategoriaSerializer

class TipoAlmacenViewSet(RestViewSet):
    queryset = TipoAlmacen.objects.filter(fecha_eliminacion__isnull=True)
    serializer_class = TipoAlmacenSerializer

class AlmacenViewSet(RestViewSet):
    queryset = Almacen.objects.filter(fecha_eliminacion__isnull=True)
    serializer_class = AlmacenSerializer

class ProductoViewSet(RestViewSet):
    queryset = Producto.objects.filter(fecha_eliminacion__isnull=True)
    serializer_class = ProductoSerializer

class ProductoImagenViewSet(RestViewSetSimple):
    """
    Usa RestViewSetSimple porque hereda de models.Model estándar
    y requiere hard-delete sin campos de auditoría.
    """
    queryset = ProductoImagen.objects.all()
    serializer_class = ProductoImagenSerializer

class RecetaDetalleViewSet(RestViewSet):
    queryset = RecetaDetalle.objects.filter(fecha_eliminacion__isnull=True)
    serializer_class = RecetaDetalleSerializer

class StockAlmacenViewSet(RestViewSet):
    queryset = StockAlmacen.objects.filter(fecha_eliminacion__isnull=True)
    serializer_class = StockAlmacenSerializer