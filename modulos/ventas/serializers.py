from rest_framework import serializers
from django.db import transaction
from django.db.models import F

from modulos.inventario.models import StockAlmacen
from .models import Cliente, MetodoPago, Venta, VentaDetalle

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = (
            "creado_por",
            "fecha_creacion",
            "modificado_por",
            "fecha_modificacion",
            "eliminado_por",
            "fecha_eliminacion",
        )

class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = '__all__'
        read_only_fields = (
            "creado_por",
            "fecha_creacion",
            "modificado_por",
            "fecha_modificacion",
            "eliminado_por",
            "fecha_eliminacion",
        )

class VentaDetalleSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = VentaDetalle
        fields = '__all__'
        read_only_fields = (
            'venta', 'subtotal',
            'creado_por', 'fecha_creacion', 'modificado_por', 
            'fecha_modificacion', 'eliminado_por', 'fecha_eliminacion'
        )

class VentaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    metodo_pago_nombre = serializers.CharField(source='metodo_pago.nombre', read_only=True)
    detalles = VentaDetalleSerializer(many=True)

    class Meta:
        model = Venta
        fields = '__all__'
        read_only_fields = (
            'creado_por', 'fecha_creacion', 'modificado_por', 
            'fecha_modificacion', 'eliminado_por', 'fecha_eliminacion'
        )

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        #usuario = self.context['request'].user
        usuario = validated_data.pop('creado_por', self.context['request'].user)

        with transaction.atomic():
            # 1. Registramos la cabecera de la venta
            venta = Venta.objects.create(**validated_data, creado_por=usuario)
            
            # 2. Iteramos el carrito de compras
            for detalle_data in detalles_data:
                producto = detalle_data['producto']
                cantidad = detalle_data['cantidad']
                precio = detalle_data['precio_unitario']
                
                # Guardamos la línea de detalle
                VentaDetalle.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    creado_por=usuario
                )

                # 3. ¡LA MAGIA DEL STOCK! 
                # Buscamos el stock de ese producto en la barra/almacén desde donde se está vendiendo
                stock, _ = StockAlmacen.objects.get_or_create(
                    almacen=venta.almacen,
                    producto=producto,
                    defaults={'cantidad': 0, 'creado_por': usuario}
                )
                
                # Restamos la cantidad vendida usando F() para seguridad en base de datos
                stock.cantidad = F('cantidad') - cantidad
                stock.save()

            return venta