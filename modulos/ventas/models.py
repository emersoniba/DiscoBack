from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator

from modulos.utilitario.models import AuditoriaBase
from modulos.inventario.models import Almacen, Producto

class Cliente(AuditoriaBase):
    nombre = models.CharField("Nombre o Razón Social", max_length=200, default="Sin Nombre")
    nit_ci = models.CharField("NIT/CI", max_length=50, blank=True, null=True)
    
    def __str__(self):
        return self.nombre

class MetodoPago(AuditoriaBase):
    nombre = models.CharField(max_length=50) # Ej: Efectivo, Tarjeta, QR, Transferencia
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Venta(AuditoriaBase):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    almacen = models.ForeignKey(Almacen, on_delete=models.PROTECT, help_text="Almacén o Barra de donde sale el producto")
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT)
    
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, default='Completada') # Podría ser 'Anulada' más adelante

    def __str__(self):
        return f"Venta {self.id} - Bs. {self.total}"

class VentaDetalle(AuditoriaBase):
    venta = models.ForeignKey(Venta, related_name="detalles", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    #cantidad = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)