-- Comercial La Estrella - SQL Server 2022. Ejecutado automaticamente por db-init.
-- No contiene carga historica: todas las inserciones se realizan por la API.
USE master;
GO
IF DB_ID(N'ComercialLaEstrella') IS NULL
    CREATE DATABASE ComercialLaEstrella;
GO
USE ComercialLaEstrella;
GO
SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO
IF OBJECT_ID(N'dbo.pais', N'U') IS NULL
BEGIN
CREATE TABLE dbo.pais (
    id_pais INT CONSTRAINT pk_pais PRIMARY KEY,
    nombre NVARCHAR(80) NOT NULL,
    CONSTRAINT uq_pais_nombre UNIQUE (nombre)
);
END;
GO

IF OBJECT_ID(N'dbo.departamento', N'U') IS NULL
BEGIN
CREATE TABLE dbo.departamento (
    id_departamento INT CONSTRAINT pk_departamento PRIMARY KEY,
    nombre NVARCHAR(80) NOT NULL,
    id_pais INT NOT NULL,
    CONSTRAINT uq_dep_pais_nombre UNIQUE (id_pais, nombre),
    CONSTRAINT fk_dep_pais FOREIGN KEY (id_pais) REFERENCES pais (id_pais)
);
END;
GO

IF OBJECT_ID(N'dbo.municipio', N'U') IS NULL
BEGIN
CREATE TABLE dbo.municipio (
    id_municipio INT CONSTRAINT pk_municipio PRIMARY KEY,
    nombre NVARCHAR(80) NOT NULL,
    id_departamento INT NOT NULL,
    CONSTRAINT uq_mun_dep_nombre UNIQUE (id_departamento, nombre),
    CONSTRAINT fk_mun_dep FOREIGN KEY (id_departamento)
        REFERENCES departamento (id_departamento)
);
END;
GO

IF OBJECT_ID(N'dbo.tipo_tienda', N'U') IS NULL
BEGIN
CREATE TABLE dbo.tipo_tienda (
    id_tipo_tienda INT CONSTRAINT pk_tipo_tienda PRIMARY KEY,
    nombre NVARCHAR(80) NOT NULL,
    CONSTRAINT uq_tip_tie_nombre UNIQUE (nombre)
);
END;
GO

IF OBJECT_ID(N'dbo.tipo_identificacion', N'U') IS NULL
BEGIN
CREATE TABLE dbo.tipo_identificacion (
    id_tipo_identificacion INT CONSTRAINT pk_tipo_id PRIMARY KEY,
    nombre NVARCHAR(50) NOT NULL,
    CONSTRAINT uq_tipo_id_nombre UNIQUE (nombre)
);
END;
GO

IF OBJECT_ID(N'dbo.cargo', N'U') IS NULL
BEGIN
CREATE TABLE dbo.cargo (
    id_cargo INT CONSTRAINT pk_cargo PRIMARY KEY,
    nombre NVARCHAR(80) NOT NULL,
    CONSTRAINT uq_cargo_nombre UNIQUE (nombre)
);
END;
GO

IF OBJECT_ID(N'dbo.categoria', N'U') IS NULL
BEGIN
CREATE TABLE dbo.categoria (
    id_categoria INT CONSTRAINT pk_categoria PRIMARY KEY,
    nombre NVARCHAR(80) NOT NULL,
    CONSTRAINT uq_cat_nombre UNIQUE (nombre)
);
END;
GO

IF OBJECT_ID(N'dbo.marca', N'U') IS NULL
BEGIN
CREATE TABLE dbo.marca (
    id_marca INT CONSTRAINT pk_marca PRIMARY KEY,
    nombre NVARCHAR(80) NOT NULL,
    CONSTRAINT uq_marca_nombre UNIQUE (nombre)
);
END;
GO

