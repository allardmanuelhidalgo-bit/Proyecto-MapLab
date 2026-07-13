# Archivo base para backend/main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from geopy.distance import geodesic
from typing import List

from .database import engine, Base, SessionLocal
from . import models  # necesario: registra las tablas en Base.metadata
from . import schemas

# Crea las tablas si no existen (no borra ni toca las que ya están)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MapLab - Comparador de precios")


# --- Dependencia: una sesión de DB por request, que se cierra sola al terminar ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Endpoint simple: listar productos (sirve para que el frontend arme un buscador/autocompletar) ---
@app.get("/productos", response_model=List[schemas.ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    return db.query(models.Producto).all()


# --- Registrar un producto nuevo (ej. el usuario está en la tienda y no existe en el catálogo) ---
@app.post("/productos", response_model=schemas.ProductoOut, status_code=201)
def crear_producto(datos: schemas.ProductoCreate, db: Session = Depends(get_db)):
    categoria = db.get(models.Categoria, datos.categoria_id)
    if categoria is None:
        raise HTTPException(status_code=404, detail=f"No existe una categoría con id {datos.categoria_id}")

    ya_existe = (
        db.query(models.Producto)
        .filter(
            func.lower(models.Producto.nombre) == datos.nombre.lower(),
            models.Producto.categoria_id == datos.categoria_id,
        )
        .first()
    )
    if ya_existe:
        raise HTTPException(status_code=409, detail=f"Ya existe el producto '{datos.nombre}' en esa categoría")

    producto = models.Producto(nombre=datos.nombre, marca=datos.marca, categoria_id=datos.categoria_id)
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


# --- Listar categorías (para el formulario de "producto nuevo" en el frontend) ---
@app.get("/categorias", response_model=List[schemas.CategoriaOut])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(models.Categoria).all()


# --- Endpoint simple: listar tiendas (el frontend ya lo consume en utils.py) ---
@app.get("/tiendas", response_model=List[schemas.TiendaOut])
def listar_tiendas(db: Session = Depends(get_db)):
    return db.query(models.Tienda).all()


# --- Registrar una tienda nueva (ej. el usuario está físicamente ahí y no existe en el sistema) ---
@app.post("/tiendas", response_model=schemas.TiendaOut, status_code=201)
def crear_tienda(datos: schemas.TiendaCreate, db: Session = Depends(get_db)):
    if not (-90 <= datos.latitud <= 90) or not (-180 <= datos.longitud <= 180):
        raise HTTPException(status_code=422, detail="Latitud/longitud fuera de rango")

    ya_existe = db.query(models.Tienda).filter(func.lower(models.Tienda.nombre) == datos.nombre.lower()).first()
    if ya_existe:
        raise HTTPException(status_code=409, detail=f"Ya existe una tienda registrada como '{datos.nombre}'")

    tienda = models.Tienda(
        nombre=datos.nombre,
        direccion=datos.direccion,
        latitud=datos.latitud,
        longitud=datos.longitud,
        geoapify_id=datos.geoapify_id,
    )
    db.add(tienda)
    db.commit()
    db.refresh(tienda)
    return tienda


# --- Registro simple de usuario (sin contraseña por ahora) ---
# Necesario para poder asociar quién reporta un precio y quién vota.
@app.post("/usuarios", response_model=schemas.UsuarioOut, status_code=201)
def crear_usuario(datos: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    ya_existe = db.query(models.Usuario).filter(models.Usuario.email == datos.email).first()
    if ya_existe:
        raise HTTPException(status_code=400, detail=f"Ya existe un usuario registrado con el email '{datos.email}'")

    usuario = models.Usuario(nombre=datos.nombre, email=datos.email)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


# --- Un cliente registra el precio que vio de un producto en una tienda ---
# Cada llamada crea un reporte NUEVO (fila nueva), no sobreescribe uno
# existente: así queda historial y cada reporte se puede votar por separado.
@app.post("/precios", response_model=schemas.PrecioProductoOut, status_code=201)
def registrar_precio(datos: schemas.PrecioProductoCreate, db: Session = Depends(get_db)):
    producto = db.get(models.Producto, datos.producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail=f"No existe un producto con id {datos.producto_id}")

    tienda = db.get(models.Tienda, datos.tienda_id)
    if tienda is None:
        raise HTTPException(status_code=404, detail=f"No existe una tienda con id {datos.tienda_id}")

    if datos.usuario_id is not None and db.get(models.Usuario, datos.usuario_id) is None:
        raise HTTPException(status_code=404, detail=f"No existe un usuario con id {datos.usuario_id}")

    if datos.precio <= 0:
        raise HTTPException(status_code=422, detail="El precio debe ser mayor a 0")

    nuevo_precio = models.PrecioProducto(
        producto_id=datos.producto_id,
        tienda_id=datos.tienda_id,
        usuario_id=datos.usuario_id,
        precio=datos.precio,
    )
    db.add(nuevo_precio)
    db.commit()
    db.refresh(nuevo_precio)
    return nuevo_precio


# --- Un cliente vota si un reporte de precio es cierto o falso (1 voto por usuario) ---
@app.post("/precios/{precio_id}/votar", response_model=schemas.VotoOut, status_code=201)
def votar_precio(precio_id: int, datos: schemas.VotoCreate, db: Session = Depends(get_db)):
    precio = db.get(models.PrecioProducto, precio_id)
    if precio is None:
        raise HTTPException(status_code=404, detail=f"No existe un reporte de precio con id {precio_id}")

    usuario = db.get(models.Usuario, datos.usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail=f"No existe un usuario con id {datos.usuario_id}")

    if precio.usuario_id == datos.usuario_id:
        raise HTTPException(status_code=400, detail="No puedes votar tu propio reporte de precio")

    voto = models.Voto(precio_id=precio_id, usuario_id=datos.usuario_id, es_verdadero=datos.es_verdadero)
    db.add(voto)
    try:
        db.commit()
    except IntegrityError:
        # Salta si ya existe un voto de este usuario para este precio
        # (protegido por la UniqueConstraint del modelo, no solo por este check en Python)
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya votaste sobre este reporte de precio")

    db.refresh(voto)
    return voto


# --- Lista personal de productos: agregar un producto a la lista de un usuario ---
@app.post("/listas", response_model=schemas.ItemListaOut, status_code=201)
def agregar_a_lista(datos: schemas.ItemListaCreate, db: Session = Depends(get_db)):
    usuario = db.get(models.Usuario, datos.usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail=f"No existe un usuario con id {datos.usuario_id}")

    producto = db.get(models.Producto, datos.producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail=f"No existe un producto con id {datos.producto_id}")

    item = models.ItemLista(usuario_id=datos.usuario_id, producto_id=datos.producto_id)
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ese producto ya está en tu lista")

    db.refresh(item)
    return schemas.ItemListaOut(
        id=item.id,
        producto_id=producto.id,
        producto_nombre=producto.nombre,
        marca=producto.marca,
        comprado=item.comprado,
        fecha_agregado=item.fecha_agregado,
    )


# --- Lista personal de productos: ver la lista completa de un usuario ---
@app.get("/listas/{usuario_id}", response_model=List[schemas.ItemListaOut])
def ver_lista(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.get(models.Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail=f"No existe un usuario con id {usuario_id}")

    items = (
        db.query(models.ItemLista)
        .filter(models.ItemLista.usuario_id == usuario_id)
        .order_by(models.ItemLista.fecha_agregado.desc())
        .all()
    )

    return [
        schemas.ItemListaOut(
            id=item.id,
            producto_id=item.producto.id,
            producto_nombre=item.producto.nombre,
            marca=item.producto.marca,
            comprado=item.comprado,
            fecha_agregado=item.fecha_agregado,
        )
        for item in items
    ]


# --- Lista personal de productos: marcar un item como comprado / no comprado ---
@app.patch("/listas/{item_id}", response_model=schemas.ItemListaOut)
def actualizar_item_lista(item_id: int, datos: schemas.ItemListaActualizar, db: Session = Depends(get_db)):
    item = db.get(models.ItemLista, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"No existe un item de lista con id {item_id}")

    item.comprado = datos.comprado
    db.commit()
    db.refresh(item)
    return schemas.ItemListaOut(
        id=item.id,
        producto_id=item.producto.id,
        producto_nombre=item.producto.nombre,
        marca=item.producto.marca,
        comprado=item.comprado,
        fecha_agregado=item.fecha_agregado,
    )


# --- Lista personal de productos: quitar un producto de la lista ---
@app.delete("/listas/{item_id}", status_code=204)
def quitar_de_lista(item_id: int, db: Session = Depends(get_db)):
    item = db.get(models.ItemLista, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"No existe un item de lista con id {item_id}")

    db.delete(item)
    db.commit()


# --- Endpoint principal: RF1 + RF2 juntos ---
# Busca un producto por nombre, calcula la distancia del usuario a cada tienda
# que tiene ese producto, y devuelve el precio en las N tiendas más cercanas.
@app.get("/productos/comparar", response_model=schemas.ProductoConPrecios)
def comparar_producto(
    nombre: str = Query(..., description="Nombre (o parte del nombre) del producto a buscar"),
    lat: float = Query(..., description="Latitud del usuario"),
    lon: float = Query(..., description="Longitud del usuario"),
    limite: int = Query(2, description="Cuántas tiendas cercanas devolver"),
    db: Session = Depends(get_db),
):
    # Búsqueda parcial e insensible a mayúsculas: "leche" encuentra "Leche entera 1L"
    producto = (
        db.query(models.Producto)
        .filter(func.lower(models.Producto.nombre).contains(nombre.lower()))
        .first()
    )

    if producto is None:
        raise HTTPException(status_code=404, detail=f"No se encontró ningún producto que coincida con '{nombre}'")

    # Todos los precios registrados de ese producto, cada uno con su tienda,
    # del más reciente al más viejo (para poder quedarnos con el último por tienda)
    precios_registrados = (
        db.query(models.PrecioProducto)
        .filter(models.PrecioProducto.producto_id == producto.id)
        .order_by(models.PrecioProducto.fecha_registro.desc())
        .all()
    )

    if not precios_registrados:
        raise HTTPException(status_code=404, detail=f"'{producto.nombre}' no tiene precios registrados en ninguna tienda")

    # Un producto puede tener varios reportes en la misma tienda a lo largo
    # del tiempo (RF de historial/votación); para comparar precios entre
    # tiendas solo nos interesa el reporte MÁS RECIENTE de cada tienda.
    # Como la lista ya viene ordenada de más nuevo a más viejo, el primero
    # que veamos de cada tienda_id es el vigente.
    ultimo_precio_por_tienda = {}
    for registro in precios_registrados:
        if registro.tienda_id not in ultimo_precio_por_tienda:
            ultimo_precio_por_tienda[registro.tienda_id] = registro

    ubicacion_usuario = (lat, lon)

    # Calculamos distancia real (en km) del usuario a cada tienda con precio de este producto
    precios_con_distancia = []
    for registro in ultimo_precio_por_tienda.values():
        tienda = registro.tienda
        distancia_km = geodesic(
            ubicacion_usuario,
            (tienda.latitud, tienda.longitud)
        ).km

        votos_a_favor = sum(1 for v in registro.votos if v.es_verdadero)
        votos_en_contra = sum(1 for v in registro.votos if not v.es_verdadero)

        precios_con_distancia.append(
            schemas.PrecioEnTienda(
                precio_id=registro.id,
                tienda_id=tienda.id,
                tienda_nombre=tienda.nombre,
                direccion=tienda.direccion,
                latitud=tienda.latitud,
                longitud=tienda.longitud,
                precio=registro.precio,
                fecha_registro=registro.fecha_registro,
                votos_a_favor=votos_a_favor,
                votos_en_contra=votos_en_contra,
                distancia_km=round(distancia_km, 2),
            )
        )

    # Ordenamos por cercanía y nos quedamos solo con las N tiendas más cercanas (RF2)
    precios_con_distancia.sort(key=lambda p: p.distancia_km)
    precios_mas_cercanos = precios_con_distancia[:limite]

    return schemas.ProductoConPrecios(
        producto_id=producto.id,
        producto_nombre=producto.nombre,
        marca=producto.marca,
        precios=precios_mas_cercanos,
    )