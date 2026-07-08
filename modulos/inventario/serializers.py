# inventario/serializers.py
from rest_framework import serializers
from .models import (
    UnidadMedida, TipoProducto, Categoria, TipoAlmacen, 
    Almacen, Producto, ProductoImagen, RecetaDetalle, StockAlmacen
)

class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = '__all__'
        read_only_fields = ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion', 'eliminado_por', 'fecha_eliminacion')

class TipoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoProducto
        fields = '__all__'
        read_only_fields = ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion', 'eliminado_por', 'fecha_eliminacion')

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion', 'eliminado_por', 'fecha_eliminacion')

class TipoAlmacenSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAlmacen
        fields = '__all__'
        read_only_fields = ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion', 'eliminado_por', 'fecha_eliminacion')

class AlmacenSerializer(serializers.ModelSerializer):
    # Opcional: Mostrar el nombre del tipo de almacén en modo lectura
    tipo_almacen_nombre = serializers.CharField(source='tipo_almacen.nombre', read_only=True)

    class Meta:
        model = Almacen
        fields = '__all__'
        read_only_fields = ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion', 'eliminado_por', 'fecha_eliminacion')

class ProductoImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoImagen
        fields = '__all__'
        # Este modelo hereda de models.Model normal, no tiene campos de auditoría

class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    unidad_medida_abreviatura = serializers.CharField(source='unidad_medida.abreviatura', read_only=True)
    imagenes = ProductoImagenSerializer(many=True, read_only=True) # Anidamos las imágenes para el frontend
    stock_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    class Meta:
        model = Producto
        fields = '__all__'
        read_only_fields = ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion', 'eliminado_por', 'fecha_eliminacion')

class RecetaDetalleSerializer(serializers.ModelSerializer):
    insumo_nombre = serializers.CharField(source='insumo.nombre', read_only=True)
    unidad_medida = serializers.CharField(source='insumo.unidad_medida.abreviatura', read_only=True)

    class Meta:
        model = RecetaDetalle
        fields = '__all__'
        read_only_fields = ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion', 'eliminado_por', 'fecha_eliminacion')

class StockAlmacenSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    almacen_nombre = serializers.CharField(source='almacen.nombre', read_only=True)

    class Meta:
        model = StockAlmacen
        fields = '__all__'
        read_only_fields = ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion', 'eliminado_por', 'fecha_eliminacion')