IF OBJECT_ID(N'dbo.estado_venta', N'U') IS NULL
BEGIN
CREATE TABLE dbo.estado_venta (
    id_estado_venta INT CONSTRAINT pk_estado_venta PRIMARY KEY,
    nombre NVARCHAR(30) NOT NULL,
    CONSTRAINT uq_est_ven_nombre UNIQUE (nombre),
    CONSTRAINT ck_est_ven_nombre CHECK (nombre IN ('REGISTRADA', 'PAGADA', 'ANULADA'))
);
END;
GO

IF OBJECT_ID(N'dbo.metodo_pago', N'U') IS NULL
BEGIN
CREATE TABLE dbo.metodo_pago (
    id_metodo_pago INT CONSTRAINT pk_metodo_pago PRIMARY KEY,
    nombre NVARCHAR(80) NOT NULL,
    CONSTRAINT uq_met_pag_nombre UNIQUE (nombre)
);
END;
GO

IF OBJECT_ID(N'dbo.persona', N'U') IS NULL
BEGIN
CREATE TABLE dbo.persona (
    id_persona INT CONSTRAINT pk_persona PRIMARY KEY,
    nombres NVARCHAR(100) NOT NULL,
    apellidos NVARCHAR(100) NOT NULL,
    telefono NVARCHAR(25) NOT NULL,
    correo NVARCHAR(150),
    direccion NVARCHAR(200) NOT NULL,
    id_municipio INT NOT NULL,
    CONSTRAINT fk_persona_mun FOREIGN KEY (id_municipio)
        REFERENCES municipio (id_municipio)
);
END;
GO

IF OBJECT_ID(N'dbo.tienda', N'U') IS NULL
BEGIN
CREATE TABLE dbo.tienda (
    id_tienda INT CONSTRAINT pk_tienda PRIMARY KEY,
    nombre NVARCHAR(120) NOT NULL,
    direccion NVARCHAR(200) NOT NULL,
    telefono NVARCHAR(25) NOT NULL,
    id_municipio INT NOT NULL,
    id_tipo_tienda INT NOT NULL,
    CONSTRAINT uq_tienda_nombre UNIQUE (nombre),
    CONSTRAINT fk_tienda_mun FOREIGN KEY (id_municipio)
        REFERENCES municipio (id_municipio),
    CONSTRAINT fk_tienda_tipo FOREIGN KEY (id_tipo_tienda)
        REFERENCES tipo_tienda (id_tipo_tienda)
);
END;
GO

IF OBJECT_ID(N'dbo.empleado', N'U') IS NULL
BEGIN
CREATE TABLE dbo.empleado (
    id_empleado INT CONSTRAINT pk_empleado PRIMARY KEY,
    fecha_contratacion DATETIME2(0) NOT NULL,
    id_tienda INT NOT NULL,
    id_cargo INT NOT NULL,
    id_persona INT NOT NULL,
    CONSTRAINT uq_emp_persona UNIQUE (id_persona),
    CONSTRAINT uq_emp_tienda UNIQUE (id_empleado, id_tienda),
    CONSTRAINT fk_emp_tienda FOREIGN KEY (id_tienda) REFERENCES tienda (id_tienda),
    CONSTRAINT fk_emp_cargo FOREIGN KEY (id_cargo) REFERENCES cargo (id_cargo),
    CONSTRAINT fk_emp_persona FOREIGN KEY (id_persona) REFERENCES persona (id_persona)
);
END;
GO

IF OBJECT_ID(N'dbo.cliente', N'U') IS NULL
BEGIN
CREATE TABLE dbo.cliente (
    id_cliente INT CONSTRAINT pk_cliente PRIMARY KEY,
    id_tipo_identificacion INT NOT NULL,
    numero_identificacion NVARCHAR(30) NOT NULL,
    id_persona INT NOT NULL,
    CONSTRAINT uq_cli_identificacion UNIQUE (id_tipo_identificacion, numero_identificacion),
    CONSTRAINT uq_cli_persona UNIQUE (id_persona),
    CONSTRAINT fk_cli_tipo_id FOREIGN KEY (id_tipo_identificacion)
        REFERENCES tipo_identificacion (id_tipo_identificacion),
    CONSTRAINT fk_cli_persona FOREIGN KEY (id_persona) REFERENCES persona (id_persona)
);
END;
GO

