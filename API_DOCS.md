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
      "tienda_id": 2,
      "tienda_nombre": "Super 99 David",
      "direccion": "Calle F Sur, San Mateo, David, Chiriquí",
      "precio": 1.35,
      "distancia_km": 0.32
    },
    {
      "tienda_id": 1,
      "tienda_nombre": "Súper Xtra David",
      "direccion": "Urbanización Brisas Davideñas, David, Chiriquí",
      "precio": 1.25,
      "distancia_km": 0.47
    }
  ]
}
```

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
