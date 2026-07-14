# API MapLab — Documentación rápida para consumo del endpoint

## GET /productos

Lista todos los productos disponibles (sirve para autocompletar en el buscador).

**Respuesta (200):**
```json
[
  { "id": 1, "nombre": "Leche entera 1L", "marca": "Estrella Azul", "categoria_id": 1 },
  { "id": 2, "nombre": "Queso blanco 500g", "marca": "Coclé", "categoria_id": 1 }
]
```

---

## GET /productos/comparar

Busca un producto por nombre (coincidencia parcial, no distingue mayúsculas) y devuelve
su precio en las tiendas más cercanas a una ubicación dada, ordenadas de más cercana a
más lejana.

### Parámetros (query string)

| Parámetro | Tipo  | Obligatorio | Descripción                              |
|-----------|-------|:-----------:|-------------------------------------------|
| `nombre`  | str   | Sí           | Nombre o parte del nombre del producto    |
| `lat`     | float | Sí           | Latitud del usuario                       |
| `lon`     | float | Sí           | Longitud del usuario                      |
| `limite`  | int   | No (default 2) | Cuántas tiendas cercanas devolver      |

### Ejemplo de request

```
GET /productos/comparar?nombre=leche&lat=8.4283&lon=-82.4400
```

(`8.4283, -82.4400` es un punto de referencia entre las dos tiendas de prueba en David)

### Ejemplo de response (200 OK)

```json
{
  "producto_id": 1,
  "producto_nombre": "Leche entera 1L",
  "marca": "Estrella Azul",
  "precios": [
    {
      "precio_id": 7,
      "tienda_id": 2,
      "tienda_nombre": "Super 99 David",
      "direccion": "Calle F Sur, San Mateo, David, Chiriquí",
      "latitud": 8.4280232,
      "longitud": -82.4370701,
      "precio": 1.35,
      "fecha_registro": "2026-07-10T14:32:00",
      "votos_a_favor": 3,
      "votos_en_contra": 0,
      "distancia_km": 0.32
    },
    {
      "precio_id": 5,
      "tienda_id": 1,
      "tienda_nombre": "Súper Xtra David",
      "direccion": "Urbanización Brisas Davideñas, David, Chiriquí",
      "latitud": 8.4286421,
      "longitud": -82.4442399,
      "precio": 1.25,
      "fecha_registro": "2026-07-08T09:10:00",
      "votos_a_favor": 1,
      "votos_en_contra": 1,
      "distancia_km": 0.47
    }
  ]
}
```

Notas nuevas:
- `precio_id` es el id del reporte de precio; úsalo para llamar a `POST /precios/{precio_id}/votar`.
- `latitud`/`longitud` de la tienda ya vienen incluidas para poder trazar la ruta en el mapa sin pedirlas aparte.
- Si una tienda tiene varios reportes de precio para el mismo producto, aquí solo se muestra el **más reciente**; el historial completo no se expone en este endpoint.

---

## GET /tiendas

Lista todas las tiendas registradas (para pintar el mapa inicial). Devuelve `id, nombre, direccion, latitud, longitud`.

### POST /tiendas
Registra una tienda nueva (ej. el usuario está físicamente ahí y no existe en el sistema).
**Body:** `{ "nombre": "Minisuper El Ahorro", "direccion": "Calle 3, David", "latitud": 8.43, "longitud": -82.44 }`
**201:** la tienda creada. **409** si ya existe una tienda con ese nombre. **422** si lat/lon están fuera de rango.

---

## GET /categorias
Lista todas las categorías (`id, nombre`) — se usa para armar el formulario de "producto nuevo", que pide `categoria_id`.

## POST /productos
Registra un producto nuevo que no está en el catálogo.
**Body:** `{ "nombre": "Yogurt natural", "marca": "Estrella Azul", "categoria_id": 1 }` (`marca` es opcional)
**201:** el producto creado. **404** si la categoría no existe. **409** si ya existe ese producto (mismo nombre + categoría).

---

## POST /usuarios

Registra un cliente simple (sin contraseña por ahora — pendiente decidir si se agrega login real).

**Body:** `{ "nombre": "Ana Pérez", "email": "ana@example.com" }`
**201:** el usuario creado. **400** si el email ya está registrado.

---

## POST /precios

Un cliente registra el precio que vio de un producto en una tienda. Cada llamada crea un reporte **nuevo** (no sobreescribe uno existente), así queda historial y cada reporte se puede votar por separado.

**Body:** `{ "producto_id": 1, "tienda_id": 2, "precio": 1.30, "usuario_id": 5 }` (`usuario_id` es opcional)
**201:** el reporte creado, con su `fecha_registro`. **404** si el producto/tienda/usuario no existen. **422** si el precio es <= 0.

---

## POST /precios/{precio_id}/votar

Un cliente vota si un reporte de precio es cierto o falso. Un usuario solo puede votar **una vez** por reporte, y no puede votar su propio reporte.

**Body:** `{ "usuario_id": 8, "es_verdadero": true }`
**201:** el voto registrado. **404** si el precio o el usuario no existen. **400** si intenta votar su propio reporte. **409** si ya había votado ese mismo reporte antes.

---

## Lista personal de productos

Para que un usuario guarde qué productos quiere comprar y vaya marcando cuáles ya consiguió.

### POST /listas
Agrega un producto a la lista de un usuario.
**Body:** `{ "usuario_id": 8, "producto_id": 3 }`
**201:** el item creado. **404** si el usuario o el producto no existen. **409** si ese producto ya estaba en su lista.

### GET /listas/{usuario_id}
Devuelve la lista completa de ese usuario (con nombre y marca del producto ya incluidos), la más reciente primero.

### PATCH /listas/{item_id}
Marca un item como comprado o no comprado.
**Body:** `{ "comprado": true }`

### DELETE /listas/{item_id}
Quita un producto de la lista. Responde **204** sin body.

Notas sobre este ejemplo:
- El array `precios` ya viene **ordenado por cercanía** (el frontend no necesita ordenar nada).
- Aunque Super 99 está más cerca, Súper Xtra tiene el precio más bajo (1.25 vs 1.35) —
  el frontend debería mostrar ambos datos (precio y distancia) para que el usuario decida,
  no asumir que "más cerca" = "más barato".
- Los `id` reales pueden variar según el orden en que se insertaron los datos con `seed.py`;
  no hay que hardcodearlos, el frontend siempre busca por `nombre`.

### Errores posibles

| Código | Cuándo pasa | Body de ejemplo |
|--------|-------------|------------------|
| 404 | No existe ningún producto que coincida con `nombre` | `{ "detail": "No se encontró ningún producto que coincida con 'yogurt'" }` |
| 404 | El producto existe pero no tiene precios registrados en ninguna tienda | `{ "detail": "'Yogurt natural' no tiene precios registrados en ninguna tienda" }` |
| 422 | Falta algún parámetro obligatorio o `lat`/`lon` no son números | Generado automáticamente por FastAPI |

El frontend debería mostrar el campo `detail` directamente al usuario en caso de error 404
(ej. con `st.error(respuesta.json()["detail"])`), es un mensaje ya pensado para mostrarse tal cual.