IF OBJECT_ID(N'dbo.producto', N'U') IS NULL
BEGIN
CREATE TABLE dbo.producto (
    id_producto INT CONSTRAINT pk_producto PRIMARY KEY,
    nombre NVARCHAR(120) NOT NULL,
    descripcion NVARCHAR(300) NOT NULL,
    id_categoria INT NOT NULL,
    id_marca INT NOT NULL,
    CONSTRAINT fk_prod_cat FOREIGN KEY (id_categoria) REFERENCES categoria (id_categoria),
    CONSTRAINT fk_prod_marca FOREIGN KEY (id_marca) REFERENCES marca (id_marca)
);
END;
GO

IF OBJECT_ID(N'dbo.catalogo_producto', N'U') IS NULL
BEGIN
CREATE TABLE dbo.catalogo_producto (
    precio_vigente DECIMAL(12,2) NOT NULL,
    existencia_actual INT NOT NULL,
    id_tienda INT NOT NULL,
    id_producto INT NOT NULL,
    CONSTRAINT pk_catalogo_producto PRIMARY KEY (id_tienda, id_producto),
    CONSTRAINT ck_cat_prod_precio CHECK (precio_vigente > 0),
    CONSTRAINT ck_cat_prod_exist CHECK (existencia_actual >= 0),
    CONSTRAINT fk_cat_prod_tienda FOREIGN KEY (id_tienda) REFERENCES tienda (id_tienda),
    CONSTRAINT fk_cat_prod_producto FOREIGN KEY (id_producto) REFERENCES producto (id_producto)
);
END;
GO

IF OBJECT_ID(N'dbo.venta', N'U') IS NULL
BEGIN
CREATE TABLE dbo.venta (
    id_venta INT CONSTRAINT pk_venta PRIMARY KEY,
    fecha_venta DATETIME2(0) NOT NULL,
    id_tienda INT NOT NULL,
    id_empleado INT NOT NULL,
    id_cliente INT NOT NULL,
    id_estado_venta INT NOT NULL,
    CONSTRAINT fk_venta_emp_tienda FOREIGN KEY (id_empleado, id_tienda)
        REFERENCES empleado (id_empleado, id_tienda),
    CONSTRAINT fk_venta_cli FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente),
    CONSTRAINT fk_venta_estado FOREIGN KEY (id_estado_venta)
        REFERENCES estado_venta (id_estado_venta)
);
END;
GO

IF OBJECT_ID(N'dbo.detalle_venta', N'U') IS NULL
BEGIN
CREATE TABLE dbo.detalle_venta (
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(12,2) NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    CONSTRAINT pk_detalle_venta PRIMARY KEY (id_venta, id_producto),
    CONSTRAINT ck_det_cantidad CHECK (cantidad > 0),
    CONSTRAINT ck_det_precio CHECK (precio_unitario > 0),
    CONSTRAINT ck_det_subtotal CHECK (subtotal = cantidad * precio_unitario),
    CONSTRAINT fk_det_venta FOREIGN KEY (id_venta) REFERENCES venta (id_venta),
    CONSTRAINT fk_det_producto FOREIGN KEY (id_producto) REFERENCES producto (id_producto)
);
END;
GO

IF OBJECT_ID(N'dbo.pago', N'U') IS NULL
BEGIN
CREATE TABLE dbo.pago (
    id_pago INT CONSTRAINT pk_pago PRIMARY KEY,
    monto DECIMAL(12,2) NOT NULL,
    id_metodo_pago INT NOT NULL,
    id_venta INT NOT NULL,
    CONSTRAINT ck_pago_monto CHECK (monto > 0),
    CONSTRAINT fk_pago_metodo FOREIGN KEY (id_metodo_pago)
        REFERENCES metodo_pago (id_metodo_pago),
    CONSTRAINT fk_pago_venta FOREIGN KEY (id_venta) REFERENCES venta (id_venta)
);
END;
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'uq_persona_correo' AND object_id = OBJECT_ID(N'dbo.persona'))
    CREATE UNIQUE INDEX uq_persona_correo ON dbo.persona(correo) WHERE correo IS NOT NULL;
