# Comercial La Estrella — Proyecto Fase 2

**Alex Ricardo Castañeda Rodríguez · Carné 202300476 · Bases de Datos 1 · Segundo semestre 2026**

Repositorio: <https://github.com/ricardious/SBD1_2S2026>

API REST con Express 5, TypeScript y TypeORM. SQL Server 2022 se ejecuta en Docker y conserva las 19 tablas del modelo de la fase 1. Incluye importación de los 9,068 registros originales por HTTP, las tres vistas solicitadas, los triggers `Insert_Detalle` e `Insert_Pago`, Postman y pruebas contra el motor real. El frontend no forma parte de los entregables exigidos.

## 1. Requisitos

- Linux x86-64 con Docker Engine y el complemento `docker compose`, o Docker Desktop con contenedores Linux.
- Node.js 22 o superior y npm. Python 3 para generar credenciales y empaquetar; no se necesita Python para ejecutar el backend.
- Postman para importar las colecciones. La ejecución por terminal usa el CLI oficial incluido entre las dependencias de desarrollo.
- Memoria disponible suficiente para SQL Server: se configura un presupuesto interno de 2 GiB; reservar margen adicional para el sistema y Node. No detener contenedores de otros proyectos automáticamente.
- Puertos libres: `1433` y `3000`, modificables en `.env`.

Ejecutar los siguientes comandos **dentro de `Proyecto 2`**. Con RTK instalado pueden prefijarse con `rtk proxy`.

## 2. Crear el entorno y levantar SQL Server

```bash
python3 scripts/setup-env.py
npm ci
docker compose up -d
docker compose ps -a
docker compose logs db-init
```

El generador crea `.env` con claves aleatorias y permisos privados; no sobrescribe uno existente. No se debe versionar ni incluir en la entrega. Alternativamente, copiar `.env.example` y sustituir **todas** las claves. Las claves de los usuarios SQL requieren 16–128 caracteres de los conjuntos `A-Z`, `a-z`, `0-9`, `_`, `!` y `-`.

`sqlserver` debe aparecer saludable y `db-init` terminar con código **0** y el mensaje de inicialización completada. `docker compose up -d` espera la disponibilidad del servidor; comprobar también el resultado de `db-init`, porque el servidor saludable por sí solo no garantiza que el DDL haya terminado.

El servicio `db-init` ejecuta automáticamente `init.sql` mediante `sqlcmd`. Crea tablas, restricciones, índices, vistas, triggers y los usuarios `estrella_api` y `estrella_import`. Se puede repetir sin borrar datos:

```bash
docker compose run --rm db-init
```

La imagen de SQL Server 2022 está fijada por digest para reproducir la versión probada. Los datos se guardan en un volumen Docker. `docker compose down` conserva ese volumen; **`docker compose down -v` borra la base del proyecto**. No es parte del arranque normal. Si se cambian claves en `.env`, los logins ya existentes no se modifican automáticamente: conservar las claves originales o coordinar su rotación administrativa.

## 3. Compilar e iniciar la API

```bash
npm run build
npm start
```

En otra terminal:

```bash
curl http://127.0.0.1:3000/api/health
```

Respuesta esperada: `{"estado":"ok","database":"SQL Server 2022"}`. Para desarrollo usar `npm run dev`. La API escucha solamente en `127.0.0.1` por defecto y este proyecto está preparado para evaluación local, sin autenticación general de usuarios ni despliegue público.

## 4. Importar el histórico completo una sola vez

1. Detener la API con `Ctrl+C`.
2. Cambiar temporalmente `IMPORT_ENABLED=false` a `IMPORT_ENABLED=true` en `.env`.
3. Iniciar la API nuevamente con `npm start`.
4. Desde otra terminal ejecutar:

```bash
npm run import:historico
```

5. Comprobar `total: 9068` y `mensaje: "Historico importado y conciliado"`.
6. Detener la API, volver a `IMPORT_ENABLED=false` y reiniciarla.

El script cliente **envía una petición HTTP** a `POST /api/admin/importacion`; no escribe directamente en SQL. También se entrega una colección separada de importación: en Postman definir `importKey` de forma local, seleccionar `data/historico.json` en Body → binary y mantener `Content-Type: application/json`. No exportar la clave. El script npm es la opción reproducible para la carga; el CLI de Postman puede limitar el envío de archivos locales.

