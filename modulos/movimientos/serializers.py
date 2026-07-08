from rest_framework import serializers
from django.db import transaction
from django.db.models import F
from inventario.models import StockAlmacen  # Importamos el modelo de Stock
from .models import Proveedor, TipoMovimiento, EstadoMovimiento, Movimiento, MovimientoDetalle

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'
        read_only_fields = ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion', 'eliminado_por', 'fecha_eliminacion')

class TipoMovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoMovimiento
        fields = '__all__'
        read_only_fields = ('creado_por', 'fecha_creacion')

class EstadoMovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoMovimiento
        fields = '__all__'
        read_only_fields = ('creado_por', 'fecha_creacion')

class MovimientoDetalleSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = MovimientoDetalle
        fields = '__all__'
        # movimiento se vuelve read_only porque lo asignará el serializador padre automáticamente
        read_only_fields = ('movimiento', 'subtotal', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion', 'eliminado_por', 'fecha_eliminacion')

class MovimientoSerializer(serializers.ModelSerializer):
    tipo_movimiento_nombre = serializers.CharField(source='tipo_movimiento.nombre', read_only=True)
    estado_nombre = serializers.CharField(source='estado.nombre', read_only=True)
    proveedor_nombre = serializers.CharField(source='proveedor.razon_social', read_only=True)
    
    # Quitamos 'read_only=True' para permitir que el frontend envíe el array de detalles en el mismo JSON
    detalles = MovimientoDetalleSerializer(many=True)

    class Meta:
        model = Movimiento
        fields = '__all__'
        read_only_fields = ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion', 'eliminado_por', 'fecha_eliminacion')

    def create(self, validated_data):
        # Extraemos los detalles del JSON recibido antes de guardar la cabecera
        detalles_data = validated_data.pop('detalles', [])
        
        # Obtenemos el usuario de la petición para mantener tu lógica de auditoría
        usuario = self.context['request'].user

        # 'transaction.atomic' asegura que si algo falla con un solo producto, 
        # NADA se guarde en la BD, evitando datos a medias.
        with transaction.atomic():
            # 1. Creamos la cabecera del movimiento
            movimiento = Movimiento.objects.create(**validated_data)
            
            tipo = movimiento.tipo_movimiento
            estado = movimiento.estado

            # 2. Iteramos cada producto enviado en los detalles
            for detalle_data in detalles_data:
                producto = detalle_data['producto']
                cantidad = detalle_data['cantidad']
                precio = detalle_data.get('precio_unitario_compra', 0)

                # Guardamos la línea de detalle vinculada a este movimiento
                MovimientoDetalle.objects.create(
                    movimiento=movimiento,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario_compra=precio,
                    creado_por=usuario
                )

                # 3. LÓGICA DE ACTUALIZACIÓN DE STOCK (Solo si el estado lo exige, ej: 'Completado')
                if estado.afecta_stock:
                    
                    # CONTROL DE SALIDA: Restar del almacén de origen
                    if tipo.requiere_origen and movimiento.almacen_origen and tipo.factor_origen != 0:
                        stock_origen, _ = StockAlmacen.objects.get_or_create(
                            almacen=movimiento.almacen_origen,
                            producto=producto,
                            defaults={'cantidad': 0, 'creado_por': usuario}
                        )
                        # Multiplica la cantidad por el factor (ej: 5 * -1 = -5)
                        # F() ejecuta la operación directamente en el motor de la base de datos de manera segura
                        stock_origen.cantidad = F('cantidad') + (cantidad * tipo.factor_origen)
                        stock_origen.save()

                    # CONTROL DE INGRESO: Sumar al almacén de destino (Tu caso del Proveedor)
                    if tipo.requiere_destino and movimiento.almacen_destino and tipo.factor_destino != 0:
                        stock_destino, _ = StockAlmacen.objects.get_or_create(
                            almacen=movimiento.almacen_destino,
                            producto=producto,
                            defaults={'cantidad': 0, 'creado_por': usuario}
                        )
                        # Multiplica la cantidad por el factor (ej: 5 * 1 = 5)
                        stock_destino.cantidad = F('cantidad') + (cantidad * tipo.factor_destino)
                        stock_destino.save()

            return movimiento