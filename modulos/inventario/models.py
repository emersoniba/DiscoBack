# inventario/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum

from modulos.utilitario.models import AuditoriaBase

class Categoria(AuditoriaBase):
    nombre = models.CharField("Nombre", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=100, unique=True)
    descripcion = models.TextField("Descripción", blank=True)
    imagen = models.TextField("Imagen (base64)", blank=True, null=True)
    orden = models.IntegerField("Orden", default=0)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Producto(AuditoriaBase):
    nombre = models.CharField("Nombre", max_length=200)
    slug = models.SlugField("Slug", max_length=200, blank=True)
    descripcion_corta = models.TextField("Descripción corta", max_length=500)
    precio = models.DecimalField("Precio", max_digits=10, decimal_places=2)
    precio_oferta = models.DecimalField("Precio oferta", max_digits=10, decimal_places=2, null=True, blank=True)
    imagen_principal = models.ImageField(upload_to="productos/", null=True, blank=True)
    categorias = models.ManyToManyField(Categoria, related_name="productos")
    
    # Características
    destacado = models.BooleanField("Producto destacado", default=False)
    oferta = models.BooleanField("En oferta", default=False)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    @property
    def precio_actual(self):
        if self.oferta and self.precio_oferta:
            return self.precio_oferta
        return self.precio

    @property
    def stock_total(self):
        # Calcula el stock sumando todos los almacenes/barras
        total = self.stocks.aggregate(total=Sum('cantidad'))['total']
        return total if total else 0


class ProductoImagen(models.Model):
    producto = models.ForeignKey(Producto, related_name="imagenes", on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to="productos/")
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden"]


# ==========================================
# NUEVOS MODELOS DE INVENTARIO (CERO CHOICES)
# ==========================================

class Almacen(AuditoriaBase):
    """Representa la Bodega Principal, Barra 1, Barra VIP, etc."""
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class StockAlmacen(AuditoriaBase):
    """Stock específico de un producto en una barra o bodega específica"""
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name="stocks")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="stocks")
    cantidad = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5)

    class Meta:
        unique_together = ('almacen', 'producto')

    def __str__(self):
        return f"{self.producto.nombre} en {self.almacen.nombre}: {self.cantidad}"


class TipoMovimiento(AuditoriaBase):
    """
    Configurable por ID. Ejemplos:
    ID 1: "Compra a Proveedor" -> factor_origen=0, factor_destino=1 (Suma al destino)
    ID 2: "Venta en Barra" -> factor_origen=-1, factor_destino=0 (Resta al origen)
    ID 3: "Traspaso a Barra" -> factor_origen=-1, factor_destino=1 (Resta origen, suma destino)
    ID 4: "Merma/Rotura" -> factor_origen=-1, factor_destino=0
    """
    nombre = models.CharField(max_length=100, unique=True)
    factor_origen = models.SmallIntegerField("Multiplicador Origen", default=0, help_text="-1 resta, 0 no afecta, 1 suma")
    factor_destino = models.SmallIntegerField("Multiplicador Destino", default=0, help_text="-1 resta, 0 no afecta, 1 suma")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Movimiento(AuditoriaBase):
    """Cabecera del movimiento de inventario"""
    tipo_movimiento = models.ForeignKey(TipoMovimiento, on_delete=models.PROTECT)
    almacen_origen = models.ForeignKey(Almacen, on_delete=models.PROTECT, related_name="movimientos_origen", null=True, blank=True)
    almacen_destino = models.ForeignKey(Almacen, on_delete=models.PROTECT, related_name="movimientos_destino", null=True, blank=True)
    observacion = models.TextField(blank=True, null=True)
    comprobante = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Movimiento {self.id} - {self.tipo_movimiento.nombre}"


class MovimientoDetalle(AuditoriaBase):
    """Los productos específicos que se movieron"""
    movimiento = models.ForeignKey(Movimiento, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"