GO

-- Registro de importacion: no concede escritura al usuario normal de la API.
IF OBJECT_ID(N'dbo.importacion_historica', N'U') IS NULL
CREATE TABLE dbo.importacion_historica (
    id INT NOT NULL PRIMARY KEY CHECK (id = 1),
    fecha DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    filas INT NOT NULL,
    sha256 CHAR(64) NOT NULL
);
GO
IF DATABASE_PRINCIPAL_ID(N'importador') IS NULL CREATE ROLE importador;
GO
CREATE OR ALTER VIEW dbo.Vista_Ventas_Ubicacion AS
WITH totales AS (
    SELECT id_venta, SUM(subtotal) AS total FROM dbo.detalle_venta GROUP BY id_venta
)
SELECT t.id_tienda, t.nombre AS tienda, m.nombre AS municipio,
       d.nombre AS departamento, p.nombre AS pais,
       COUNT_BIG(v.id_venta) AS cantidad_ventas,
       COALESCE(SUM(tot.total), 0) AS total_facturado
FROM dbo.venta v
JOIN dbo.estado_venta ev ON ev.id_estado_venta = v.id_estado_venta
JOIN dbo.tienda t ON t.id_tienda = v.id_tienda
JOIN dbo.municipio m ON m.id_municipio = t.id_municipio
JOIN dbo.departamento d ON d.id_departamento = m.id_departamento
JOIN dbo.pais p ON p.id_pais = d.id_pais
LEFT JOIN totales tot ON tot.id_venta = v.id_venta
WHERE ev.nombre <> N'ANULADA'
GROUP BY t.id_tienda, t.nombre, m.nombre, d.nombre, p.nombre;
GO
CREATE OR ALTER VIEW dbo.Vista_Top_Productos AS
SELECT p.id_producto AS codigo_producto, p.nombre, c.nombre AS categoria,
       m.nombre AS marca, SUM(CONVERT(BIGINT,d.cantidad)) AS unidades_vendidas,
       SUM(d.subtotal) AS monto_total
FROM dbo.detalle_venta d
JOIN dbo.venta v ON v.id_venta = d.id_venta
JOIN dbo.estado_venta ev ON ev.id_estado_venta = v.id_estado_venta
JOIN dbo.producto p ON p.id_producto = d.id_producto
JOIN dbo.categoria c ON c.id_categoria = p.id_categoria
JOIN dbo.marca m ON m.id_marca = p.id_marca
WHERE ev.nombre <> N'ANULADA'
GROUP BY p.id_producto, p.nombre, c.nombre, m.nombre;
GO
CREATE OR ALTER VIEW dbo.Vista_Consulta_Ventas AS
WITH totales AS (
    SELECT id_venta, SUM(subtotal) AS total FROM dbo.detalle_venta GROUP BY id_venta
), pagos AS (
    SELECT id_venta, SUM(monto) AS pagado FROM dbo.pago GROUP BY id_venta
)
SELECT v.*, e.nombre AS estado, COALESCE(t.total,0) AS total_venta,
       COALESCE(p.pagado,0) AS total_pagado,
       COALESCE(t.total,0)-COALESCE(p.pagado,0) AS saldo_pendiente
