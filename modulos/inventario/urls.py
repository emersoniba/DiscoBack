# inventario/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UnidadMedidaViewSet, TipoProductoViewSet, CategoriaViewSet, 
    TipoAlmacenViewSet, AlmacenViewSet, ProductoViewSet, 
    ProductoImagenViewSet, RecetaDetalleViewSet, StockAlmacenViewSet
)

# Instanciamos el router
router = DefaultRouter()

# 1. Catálogos Base
router.register(r'unidades-medida', UnidadMedidaViewSet, basename='unidad-medida')
router.register(r'tipos-producto', TipoProductoViewSet, basename='tipo-producto')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'tipos-almacen', TipoAlmacenViewSet, basename='tipo-almacen')

# 2. Entidades Principales
router.register(r'almacenes', AlmacenViewSet, basename='almacen')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'producto-imagenes', ProductoImagenViewSet, basename='producto-imagen')
router.register(r'recetas-detalle', RecetaDetalleViewSet, basename='receta-detalle')

# 3. Stock Físico
router.register(r'stock', StockAlmacenViewSet, basename='stock-almacen')

urlpatterns = [
    # Incluimos todas las rutas generadas por el router
    path('', include(router.urls)),
]