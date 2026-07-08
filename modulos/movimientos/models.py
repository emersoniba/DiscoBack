from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from modulos.inventario.models import Almacen, Producto
from modulos.utilitario.models import AuditoriaBase
# Importamos de tu módulo base
#from inventario.models import Almacen, Producto


class Proveedor(AuditoriaBase):
    razon_social = models.CharField(max_length=200, unique=True)
    nit = models.CharField("NIT/Documento", max_length=50, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    contacto = models.CharField("Nombre de contacto", max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.razon_social


class TipoMovimiento(AuditoriaBase):
    nombre = models.CharField(max_length=100, unique=True)
    # Estos factores te servirán para automatizar la suma/resta en el backend más adelante
    factor_origen = models.SmallIntegerField("Mult. Origen (-1, 0, 1)", default=0)
    factor_destino = models.SmallIntegerField("Mult. Destino (-1, 0, 1)", default=0)
    requiere_origen = models.BooleanField(default=False)
    requiere_destino = models.BooleanField(default=False)
    requiere_proveedor = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class EstadoMovimiento(AuditoriaBase):
    nombre = models.CharField(max_length=50, unique=True)
    permite_edicion = models.BooleanField("¿Se puede editar?", default=True)
    afecta_stock = models.BooleanField("¿Actualiza el kardex físico?", default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Movimiento(AuditoriaBase):
    tipo_movimiento = models.ForeignKey(TipoMovimiento, on_delete=models.PROTECT)
    estado = models.ForeignKey(EstadoMovimiento, on_delete=models.PROTECT)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, null=True, blank=True)
    
    almacen_origen = models.ForeignKey(
        Almacen, on_delete=models.PROTECT, related_name="salidas", null=True, blank=True
    )
    almacen_destino = models.ForeignKey(
        Almacen, on_delete=models.PROTECT, related_name="entradas", null=True, blank=True
    )

    comprobante = models.CharField("Factura/Recibo", max_length=100, blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)
    total_movimiento = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def clean(self):
        if self.tipo_movimiento.requiere_proveedor and not self.proveedor:
            raise ValidationError({"proveedor": "Requiere seleccionar un proveedor."})
        if self.tipo_movimiento.requiere_origen and not self.almacen_origen:
            raise ValidationError({"almacen_origen": "Requiere almacén de origen."})
        if self.tipo_movimiento.requiere_destino and not self.almacen_destino:
            raise ValidationError({"almacen_destino": "Requiere almacén de destino."})

    def __str__(self):
        return f"Movimiento {self.id} - {self.tipo_movimiento.nombre}"


class MovimientoDetalle(AuditoriaBase):
    movimiento = models.ForeignKey(Movimiento, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    precio_unitario_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Auto-calculamos el subtotal antes de guardar
        self.subtotal = self.cantidad * self.precio_unitario_compra
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} de {self.producto.nombre}"