`GET /api/admin/importacion` informa si la carga terminó, su fecha, cantidad, hash y si la ruta está habilitada. Una segunda importación devuelve `409`; una ruta deshabilitada devuelve `404`. Con la ruta habilitada, una clave incorrecta devuelve `401` y un archivo diferente del histórico original devuelve `400`.

### Por qué la carga histórica es especial

El Excel de la fase 1 contiene existencias y estados históricos. Volver a procesar esos detalles como ventas nuevas descontaría el stock otra vez. Por ello:

- Se entrega una conversión JSON del Excel y un manifiesto con sus conteos; la fuente está indicada en `data/manifest.json`.
- Solo se admite ese contenido exacto, validado mediante SHA-256 canónico y validación de campos.
- La importación requiere las 19 tablas vacías, bloquea cargas simultáneas y se ejecuta en una transacción.
- Usa un login separado, miembro del rol `importador`, y un contexto de sesión temporal. Solo ambos juntos permiten omitir efectos operativos de los triggers. Las PK, FK, CHECK e índices únicos continúan activos.
- Se comparan **todos los valores** importados, incluidos fechas, importes, IDs y correos nulos. Un error revierte toda la carga.
- Se limpia el contexto y se cierra el pool de importación. El usuario del CRUD no pertenece al rol y no puede crear ni modificar objetos SQL.

El histórico trae 45 correos nulos. SQL Server conserva su unicidad mediante un índice filtrado que solo incluye correos no nulos. El histórico original permanece en 9,068 registros; ejecutar las demostraciones añade registros identificables como `QA` o `Demo` con IDs altos.

## 5. Usar y probar el API

Importar en Postman la colección principal y el entorno local de `postman/`. Con el histórico ya cargado, ejecutar **toda la colección en orden**: preparación, CRUD, limpieza de auxiliares, triggers y vistas. Los IDs se generan en la primera petición; ejecutar una carpeta aislada requiere haber creado sus dependencias.

También puede ejecutarse desde terminal:

```bash
npm run postman
npm test
npm run test:integration
```

Las pruebas de integración requieren la API iniciada y el histórico cargado. Usan únicamente HTTP para manipular datos y dejan escenarios de demostración en la base. Son pruebas con efectos reales; no ejecutarlas sobre una base de producción. Puede cambiarse el destino mediante `API_URL` en las pruebas de integración. En Postman se cambia `baseUrl`.

### Contrato de los endpoints

La referencia de todas las rutas y campos está en [API.md](docs/API.md). Para cada entidad:

| Método | Ruta | Resultado |
|---|---|---|
| POST | `/api/pais` | Crea un registro con ID explícito; `201`. |
| GET | `/api/pais?limit=100&offset=0` | `{data,total,limit,offset}`; límite máximo 500. |
| GET | `/api/pais/1` | Registro individual o `404`. |
| PUT | `/api/pais/1` | Modificación de uno o más campos; claves inmutables. |
| DELETE | `/api/pais/1` | `204`, o `409` si existen referencias/protecciones. |

Los otros nombres corresponden exactamente a las tablas. Las claves compuestas se usan en orden:

- `/api/catalogo_producto/:id_tienda/:id_producto`
- `/api/detalle_venta/:id_venta/:id_producto`

Se admiten lotes de 1–100 registros mediante `POST /api/detalle_venta/lote` y `POST /api/pago/lote`, con un array JSON. Cada lote es una sola inserción y se revierte por completo si una fila falla.

Los campos y tipos son estrictos: IDs positivos, stock no negativo, importes positivos con hasta dos decimales y fechas `YYYY-MM-DD` o `YYYY-MM-DDTHH:mm:ss`. No se admiten campos extra ni cambios de claves primarias. Las fechas se interpretan en UTC para preservar los valores del dataset sin desplazamientos. Los importes JSON son números; SQL usa `DECIMAL(12,2)`.

Errores: `{error: "mensaje"}`, con `400` para entrada inválida/stock insuficiente, `404` para inexistentes y `409` para conflictos. No se exponen consultas SQL ni credenciales en errores internos.

## 6. Reglas y reportes

