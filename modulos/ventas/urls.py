from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, MetodoPagoViewSet, VentaViewSet, VentaDetalleViewSet

router = DefaultRouter()

router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'metodos-pago', MetodoPagoViewSet, basename='metodo-pago')
router.register(r'ventas', VentaViewSet, basename='venta')
router.register(r'ventas-detalle', VentaDetalleViewSet, basename='venta-detalle')

urlpatterns = [
    path('', include(router.urls)),
]