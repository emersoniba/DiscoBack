from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriaViewSet, 
    ProductoViewSet, 
    AlmacenViewSet, 
    StockAlmacenViewSet, 
    TipoMovimientoViewSet, 
    MovimientoViewSet
)

router = DefaultRouter()
# Rutas de Catálogo
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'productos', ProductoViewSet, basename='producto')

# Rutas de Inventario
router.register(r'almacenes', AlmacenViewSet, basename='almacen')
router.register(r'stock', StockAlmacenViewSet, basename='stock')
router.register(r'tipos-movimiento', TipoMovimientoViewSet, basename='tipo-movimiento')
router.register(r'movimientos', MovimientoViewSet, basename='movimiento')

urlpatterns = [
    path('', include(router.urls)),
]