FROM dbo.venta v
JOIN dbo.estado_venta e ON e.id_estado_venta = v.id_estado_venta
LEFT JOIN totales t ON t.id_venta = v.id_venta
LEFT JOIN pagos p ON p.id_venta = v.id_venta;
GO
CREATE OR ALTER VIEW dbo.Vista_Saldos_Pendientes AS
SELECT id_venta, total_venta, total_pagado, saldo_pendiente
FROM dbo.Vista_Consulta_Ventas WHERE estado = N'REGISTRADA';
GO
-- AFTER dispara una vez por sentencia, no una vez por fila.
-- inserted/deleted se agrupan para soportar lotes, UPDATE y DELETE.
CREATE OR ALTER TRIGGER dbo.Insert_Detalle ON dbo.detalle_venta
AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    IF IS_ROLEMEMBER(N'importador') = 1
       AND TRY_CONVERT(INT, SESSION_CONTEXT(N'importacion_historica')) = 1 RETURN;

    DECLARE @ventas TABLE (id INT PRIMARY KEY);
    INSERT @ventas SELECT id_venta FROM inserted UNION SELECT id_venta FROM deleted;
    DECLARE @lock INT;
    SELECT @lock = v.id_venta FROM dbo.venta v WITH (UPDLOCK, HOLDLOCK)
    JOIN @ventas a ON a.id = v.id_venta ORDER BY v.id_venta;
    IF EXISTS (
        SELECT 1 FROM @ventas a JOIN dbo.venta v ON v.id_venta=a.id
        JOIN dbo.estado_venta e ON e.id_estado_venta=v.id_estado_venta
        WHERE e.nombre <> N'REGISTRADA' OR EXISTS(SELECT 1 FROM dbo.pago p WHERE p.id_venta=a.id)
    ) THROW 51002, N'Solo se permiten detalles en ventas REGISTRADA sin pagos', 1;

    DECLARE @delta TABLE (id_tienda INT, id_producto INT, cantidad BIGINT, PRIMARY KEY(id_tienda,id_producto));
    INSERT @delta
    SELECT v.id_tienda, x.id_producto, SUM(x.cantidad)
    FROM (
        SELECT id_venta,id_producto,CONVERT(BIGINT,cantidad) cantidad FROM inserted
        UNION ALL
        SELECT id_venta,id_producto,-CONVERT(BIGINT,cantidad) FROM deleted
    ) x JOIN dbo.venta v ON v.id_venta=x.id_venta
    GROUP BY v.id_tienda,x.id_producto;

    UPDATE c WITH (UPDLOCK, HOLDLOCK)
       SET existencia_actual = c.existencia_actual - d.cantidad
    FROM dbo.catalogo_producto c JOIN @delta d
      ON d.id_tienda=c.id_tienda AND d.id_producto=c.id_producto
    WHERE CONVERT(BIGINT,c.existencia_actual) >= d.cantidad;
    IF @@ROWCOUNT <> (SELECT COUNT(*) FROM @delta)
        THROW 51001, N'Stock insuficiente', 1;
END;
GO
CREATE OR ALTER TRIGGER dbo.Insert_Pago ON dbo.pago
AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    IF IS_ROLEMEMBER(N'importador') = 1
       AND TRY_CONVERT(INT, SESSION_CONTEXT(N'importacion_historica')) = 1 RETURN;
    DECLARE @ventas TABLE (id INT PRIMARY KEY);
    INSERT @ventas SELECT id_venta FROM inserted UNION SELECT id_venta FROM deleted;
    DECLARE @lock INT;
    SELECT @lock=v.id_venta FROM dbo.venta v WITH(UPDLOCK,HOLDLOCK)
    JOIN @ventas a ON a.id=v.id_venta ORDER BY v.id_venta;
    IF EXISTS (
        SELECT 1 FROM @ventas a JOIN dbo.venta v ON v.id_venta=a.id
        JOIN dbo.estado_venta e ON e.id_estado_venta=v.id_estado_venta
        WHERE e.nombre=N'ANULADA'
    ) THROW 51002, N'No se permiten pagos en ventas anuladas', 1;
    IF EXISTS (
        SELECT 1 FROM inserted i WHERE NOT EXISTS (
            SELECT 1 FROM dbo.detalle_venta d WHERE d.id_venta=i.id_venta
        )
    ) THROW 51002, N'La venta debe tener detalles antes de recibir pagos', 1;

    UPDATE v SET id_estado_venta = e.id_estado_venta
    FROM dbo.venta v JOIN @ventas a ON a.id=v.id_venta
    CROSS APPLY (SELECT COALESCE(SUM(subtotal),0) total FROM dbo.detalle_venta WHERE id_venta=v.id_venta) d
    CROSS APPLY (SELECT COALESCE(SUM(monto),0) total FROM dbo.pago WHERE id_venta=v.id_venta) p
    JOIN dbo.estado_venta e ON e.nombre = CASE WHEN d.total > 0 AND p.total >= d.total THEN N'PAGADA' ELSE N'REGISTRADA' END;
