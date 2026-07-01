from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q

# Importaciones de tus utilitarios
from modulos.utilitario.viewset import RestViewSet
from modulos.utilitario.response import SuccessResponse, ErrorResponse

# Importaciones de Modelos y Serializers
from .models import (
    Categoria, Producto, ProductoImagen, 
    Almacen, StockAlmacen, TipoMovimiento, Movimiento
)
from .serializers import (
    CategoriaSerializer, ProductoListSerializer, ProductoDetailSerializer,
    AlmacenSerializer, StockAlmacenSerializer, TipoMovimientoSerializer, MovimientoSerializer
)

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 500
    page_query_param = 'page'

class CategoriaViewSet(RestViewSet):
    queryset = Categoria.objects.prefetch_related('productos')
    serializer_class = CategoriaSerializer
    pagination_class = CustomPagination
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ['list', 'retrieve'] and not self.request.user.is_authenticated:
            queryset = queryset.filter(activo=True)
        return queryset

class ProductoViewSet(RestViewSet):
    queryset = Producto.objects.prefetch_related('categorias', 'imagenes')
    pagination_class = CustomPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'retrieve']:
            return ProductoDetailSerializer
        return ProductoListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ['list', 'retrieve'] and not self.request.user.is_authenticated:
            queryset = queryset.filter(activo=True)
        
        # Filtros
        categoria_id = self.request.query_params.get('categoria', None)
        if categoria_id:
            queryset = queryset.filter(categorias__id=categoria_id)
        
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | 
                Q(descripcion_corta__icontains=search)
            )
        
        if self.request.query_params.get('destacados') == 'true':
            queryset = queryset.filter(destacado=True)
        if self.request.query_params.get('ofertas') == 'true':
            queryset = queryset.filter(oferta=True)
        
        orden = self.request.query_params.get('orden', '-fecha_creacion')
        queryset = queryset.order_by(orden)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return SuccessResponse(
            message="Producto actualizado exitosamente",
            data=serializer.data
        )
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def publicos(self, request):
        queryset = self.get_queryset().filter(activo=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(message="Productos públicos obtenidos exitosamente", data=serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def destacados(self, request):
        productos = self.get_queryset().filter(activo=True, destacado=True)[:8]
        serializer = self.get_serializer(productos, many=True)
        return SuccessResponse(message="Productos destacados obtenidos exitosamente", data=serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def ofertas(self, request):
        productos = self.get_queryset().filter(activo=True, oferta=True)[:8]
        serializer = self.get_serializer(productos, many=True)
        return SuccessResponse(message="Productos en oferta obtenidos exitosamente", data=serializer.data)

# --- VISTAS DE INVENTARIO ---

class AlmacenViewSet(RestViewSet):
    queryset = Almacen.objects.filter(activo=True)
    serializer_class = AlmacenSerializer
    permission_classes = [IsAuthenticated]

class StockAlmacenViewSet(RestViewSet):
    queryset = StockAlmacen.objects.all().select_related('almacen', 'producto')
    serializer_class = StockAlmacenSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        almacen_id = self.request.query_params.get('almacen', None)
        producto_id = self.request.query_params.get('producto', None)
        
        if almacen_id:
            queryset = queryset.filter(almacen_id=almacen_id)
        if producto_id:
            queryset = queryset.filter(producto_id=producto_id)
            
        return queryset

class TipoMovimientoViewSet(RestViewSet):
    queryset = TipoMovimiento.objects.filter(activo=True)
    serializer_class = TipoMovimientoSerializer
    permission_classes = [IsAuthenticated]

class MovimientoViewSet(RestViewSet):
    queryset = Movimiento.objects.prefetch_related('detalles__producto', 'tipo_movimiento')
    serializer_class = MovimientoSerializer
    permission_classes = [IsAuthenticated]