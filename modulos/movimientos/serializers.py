from rest_framework import serializers
from django.db import transaction
from django.db.models import F

from modulos.inventario.models import StockAlmacen

# from inventario.models import StockAlmacen  # Importamos el modelo de Stock
from .models import (
    Proveedor,
    TipoMovimiento,
    EstadoMovimiento,
    Movimiento,
    MovimientoDetalle,
)


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = "__all__"
        read_only_fields = (
            "creado_por",
            "fecha_creacion",
            "modificado_por",
            "fecha_modificacion",
            "eliminado_por",
            "fecha_eliminacion",
        )


class TipoMovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoMovimiento
        fields = "__all__"
        read_only_fields = ("creado_por", "fecha_creacion")


class EstadoMovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoMovimiento
        fields = "__all__"
        read_only_fields = ("creado_por", "fecha_creacion")


class MovimientoDetalleSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)

    class Meta:
        model = MovimientoDetalle
        fields = "__all__"
        # movimiento se vuelve read_only porque lo asignará el serializador padre automáticamente
        read_only_fields = (
            "movimiento",
            "subtotal",
            "creado_por",
            "fecha_creacion",
            "modificado_por",
            "fecha_modificacion",
            "eliminado_por",
            "fecha_eliminacion",
        )


class MovimientoSerializer(serializers.ModelSerializer):
    tipo_movimiento_nombre = serializers.CharField(
        source="tipo_movimiento.nombre", read_only=True
    )
    estado_nombre = serializers.CharField(source="estado.nombre", read_only=True)
    proveedor_nombre = serializers.CharField(
        source="proveedor.razon_social", read_only=True
    )

    # Quitamos 'read_only=True' para permitir que el frontend envíe el array de detalles en el mismo JSON
    detalles = MovimientoDetalleSerializer(many=True)

    class Meta:
        model = Movimiento
        fields = "__all__"
        read_only_fields = (
            "creado_por",
            "fecha_creacion",
            "modificado_por",
            "fecha_modificacion",
            "eliminado_por",
            "fecha_eliminacion",
        )

    def create(self, validated_data):
        # Extraemos los detalles del JSON recibido antes de guardar la cabecera
        detalles_data = validated_data.pop("detalles", [])

        # Obtenemos el usuario de la petición para mantener tu lógica de auditoría
        usuario = self.context["request"].user

        # 'transaction.atomic' asegura que si algo falla con un solo producto,
        # NADA se guarde en la BD, evitando datos a medias.
        with transaction.atomic():
            # 1. Creamos la cabecera del movimiento
            movimiento = Movimiento.objects.create(**validated_data)

            tipo = movimiento.tipo_movimiento
            estado = movimiento.estado

            # 2. Iteramos cada producto enviado en los detalles
            for detalle_data in detalles_data:
                producto = detalle_data["producto"]
                cantidad = detalle_data["cantidad"]
                precio = detalle_data.get("precio_unitario_compra", 0)

                # Guardamos la línea de detalle vinculada a este movimiento
                MovimientoDetalle.objects.create(
                    movimiento=movimiento,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario_compra=precio,
                    creado_por=usuario,
                )

                # 3. LÓGICA DE ACTUALIZACIÓN DE STOCK (Solo si el estado lo exige, ej: 'Completado')
                if estado.afecta_stock:

                    # CONTROL DE SALIDA: Restar del almacén de origen
                    if (
                        tipo.requiere_origen
                        and movimiento.almacen_origen
                        and tipo.factor_origen != 0
                    ):
                        stock_origen, _ = StockAlmacen.objects.get_or_create(
                            almacen=movimiento.almacen_origen,
                            producto=producto,
                            defaults={"cantidad": 0, "creado_por": usuario},
                        )
                        # Multiplica la cantidad por el factor (ej: 5 * -1 = -5)
                        # F() ejecuta la operación directamente en el motor de la base de datos de manera segura
                        stock_origen.cantidad = F("cantidad") + (
                            cantidad * tipo.factor_origen
                        )
                        stock_origen.save()

                    # CONTROL DE INGRESO: Sumar al almacén de destino (Tu caso del Proveedor)
                    # CONTROL DE INGRESO: Sumar al almacén de destino
                    if (
                        tipo.requiere_destino
                        and movimiento.almacen_destino
                        and tipo.factor_destino > 0
                    ):
                        stock_destino, created = StockAlmacen.objects.get_or_create(
                            almacen=movimiento.almacen_destino,
                            producto=producto,
                            defaults={"cantidad": 0, "creado_por": usuario},
                        )

                        # --- INICIO MAGIA DEL COSTO PROMEDIO PONDERADO ---
                        # 1. Obtenemos el producto para actualizar su costo
                        prod_instancia = producto

                        # 2. Calculamos el stock total actual (antes de sumar el nuevo)
                        # Usamos sum() sobre todos los almacenes por si el producto está en varios lados
                        stock_total_anterior = sum(
                            s.cantidad for s in prod_instancia.stocks.all()
                        )
                        costo_anterior = prod_instancia.costo_promedio

                        cantidad_ingresando = cantidad
                        nuevo_costo_unitario = precio  # El que calculó Angular (ej: Costo paquete / unidades)

                        if stock_total_anterior <= 0:
                            # Si no había stock (o era negativo), el nuevo costo es directamente el de esta compra
                            prod_instancia.costo_promedio = nuevo_costo_unitario
                        else:
                            # Fórmula: ((Stock Viejo * Costo Viejo) + (Stock Nuevo * Costo Nuevo)) / (Stock Total)
                            valor_inventario_actual = (
                                stock_total_anterior * costo_anterior
                            )
                            valor_nueva_compra = (
                                cantidad_ingresando * nuevo_costo_unitario
                            )
                            nuevo_stock_total = (
                                stock_total_anterior + cantidad_ingresando
                            )

                            nuevo_costo_promedio = (
                                valor_inventario_actual + valor_nueva_compra
                            ) / nuevo_stock_total

                            prod_instancia.costo_promedio = nuevo_costo_promedio

                        # Guardamos el nuevo costo en el producto
                        prod_instancia.save()
                        # --- FIN MAGIA DEL COSTO PROMEDIO PONDERADO ---

                        # Finalmente, sumamos el stock físico usando F() para evitar colisiones
                        stock_destino.cantidad = F("cantidad") + (
                            cantidad * tipo.factor_destino
                        )
                        stock_destino.save()

            return movimiento

    def update(self, instance, validated_data):
        # 1. Seguridad: Evitar editar movimientos que ya afectaron stock
        if instance.estado.afecta_stock:
            raise serializers.ValidationError(
                {
                    "estado": "No se puede editar un movimiento que ya ha sido completado."
                }
            )

        detalles_data = validated_data.pop("detalles", None)
        usuario = self.context["request"].user

        with transaction.atomic():
            # 2. Actualizar la cabecera
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            # 3. Actualizar los detalles (Sobrescribimos por seguridad)
            if detalles_data is not None:
                # Eliminamos los detalles anteriores del borrador
                instance.detalles.all().delete()

                # Creamos los nuevos
                for detalle_data in detalles_data:
                    producto = detalle_data["producto"]
                    cantidad = detalle_data["cantidad"]
                    precio = detalle_data.get("precio_unitario_compra", 0)

                    MovimientoDetalle.objects.create(
                        movimiento=instance,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario_compra=precio,
                        creado_por=usuario,
                    )

            instance.save()
            return instance