END;
GO
CREATE OR ALTER TRIGGER dbo.Validar_Venta ON dbo.venta
AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    IF IS_ROLEMEMBER(N'importador') = 1
       AND TRY_CONVERT(INT, SESSION_CONTEXT(N'importacion_historica')) = 1 RETURN;
    IF TRIGGER_NESTLEVEL(OBJECT_ID(N'dbo.Insert_Pago')) > 0 RETURN;
    IF EXISTS (
        SELECT 1 FROM inserted i LEFT JOIN deleted d ON d.id_venta=i.id_venta
        JOIN dbo.estado_venta e ON e.id_estado_venta=i.id_estado_venta
        WHERE d.id_venta IS NULL AND e.nombre <> N'REGISTRADA'
    ) THROW 51002,N'Una venta nueva debe iniciar REGISTRADA',1;
    IF EXISTS (
        SELECT 1 FROM inserted i JOIN deleted d ON d.id_venta=i.id_venta
        JOIN dbo.estado_venta anterior ON anterior.id_estado_venta=d.id_estado_venta
        JOIN dbo.estado_venta nuevo ON nuevo.id_estado_venta=i.id_estado_venta
        WHERE (anterior.nombre=N'ANULADA')
           OR (i.id_estado_venta<>d.id_estado_venta AND NOT (
                 anterior.nombre=N'REGISTRADA' AND nuevo.nombre=N'ANULADA'
                 AND NOT EXISTS(SELECT 1 FROM dbo.pago p WHERE p.id_venta=i.id_venta)))
           OR ((i.id_tienda<>d.id_tienda OR i.id_empleado<>d.id_empleado OR i.id_cliente<>d.id_cliente OR i.fecha_venta<>d.fecha_venta)
               AND (EXISTS(SELECT 1 FROM dbo.detalle_venta dv WHERE dv.id_venta=i.id_venta)
                 OR EXISTS(SELECT 1 FROM dbo.pago p WHERE p.id_venta=i.id_venta)))
    ) THROW 51002,N'Cambio de venta no permitido: estado automatico, venta anulada o registros asociados',1;

    -- Devolver stock solo en la transicion REGISTRADA -> ANULADA.
    ;WITH devolucion AS (
        SELECT i.id_tienda,dv.id_producto,SUM(CONVERT(BIGINT,dv.cantidad)) cantidad
        FROM inserted i JOIN deleted d ON d.id_venta=i.id_venta
        JOIN dbo.estado_venta e ON e.id_estado_venta=i.id_estado_venta
        JOIN dbo.detalle_venta dv ON dv.id_venta=i.id_venta
        WHERE i.id_estado_venta<>d.id_estado_venta AND e.nombre=N'ANULADA'
        GROUP BY i.id_tienda,dv.id_producto
    )
    UPDATE c SET existencia_actual=c.existencia_actual+x.cantidad
    FROM dbo.catalogo_producto c JOIN devolucion x ON x.id_tienda=c.id_tienda AND x.id_producto=c.id_producto;
END;
GO
-- No borrar inventario que aun da contexto a detalles de venta historicos.
CREATE OR ALTER TRIGGER dbo.Proteger_Catalogo ON dbo.catalogo_producto
AFTER UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS (
        SELECT 1 FROM deleted d
        WHERE NOT EXISTS (SELECT 1 FROM inserted i WHERE i.id_tienda=d.id_tienda AND i.id_producto=d.id_producto)
          AND EXISTS (SELECT 1 FROM dbo.detalle_venta dv JOIN dbo.venta v ON v.id_venta=dv.id_venta
                      WHERE v.id_tienda=d.id_tienda AND dv.id_producto=d.id_producto)
    ) THROW 51002,N'El catalogo tiene detalles de venta asociados',1;
