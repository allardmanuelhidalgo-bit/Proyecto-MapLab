"""
Script para poblar la base de datos con datos de prueba.
Se corre UNA sola vez (o cada vez que se quiera resetear la data de ejemplo).

Uso:
    python seed.py
"""
from backend.database import SessionLocal, engine, Base
from backend.models import Categoria, Producto, Tienda, PrecioProducto, Usuario, Voto

# Nos aseguramos de que las tablas existan antes de insertar
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # --- Categorías ---
    categoria_lacteos = Categoria(nombre="Lácteos")
    categoria_abarrotes = Categoria(nombre="Abarrotes")
    categoria_limpieza = Categoria(nombre="Limpieza")
    db.add_all([categoria_lacteos, categoria_abarrotes, categoria_limpieza])
    db.commit()

    # --- Tiendas reales, cercanas entre sí en David, Chiriquí ---
    tienda_xtra = Tienda(
        nombre="Súper Xtra David",
        direccion="Urbanización Brisas Davideñas, David, Chiriquí",
        latitud=8.4286421,
        longitud=-82.4442399,
    )
    tienda_99 = Tienda(
        nombre="Super 99 David",
        direccion="Calle F Sur, San Mateo, David, Chiriquí",
        latitud=8.4280232,
        longitud=-82.4370701,
    )
    db.add_all([tienda_xtra, tienda_99])
    db.commit()

    # --- Productos ---
    productos = [
        Producto(nombre="Leche entera 1L", marca="Estrella Azul", categoria_id=categoria_lacteos.id),
        Producto(nombre="Queso blanco 500g", marca="Coclé", categoria_id=categoria_lacteos.id),
        Producto(nombre="Arroz 1lb", marca="Riso", categoria_id=categoria_abarrotes.id),
        Producto(nombre="Aceite vegetal 1L", marca="Bella Vista", categoria_id=categoria_abarrotes.id),
        Producto(nombre="Azúcar blanca 1lb", marca="Los Ángeles", categoria_id=categoria_abarrotes.id),
        Producto(nombre="Detergente líquido 1L", marca="Ace", categoria_id=categoria_limpieza.id),
        Producto(nombre="Papel higiénico x4", marca="Scott", categoria_id=categoria_limpieza.id),
    ]
    db.add_all(productos)
    db.commit()

    # --- Precios: mismo producto, precio distinto según la tienda ---
    precios = [
        # producto, tienda, precio
        (productos[0], tienda_xtra, 1.25),
        (productos[0], tienda_99, 1.35),

        (productos[1], tienda_xtra, 3.50),
        (productos[1], tienda_99, 3.20),

        (productos[2], tienda_xtra, 0.65),
        (productos[2], tienda_99, 0.70),

        (productos[3], tienda_xtra, 2.90),
        (productos[3], tienda_99, 3.10),

        (productos[4], tienda_xtra, 0.55),
        (productos[4], tienda_99, 0.60),

        (productos[5], tienda_xtra, 4.25),
        (productos[5], tienda_99, 3.95),

        (productos[6], tienda_xtra, 5.10),
        (productos[6], tienda_99, 5.40),
    ]

    filas_precio = []
    for producto, tienda, precio in precios:
        fila = PrecioProducto(producto_id=producto.id, tienda_id=tienda.id, precio=precio)
        db.add(fila)
        filas_precio.append(fila)

    db.commit()

    # --- Usuarios y votos de ejemplo (para poder probar /votar de una vez) ---
    usuario_ana = Usuario(nombre="Ana Pérez", email="ana@example.com")
    usuario_luis = Usuario(nombre="Luis Gómez", email="luis@example.com")
    db.add_all([usuario_ana, usuario_luis])
    db.commit()

    # Ambos votan sobre el primer precio registrado (leche en Súper Xtra)
    db.add_all([
        Voto(precio_id=filas_precio[0].id, usuario_id=usuario_ana.id, es_verdadero=True),
        Voto(precio_id=filas_precio[0].id, usuario_id=usuario_luis.id, es_verdadero=True),
    ])
    db.commit()

    print("Listo: categorías, productos, tiendas, precios, usuarios y votos de prueba insertados.")

except Exception as e:
    db.rollback()
    print(f"Ocurrió un error, se revirtió todo: {e}")
    raise

finally:
    db.close()