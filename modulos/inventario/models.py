# inventario/models.py
from django.db import models
from django.core.validators import MinValueValidator
from modulos.utilitario.models import AuditoriaBase

# ==========================================
# CATÁLOGOS BASE 
# ==========================================

class UnidadMedida(AuditoriaBase):
    nombre = models.CharField(max_length=50, unique=True)
    abreviatura = models.CharField(max_length=10, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.abreviatura})"

class TipoProducto(AuditoriaBase):
    nombre = models.CharField(max_length=50, unique=True)
    requiere_receta = models.BooleanField("¿Es un producto preparado?", default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Categoria(AuditoriaBase):
    nombre = models.CharField("Nombre", max_length=100, unique=True)
    descripcion = models.TextField("Descripción", blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class TipoAlmacen(AuditoriaBase):
    nombre = models.CharField(max_length=50, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

# ==========================================
# ENTIDADES PRINCIPALES (Catálogo Maestro)
# ==========================================

class Almacen(AuditoriaBase):
    nombre = models.CharField(max_length=150, unique=True)
    tipo_almacen = models.ForeignKey(TipoAlmacen, on_delete=models.PROTECT)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Producto(AuditoriaBase):
    nombre = models.CharField("Nombre", max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="productos")
    tipo_producto = models.ForeignKey(TipoProducto, on_delete=models.PROTECT)
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT)
    precio_venta = models.DecimalField(
        "Precio Venta", max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    costo_promedio = models.DecimalField("Costo Promedio", max_digits=10, decimal_places=2, default=0)
    capacidad = models.DecimalField(
        "Capacidad por unidad (Ej: 750)", max_digits=10, decimal_places=2, default=1
    )
    activo = models.BooleanField(default=True)
    imagen_principal = models.ImageField("Imagen Principal", upload_to="productos/", null=True, blank=True)

    def __str__(self):
        return self.nombre

class ProductoImagen(models.Model):
    producto = models.ForeignKey(Producto, related_name="imagenes", on_delete=models.CASCADE)
    imagen = models.ImageField("Imagen", upload_to="productos/")
    orden = models.PositiveIntegerField("Orden de visualización", default=0)
    activo = models.BooleanField("Imagen activa", default=True)

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return f"Imagen {self.orden} de {self.producto.nombre}"

class RecetaDetalle(AuditoriaBase):
    producto_preparado = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="ingredientes")
    insumo = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="usado_en")
    cantidad_necesaria = models.DecimalField("Cantidad a descontar", max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad_necesaria} {self.insumo.unidad_medida.abreviatura} de {self.insumo.nombre}"

# ==========================================
# STOCK FÍSICO (Estado Actual)
# ==========================================

class StockAlmacen(AuditoriaBase):
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name="stocks")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="stocks")
    cantidad = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=5)

    class Meta:
        unique_together = ("almacen", "producto")

    def __str__(self):
        return f"{self.producto.nombre}: {self.cantidad} en {self.almacen.nombre}"