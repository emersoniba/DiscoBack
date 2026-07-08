from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProveedorViewSet, TipoMovimientoViewSet, EstadoMovimientoViewSet,
    MovimientoViewSet, MovimientoDetalleViewSet
)

router = DefaultRouter()

# Catálogos del módulo
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')
router.register(r'tipos-movimiento', TipoMovimientoViewSet, basename='tipo-movimiento')
router.register(r'estados-movimiento', EstadoMovimientoViewSet, basename='estado-movimiento')

# Transacciones
router.register(r'movimientos', MovimientoViewSet, basename='movimiento')
router.register(r'movimientos-detalle', MovimientoDetalleViewSet, basename='movimiento-detalle')

urlpatterns = [
    path('', include(router.urls)),
]