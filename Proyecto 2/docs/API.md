# Referencia del API

Base local: `http://127.0.0.1:3000/api`. Los IDs se envían explícitamente en POST. PUT acepta uno o más campos modificables; no enviar claves primarias.

## Entidades y claves

| Entidad | Clave individual en la ruta |
|---|---|
| `pais` | `/pais/:id_pais` |
| `departamento` | `/departamento/:id_departamento` |
| `municipio` | `/municipio/:id_municipio` |
| `tipo_tienda` | `/tipo_tienda/:id_tipo_tienda` |
| `tipo_identificacion` | `/tipo_identificacion/:id_tipo_identificacion` |
| `cargo` | `/cargo/:id_cargo` |
| `categoria` | `/categoria/:id_categoria` |
| `marca` | `/marca/:id_marca` |
| `estado_venta` | `/estado_venta/:id_estado_venta` |
| `metodo_pago` | `/metodo_pago/:id_metodo_pago` |
| `persona` | `/persona/:id_persona` |
| `tienda` | `/tienda/:id_tienda` |
| `empleado` | `/empleado/:id_empleado` |
| `cliente` | `/cliente/:id_cliente` |
| `producto` | `/producto/:id_producto` |
| `catalogo_producto` | `/catalogo_producto/:id_tienda/:id_producto` |
| `venta` | `/venta/:id_venta` |
| `detalle_venta` | `/detalle_venta/:id_venta/:id_producto` |
| `pago` | `/pago/:id_pago` |

Para todas: POST/GET en `/api/<entidad>` y GET/PUT/DELETE en la ruta individual. GET de listado devuelve `{data,total,limit,offset}`; usar paginación con límite de 1 a 500. Los estados del sistema tienen escritura protegida.

## Campos por entidad

### pais

| Campo | Tipo | Observación |
|---|---|---|
| `id_pais` | entero | clave |
| `nombre` | texto (80) | obligatorio en POST |

### departamento

| Campo | Tipo | Observación |
|---|---|---|
| `id_departamento` | entero | clave |
| `nombre` | texto (80) | obligatorio en POST |
| `id_pais` | entero | obligatorio en POST |

### municipio

| Campo | Tipo | Observación |
|---|---|---|
| `id_municipio` | entero | clave |
| `nombre` | texto (80) | obligatorio en POST |
| `id_departamento` | entero | obligatorio en POST |

### tipo_tienda

| Campo | Tipo | Observación |
|---|---|---|
| `id_tipo_tienda` | entero | clave |
| `nombre` | texto (80) | obligatorio en POST |

### tipo_identificacion

| Campo | Tipo | Observación |
|---|---|---|
| `id_tipo_identificacion` | entero | clave |
| `nombre` | texto (50) | obligatorio en POST |

### cargo

| Campo | Tipo | Observación |
|---|---|---|
| `id_cargo` | entero | clave |
| `nombre` | texto (80) | obligatorio en POST |

### categoria

| Campo | Tipo | Observación |
|---|---|---|
| `id_categoria` | entero | clave |
| `nombre` | texto (80) | obligatorio en POST |

### marca

| Campo | Tipo | Observación |
|---|---|---|
| `id_marca` | entero | clave |
| `nombre` | texto (80) | obligatorio en POST |

### estado_venta

| Campo | Tipo | Observación |
|---|---|---|
| `id_estado_venta` | entero | clave |
| `nombre` | texto (30) | obligatorio en POST |

### metodo_pago

| Campo | Tipo | Observación |
|---|---|---|
| `id_metodo_pago` | entero | clave |
| `nombre` | texto (80) | obligatorio en POST |

### persona

| Campo | Tipo | Observación |
|---|---|---|
| `id_persona` | entero | clave |
| `nombres` | texto (100) | obligatorio en POST |
| `apellidos` | texto (100) | obligatorio en POST |
| `telefono` | texto (25) | obligatorio en POST |
| `correo` | texto (150) | nullable |
| `direccion` | texto (200) | obligatorio en POST |
| `id_municipio` | entero | obligatorio en POST |

### tienda

| Campo | Tipo | Observación |
|---|---|---|
| `id_tienda` | entero | clave |
| `nombre` | texto (120) | obligatorio en POST |
| `direccion` | texto (200) | obligatorio en POST |
| `telefono` | texto (25) | obligatorio en POST |
| `id_municipio` | entero | obligatorio en POST |
| `id_tipo_tienda` | entero | obligatorio en POST |

### empleado

| Campo | Tipo | Observación |
|---|---|---|
| `id_empleado` | entero | clave |
| `fecha_contratacion` | fecha/hora UTC | obligatorio en POST |
| `id_tienda` | entero | obligatorio en POST |
| `id_cargo` | entero | obligatorio en POST |
| `id_persona` | entero | obligatorio en POST |

### cliente

| Campo | Tipo | Observación |
|---|---|---|
| `id_cliente` | entero | clave |
| `id_tipo_identificacion` | entero | obligatorio en POST |
| `numero_identificacion` | texto (30) | obligatorio en POST |
| `id_persona` | entero | obligatorio en POST |

### producto

| Campo | Tipo | Observación |
|---|---|---|
| `id_producto` | entero | clave |
| `nombre` | texto (120) | obligatorio en POST |
| `descripcion` | texto (300) | obligatorio en POST |
| `id_categoria` | entero | obligatorio en POST |
| `id_marca` | entero | obligatorio en POST |

### catalogo_producto

| Campo | Tipo | Observación |
|---|---|---|
| `precio_vigente` | decimal(12,2) | obligatorio en POST |
| `existencia_actual` | entero | obligatorio en POST |
| `id_tienda` | entero | clave |
| `id_producto` | entero | clave |

### venta

| Campo | Tipo | Observación |
|---|---|---|
| `id_venta` | entero | clave |
| `fecha_venta` | fecha/hora UTC | obligatorio en POST |
| `id_tienda` | entero | obligatorio en POST |
| `id_empleado` | entero | obligatorio en POST |
| `id_cliente` | entero | obligatorio en POST |
| `id_estado_venta` | entero | obligatorio en POST |

### detalle_venta

| Campo | Tipo | Observación |
|---|---|---|
| `cantidad` | entero | obligatorio en POST |
| `precio_unitario` | decimal(12,2) | obligatorio en POST |
| `subtotal` | decimal(12,2) | obligatorio en POST |
| `id_venta` | entero | clave |
| `id_producto` | entero | clave |

### pago

| Campo | Tipo | Observación |
|---|---|---|
| `id_pago` | entero | clave |
| `monto` | decimal(12,2) | obligatorio en POST |
| `id_metodo_pago` | entero | obligatorio en POST |
| `id_venta` | entero | obligatorio en POST |

## Rutas adicionales

- `GET /health`: conexión con el motor.
- `GET /admin/importacion`: estado de la carga.
- `POST /admin/importacion`: archivo histórico completo; requiere habilitación y cabecera `X-Import-Key`.
- `POST /detalle_venta/lote` y `POST /pago/lote`: array de 1–100 registros, operación atómica.
- `GET /reportes/ventas-ubicacion`, `/reportes/top-productos`, `/reportes/saldos-pendientes`: `{data: [...]}`.

GET de ventas agrega `estado`, `total_venta`, `total_pagado` y `saldo_pendiente`. Las validaciones y restricciones se describen en el README.
