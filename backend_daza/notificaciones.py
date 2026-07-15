# backend/notificaciones.py
"""
Servicio de notificaciones asíncronas.

Usa FastAPI BackgroundTasks: el endpoint responde al cliente de inmediato
y esta función corre DESPUÉS, sin bloquear la respuesta HTTP. Reutiliza la
misma sesión de base de datos del request (en vez de abrir una nueva) para
evitar problemas de conexión entre hilos.
"""
import logging

from . import models

logging.basicConfig(
    filename="notificaciones.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)
logger = logging.getLogger("maplab.notificaciones")


def _guardar_notificacion(db, tipo: str, mensaje: str, producto_id=None, tienda_id=None):
    notif = models.Notificacion(
        tipo=tipo, mensaje=mensaje, producto_id=producto_id, tienda_id=tienda_id
    )
    db.add(notif)
    db.commit()


def procesar_nuevo_precio(precio_id: int, db):
    """Tarea en segundo plano: se dispara al registrar un precio nuevo.
    Si es el precio más bajo histórico de ese producto, notifica."""
    precio = db.get(models.PrecioProducto, precio_id)
    if precio is None:
        return

    precio_minimo = (
        db.query(models.PrecioProducto)
        .filter(models.PrecioProducto.producto_id == precio.producto_id)
        .order_by(models.PrecioProducto.precio.asc())
        .first()
    )

    if precio_minimo and precio_minimo.id == precio.id:
        mensaje = (
            f"Nuevo precio más bajo para el producto {precio.producto_id} "
            f"en la tienda {precio.tienda_id}: {precio.precio}"
        )
        logger.info(mensaje)
        _guardar_notificacion(
            db, tipo="precio_minimo", mensaje=mensaje,
            producto_id=precio.producto_id, tienda_id=precio.tienda_id,
        )


def procesar_voto(precio_id: int, db):
    """Tarea en segundo plano: se dispara al votar un reporte de precio.
    Si acumula 3+ votos en contra, lo marca como posible error."""
    precio = db.get(models.PrecioProducto, precio_id)
    if precio is None:
        return

    votos_en_contra = sum(1 for v in precio.votos if not v.es_verdadero)
    if votos_en_contra >= 3:
        mensaje = f"El reporte de precio {precio_id} acumuló {votos_en_contra} votos en contra."
        logger.info(mensaje)
        _guardar_notificacion(
            db, tipo="reporte_sospechoso", mensaje=mensaje,
            producto_id=precio.producto_id, tienda_id=precio.tienda_id,
        )