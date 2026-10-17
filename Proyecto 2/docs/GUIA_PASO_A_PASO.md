# Guía de estudio y desarrollo por etapas

El orden sirve para reconstruir el proyecto y entenderlo antes de la defensa. Al terminar cada paso, explicar el resultado con palabras propias y reproducir una prueba.

## 1. Infraestructura

Leer Compose y distinguir `sqlserver`, `db-init` y el volumen. Generar `.env`, levantar los servicios y revisar los logs. Explicar por qué montar un archivo SQL no basta para ejecutarlo y por qué `db-init` espera el healthcheck.

**Comprobación:** detener y volver a iniciar SQL Server; el estado de importación y los registros deben persistir. No usar `down -v` para reiniciar.

## 2. Migración desde Oracle

Comparar el DDL de la fase 1 con `init.sql`. Identificar los cambios NUMBER → INT/DECIMAL, VARCHAR2 → NVARCHAR y DATE → DATETIME2. Ubicar las claves compuestas del catálogo y detalle, la relación empleado/tienda y el índice de correo no nulo.

**Comprobación:** explicar por qué el stock no se agregó a `producto` y por qué el total de una venta se deriva de sus detalles.

## 3. CRUD y TypeORM

Seguir una petición de países desde su módulo de rutas hasta el controlador compartido y el repositorio. Revisar los metadatos de la entidad y su validación. Identificar dónde se rechazan campos extra y por qué no se concatenan valores en SQL.

**Comprobación:** crear, consultar, modificar y eliminar un país nuevo en Postman; repetir un ID y observar `409`. Intentar un campo desconocido y observar `400`.

## 4. Histórico

Leer el cliente de importación y luego el servicio del backend. Identificar la validación del archivo, la transacción, el rol especial, el contexto de sesión y la conciliación. Las claves normales de la API no tienen privilegios de DDL ni pertenencia al rol de importación.

**Comprobación:** mostrar las 9,068 filas registradas en el estado de importación; explicar por qué las demostraciones posteriores aumentan los conteos actuales. La importación no debe repetirse ni aceptar archivos modificados.

## 5. Inventario

Estudiar `Insert_Detalle`: `inserted` contiene valores nuevos y `deleted` los anteriores. INSERT descuenta, UPDATE aplica la diferencia y DELETE devuelve. Las tablas pueden contener varias filas; no se debe asignar una cantidad arbitraria a una sola variable.

**Comprobación:** catálogo con stock 10; pedir 11 falla y conserva 10; pedir 2 deja 8. Explicar que el rollback también elimina el detalle fallido y que los bloqueos evitan vender las mismas unidades simultáneamente.

## 6. Pagos y estados

Estudiar `Insert_Pago` y `Validar_Venta`. La suma de abonos se compara con la suma de subtotales en SQL. El motor cambia el estado; Node solo comunica el resultado. La validación de ventas permite el cambio interno del trigger y bloquea marcar una venta pagada manualmente.

**Comprobación:** venta de 50, abono de 20 → REGISTRADA; abono de 30 → PAGADA. Reducir o eliminar el segundo abono permite observar el recálculo. Una anulación sin pagos devuelve inventario una sola vez.

## 7. Vistas

Explicar el propósito de cada JOIN y por qué se excluye ANULADA. Detalles y pagos deben agregarse por separado: unirlos directamente multiplicaría filas y montos. `COALESCE` representa correctamente ventas sin abonos.

**Comprobación:** ejecutar los tres reportes desde Postman y justificar al menos una fila de cada resultado. El endpoint usa SELECT sobre la vista, sin reconstruir los JOINs con TypeORM.

## 8. Ensayo de calificación

1. Mostrar los contenedores saludables y el DDL automático.
2. Ejecutar CRUD de una entidad y explicar la clave compuesta de otra.
3. Demostrar fallo y éxito del inventario, y cambio automático a PAGADA.
4. Consultar las tres vistas y explicar sus agregaciones.
5. Practicar agregar un filtro de reporte mediante parámetros o cambiar una validación de entrada; compilar y comprobar la petición.
6. Generar el ZIP y comprobar que no contiene credenciales ni dependencias instaladas.

Preguntas para practicar: ¿qué es atomicidad?, ¿cuándo se ejecuta un trigger?, ¿por qué hay un pool?, ¿qué hace una FK?, ¿por qué TypeORM no sincroniza?, ¿qué diferencia hay entre contenedor y volumen?, ¿por qué HTTP 400 y 409 son distintos?, ¿qué ocurre si llegan dos ventas simultáneas?