END;
GO
-- Catalogos de estados: los tres nombres/IDs son parte del contrato del historico.
CREATE OR ALTER TRIGGER dbo.Proteger_Estados ON dbo.estado_venta
AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS(SELECT 1 FROM deleted) THROW 51002,N'Los estados del sistema no se modifican ni eliminan',1;
    IF EXISTS(SELECT 1 FROM inserted WHERE (id_estado_venta=1 AND nombre<>N'REGISTRADA')
       OR (id_estado_venta=2 AND nombre<>N'PAGADA') OR (id_estado_venta=3 AND nombre<>N'ANULADA')
       OR id_estado_venta NOT IN(1,2,3)) THROW 51002,N'Estado del sistema invalido',1;
END;
GO
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE name=N'ix_detalle_venta_producto' AND object_id=OBJECT_ID(N'dbo.detalle_venta'))
    CREATE INDEX ix_detalle_venta_producto ON dbo.detalle_venta(id_producto) INCLUDE(cantidad,subtotal);
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE name=N'ix_pago_venta' AND object_id=OBJECT_ID(N'dbo.pago'))
    CREATE INDEX ix_pago_venta ON dbo.pago(id_venta) INCLUDE(monto);
GO
USE master;
GO
IF SUSER_ID(N'estrella_api') IS NULL
    CREATE LOGIN estrella_api WITH PASSWORD = '$(DB_PASSWORD)', CHECK_POLICY = ON;
IF SUSER_ID(N'estrella_import') IS NULL
    CREATE LOGIN estrella_import WITH PASSWORD = '$(IMPORT_DB_PASSWORD)', CHECK_POLICY = ON;
GO
USE ComercialLaEstrella;
GO
IF USER_ID(N'estrella_api') IS NULL CREATE USER estrella_api FOR LOGIN estrella_api;
IF USER_ID(N'estrella_import') IS NULL CREATE USER estrella_import FOR LOGIN estrella_import;
IF IS_ROLEMEMBER(N'importador',N'estrella_import') <> 1 ALTER ROLE importador ADD MEMBER estrella_import;
GO
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.pais TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.pais TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.departamento TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.departamento TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.municipio TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.municipio TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.tipo_tienda TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.tipo_tienda TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.tipo_identificacion TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.tipo_identificacion TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.cargo TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.cargo TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.categoria TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.categoria TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.marca TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.marca TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.estado_venta TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.estado_venta TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.metodo_pago TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.metodo_pago TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.persona TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.persona TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.tienda TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.tienda TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.empleado TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.empleado TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.cliente TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.cliente TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.producto TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.producto TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.catalogo_producto TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.catalogo_producto TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.venta TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.venta TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.detalle_venta TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.detalle_venta TO estrella_import;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.pago TO estrella_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.pago TO estrella_import;
GRANT SELECT ON dbo.Vista_Ventas_Ubicacion TO estrella_api;
GRANT SELECT ON dbo.Vista_Ventas_Ubicacion TO estrella_import;
GRANT SELECT ON dbo.Vista_Top_Productos TO estrella_api;
GRANT SELECT ON dbo.Vista_Top_Productos TO estrella_import;
GRANT SELECT ON dbo.Vista_Saldos_Pendientes TO estrella_api;
GRANT SELECT ON dbo.Vista_Saldos_Pendientes TO estrella_import;
GRANT SELECT ON dbo.Vista_Consulta_Ventas TO estrella_api;
GRANT SELECT ON dbo.Vista_Consulta_Ventas TO estrella_import;
GRANT SELECT ON dbo.importacion_historica TO estrella_api;
GRANT SELECT ON dbo.importacion_historica TO estrella_import;
GRANT INSERT ON dbo.importacion_historica TO estrella_import;
GO
PRINT N'Inicializacion completada: 19 tablas, vistas, triggers y usuarios.';
