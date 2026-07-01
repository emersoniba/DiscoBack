from typing import List, Optional

from rest_framework import serializers
from django.utils.text import slugify
from django.db import transaction
from .models import (
    Categoria, Producto, ProductoImagen, 
    Almacen, StockAlmacen, TipoMovimiento, Movimiento, MovimientoDetalle
)

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'slug', 'descripcion', 'imagen', 'orden', 'activo']
        read_only_fields = ['id', 'slug']

class ProductoImagenSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductoImagen
        fields = ['id', 'imagen', 'imagen_url', 'orden', 'activo']
        read_only_fields = ['id']
    
    def get_imagen_url(self, obj) -> Optional[str]:
        if obj.imagen:
            return obj.imagen.url
        return None

class StockAlmacenSerializer(serializers.ModelSerializer):
    almacen_nombre = serializers.CharField(source='almacen.nombre', read_only=True)
    
    class Meta:
        model = StockAlmacen
        fields = ['id', 'almacen', 'almacen_nombre', 'cantidad', 'stock_minimo']

class ProductoListSerializer(serializers.ModelSerializer):
    categoria_nombres = serializers.SerializerMethodField()
    categoria_ids = serializers.SerializerMethodField()
    precio_actual = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    imagen_principal_url = serializers.SerializerMethodField()
    
    # Nuevos campos calculados para el stock global y detalle por almacén
    stock_total = serializers.IntegerField(read_only=True)
    stocks = StockAlmacenSerializer(many=True, read_only=True)
    tiene_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'slug', 'descripcion_corta',
            'precio', 'precio_oferta', 'precio_actual', 'activo', 'imagen_principal_url',
            'destacado', 'oferta', 'tiene_stock', 'stock_total', 'stocks',
            'categoria_nombres', 'categoria_ids'
        ]
    
    def get_categoria_nombres(self, obj) -> List[str]:
        return [cat.nombre for cat in obj.categorias.all()]
    
    def get_categoria_ids(self, obj) -> List[int]:
        return [cat.id for cat in obj.categorias.all()]
    
    def get_imagen_principal_url(self, obj) -> Optional[str]:
        if obj.imagen_principal:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen_principal.url)
            return obj.imagen_principal.url
        return None

    def get_tiene_stock(self, obj) -> bool:
        return obj.stock_total > 0

class ProductoDetailSerializer(serializers.ModelSerializer):
    categorias = CategoriaSerializer(many=True, read_only=True)
    categoria_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Categoria.objects.filter(activo=True),
        source='categorias',
        write_only=True,
        required=False
    )
    imagenes = ProductoImagenSerializer(many=True, read_only=True)
    imagen_principal_url = serializers.SerializerMethodField()
    precio_actual = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    stock_total = serializers.IntegerField(read_only=True)
    stocks = StockAlmacenSerializer(many=True, read_only=True)
    tiene_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'slug', 'descripcion_corta',
            'precio', 'precio_oferta', 'imagen_principal', 'imagen_principal_url', 
            'imagenes', 'categorias', 'categoria_ids',
            'destacado', 'oferta', 'activo', 'precio_actual', 
            'tiene_stock', 'stock_total', 'stocks',
            'creado_por', 'modificado_por', 'fecha_creacion', 'fecha_modificacion',
        ]
        read_only_fields = [
            'id', 'slug', 'creado_por', 'modificado_por',
            'fecha_creacion', 'fecha_modificacion'
        ]
    
    def get_imagen_principal_url(self, obj) -> Optional[str]:
        if obj.imagen_principal:
            return obj.imagen_principal.url
        return None

    def get_tiene_stock(self, obj) -> bool:
        return obj.stock_total > 0
    
    def create(self, validated_data):
        categorias = validated_data.pop('categorias', [])
        if not validated_data.get('slug'):
            validated_data['slug'] = slugify(validated_data['nombre'])
        
        producto = Producto.objects.create(**validated_data)
        if categorias:
            producto.categorias.set(categorias)
        return producto
    
    def update(self, instance, validated_data):
        categorias = validated_data.pop('categorias', None)
        if 'nombre' in validated_data:
            instance.slug = slugify(validated_data['nombre'])
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if categorias is not None:
            instance.categorias.set(categorias)
        return instance

# --- SERIALIZERS DE INVENTARIO ---

class AlmacenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Almacen
        fields = '__all__'
        read_only_fields = ['creado_por', 'modificado_por', 'fecha_creacion', 'fecha_modificacion']

class TipoMovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoMovimiento
        fields = '__all__'
        read_only_fields = ['creado_por', 'modificado_por', 'fecha_creacion', 'fecha_modificacion']

class MovimientoDetalleSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = MovimientoDetalle
        fields = ['id', 'producto', 'producto_nombre', 'cantidad']

class MovimientoSerializer(serializers.ModelSerializer):
    detalles = MovimientoDetalleSerializer(many=True)
    tipo_movimiento_nombre = serializers.CharField(source='tipo_movimiento.nombre', read_only=True)

    class Meta:
        model = Movimiento
        fields = [
            'id', 'tipo_movimiento', 'tipo_movimiento_nombre', 'almacen_origen', 
            'almacen_destino', 'observacion', 'comprobante', 'detalles', 'fecha_creacion'
        ]
        read_only_fields = ['fecha_creacion']

    @transaction.atomic
    def create(self, validated_data, **kwargs):
        detalles_data = validated_data.pop('detalles')
        creador = kwargs.get('creado_por') or (
            self.context.get('request').user if self.context.get('request') else None
        )
        if creador is None:
            raise serializers.ValidationError(
                "No se pudo determinar el usuario creador para el movimiento."
            )

        validated_data.pop('creado_por', None)
        validated_data.pop('fecha_creacion', None)

        movimiento = Movimiento.objects.create(creado_por=creador, **validated_data)
        tipo = movimiento.tipo_movimiento

        for detalle in detalles_data:
            producto = detalle['producto']
            cantidad = detalle['cantidad']
            
            MovimientoDetalle.objects.create(
                movimiento=movimiento,
                creado_por=creador,
                **detalle
            )

            # LÓGICA DE ACTUALIZACIÓN DE STOCK POR ALMACÉN
            if tipo.factor_origen != 0 and movimiento.almacen_origen:
                stock_origen, created = StockAlmacen.objects.get_or_create(
                    almacen=movimiento.almacen_origen,
                    producto=producto,
                    defaults={'cantidad': 0, 'creado_por': creador}
                )
                stock_origen.cantidad += (cantidad * tipo.factor_origen)
                stock_origen.save()

            if tipo.factor_destino != 0 and movimiento.almacen_destino:
                stock_destino, created = StockAlmacen.objects.get_or_create(
                    almacen=movimiento.almacen_destino,
                    producto=producto,
                    defaults={'cantidad': 0, 'creado_por': creador}
                )
                stock_destino.cantidad += (cantidad * tipo.factor_destino)
                stock_destino.save()

        return movimiento