- **Inventario:** pertenece a `catalogo_producto`, por tienda y producto. `Insert_Detalle` agrupa las diferencias entre `inserted` y `deleted`, valida y descuenta mediante una actualización atómica con bloqueos. Un faltante o producto sin catálogo devuelve `400` con **Stock insuficiente**, sin dejar cambios parciales.
- **Detalles:** solo pueden agregarse, modificarse o eliminarse en ventas registradas sin pagos. Cambiar cantidad ajusta la diferencia; eliminar devuelve el stock. `subtotal` debe coincidir con cantidad × precio.
- **Pagos:** `Insert_Pago` suma abonos y los compara con la suma de detalles. Al alcanzar o superar el total cambia a `PAGADA`; modificar o eliminar abonos recalcula el estado. No permite pagar ventas vacías ni anuladas. No se puede trasladar un pago a otra venta mediante PUT.
- **Ventas:** nacen `REGISTRADA`; no se pueden marcar `PAGADA` manualmente. Con detalles o pagos, no se cambian tienda, empleado, cliente ni fecha. Se permite anular una venta registrada sin pagos; devuelve stock una sola vez. Las ventas anuladas quedan protegidas. Las referencias impiden borrar una venta con detalles o pagos.
- **Catálogo:** no se elimina mientras existan detalles de venta asociados; sí permite actualizar precio o existencias.
- **Estados:** los IDs 1/2/3 corresponden a REGISTRADA/PAGADA/ANULADA. Las rutas CRUD existen, pero la base protege estos valores del sistema y responde `409` a cambios o eliminaciones.

| Endpoint GET | Vista | Contenido |
|---|---|---|
| `/api/reportes/ventas-ubicacion` | `Vista_Ventas_Ubicacion` | Tienda, municipio, departamento, país, cantidad de ventas y facturación; excluye anuladas. |
| `/api/reportes/top-productos` | `Vista_Top_Productos` | Producto, categoría, marca, unidades e importe; excluye anuladas. |
| `/api/reportes/saldos-pendientes` | `Vista_Saldos_Pendientes` | Solo registradas: total, abonado y saldo. |

`GET /api/venta/:id_venta` también devuelve nombre del estado, total, abonado y saldo mediante una vista auxiliar. Los totales de detalles y pagos se agregan por separado para evitar multiplicaciones al unirlos. El backend consulta las vistas; no reconstruye reportes con relaciones del ORM.

## 7. Arquitectura y defensa

```text
Postman / cliente de importacion
              ↓ HTTP JSON
Express → validacion → controlador CRUD → repositorio TypeORM
                                              ↓ mssql
SQL Server 2022 en Docker → restricciones / triggers / vistas
```

Cada entidad tiene un módulo de rutas. El controlador y la validación comparten un patrón a partir de metadatos declarativos; `EntitySchema` crea las entidades de TypeORM. Las relaciones y restricciones se mantienen explícitas en `init.sql`. `synchronize: false` impide que el ORM reescriba el esquema. Las operaciones usan parámetros y solo interpolan nombres tomados de listas internas.

Se deshabilita `OUTPUT` automático de TypeORM para las tablas con triggers y se vuelve a consultar el registro después de escribirlo. **Los triggers SQL son quienes descuentan y cambian estados**; no hay listeners del ORM que repliquen esa lógica.

Consultar [GUIA_PASO_A_PASO.md](docs/GUIA_PASO_A_PASO.md) para estudiar y ensayar. Las evidencias verificadas están en [evidencias](docs/evidencias/README.md).

## 8. Empaquetar la entrega

```bash
npm run package
```

Produce `entrega/[BD1]_ProyectoFase2_202300476.zip`, con la raíz del proyecto, documentación, colecciones y datos. Excluye `.env`, `node_modules`, compilados, logs y la propia carpeta de entrega. En otra máquina se generan nuevas credenciales y se ejecuta `npm ci` y `npm run build`.

Para la calificación, realizar todo CRUD desde Postman/API. DBeaver queda para inspección estructural de solo lectura. La hoja nueva penaliza no usar SQL Server 2022 en Docker y manipular datos directamente durante la evaluación con −100%; también penaliza desconocimiento e inconsistencias.

## Referencias

- [Enunciado oficial](docs/ProyectoFase2_SBD1_2S2026.pdf) y [hoja de calificación](docs/Hoja_Calificacion_Proyecto_Fase_2_BD1.pdf).
- [TypeORM y SQL Server](https://typeorm.io/docs/drivers/microsoft-sqlserver/).
- [Microsoft: triggers para múltiples filas](https://learn.microsoft.com/en-us/sql/relational-databases/triggers/create-dml-triggers-to-handle-multiple-rows-of-data?view=sql-server-ver16).
- [Microsoft: contenedores SQL Server](https://learn.microsoft.com/en-us/sql/linux/quickstart-install-connect-docker?view=sql-server-ver16).
- [Postman CLI: ejecución de colecciones](https://learning.postman.com/docs/postman-cli/postman-cli-run-collection).
