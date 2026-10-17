"""Genera el manual LaTeX desde la implementación; --build también crea el PDF."""
from pathlib import Path
import argparse
import json
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
NAME = 'Manual_Tecnico_Fase2'
schema = json.loads((ROOT / 'src/entities/schema.json').read_text())
manifest = json.loads((ROOT / 'data/manifest.json').read_text())
collection = json.loads((ROOT / 'postman/ComercialLaEstrella.postman_collection.json').read_text())
evidence = json.loads((DOCS / 'evidencias/validacion.json').read_text())


def esc(value):
    chars = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
             '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
             '^': r'\textasciicircum{}'}
    return ''.join(chars.get(c, c) for c in str(value))


def code(value):
    return r'\texttt{' + esc(value) + '}'


parts = []


def add(value):
    parts.append(value)


def listing(value, language=''):
    add(r'\begin{lstlisting}[language={' + language + '}]' + '\n' + value + '\n' + r'\end{lstlisting}')


def table(headers, rows, widths, keep=False):
    columns = ''.join(r'>{\raggedright\arraybackslash}p{' + w + '}' for w in widths)
    if keep:
        add(r'\par\smallskip\noindent\begin{minipage}{\textwidth}\begin{tabular}{' + columns + r'}\toprule')
        add('&'.join(r'\textbf{' + esc(h) + '}' for h in headers) + r'\\\midrule')
        for row in rows:
            add('&'.join(row) + r'\\')
        add(r'\bottomrule\end{tabular}\end{minipage}\par\smallskip')
        return
    add(r'\begin{longtable}{' + columns + r'}\toprule')
    head = '&'.join(r'\textbf{' + esc(h) + '}' for h in headers) + r'\\\midrule'
    add(head + r'\endfirsthead' + head + r'\endhead')
    add(r'\bottomrule\endfoot')
    for row in rows:
        add('&'.join(row) + r'\\')
    add(r'\end{longtable}')


add(r'''\documentclass[10pt,letterpaper]{article}
\usepackage[spanish,es-nodecimaldot]{babel}
\usepackage{fontspec}
\setmainfont{TeX Gyre Heros}
\setsansfont{TeX Gyre Heros}
\setmonofont{TeX Gyre Cursor}[Scale=.86]
\usepackage[letterpaper,top=2cm,bottom=2cm,left=1.8cm,right=1.8cm]{geometry}
\usepackage{xcolor,graphicx,float,booktabs,longtable,array,fancyhdr,hyperref,listings,lastpage,tikz,titlesec,enumitem,amsmath,xurl,needspace}
\usetikzlibrary{arrows.meta,positioning,calc}
\definecolor{accent}{HTML}{7C3AED}
\definecolor{accentblue}{HTML}{2563EB}
\definecolor{accentcyan}{HTML}{06B6D4}
\definecolor{muted}{HTML}{667085}
\definecolor{codebg}{HTML}{F5F6FA}
\hypersetup{colorlinks=true,linkcolor=accent,urlcolor=accentblue,pdftitle={Manual técnico - Proyecto Fase 2 - Comercial La Estrella},pdfauthor={Alex Ricardo Castañeda Rodríguez},bookmarksnumbered=true}
\titleformat{\section}{\Large\bfseries\color{accent}}{\thesection.}{.55em}{}
\titleformat{\subsection}{\large\bfseries\color{accentblue}}{\thesubsection.}{.55em}{}
\titleformat{\subsubsection}{\normalsize\bfseries}{\thesubsubsection.}{.55em}{}
\setlength{\headheight}{24pt}
\setlength{\footskip}{22pt}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small\color{accent}Bases de Datos 1 · Proyecto Fase 2}
\fancyhead[R]{\small\color{accentblue}Manual técnico}
\fancyfoot[L]{\scriptsize\color{muted}Alex Ricardo Castañeda Rodríguez · 202300476}
\fancyfoot[R]{\small\color{accent}\thepage/\pageref*{LastPage}}
\renewcommand{\headrulewidth}{.7pt}
\renewcommand{\headrule}{\hbox to\headwidth{\color{accentblue}\leaders\hrule height \headrulewidth\hfill}}
\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}
\setlength{\emergencystretch}{2em}
\renewcommand{\arraystretch}{1.18}
\setlist{itemsep=2pt,topsep=3pt,leftmargin=1.5em}
\setcounter{tocdepth}{2}
\makeatletter
\renewcommand\l@subsection{\@dottedtocline{2}{1.5em}{3em}}
\makeatother
\lstset{basicstyle=\ttfamily\footnotesize,backgroundcolor=\color{codebg},frame=single,rulecolor=\color{accentblue!25},breaklines=true,breakatwhitespace=false,columns=fullflexible,keepspaces=true,showstringspaces=false,tabsize=2,aboveskip=8pt,belowskip=8pt,keywordstyle=\bfseries\color{accent},commentstyle=\itshape\color{muted},literate={á}{{\'a}}1 {é}{{\'e}}1 {í}{{\'i}}1 {ó}{{\'o}}1 {ú}{{\'u}}1 {ñ}{{\~n}}1 {Á}{{\'A}}1 {É}{{\'E}}1 {Í}{{\'I}}1 {Ó}{{\'O}}1 {Ú}{{\'U}}1 {Ñ}{{\~N}}1}
\newcommand{\nota}[1]{\par\smallskip\noindent\textcolor{accentblue}{\textbf{Nota.}} #1\par\smallskip}
\newcommand{\evidencia}[2]{\begin{figure}[H]\centering\includegraphics[width=\textwidth,height=.80\textheight,keepaspectratio]{#1}\caption{#2}\end{figure}}
\begin{document}
\hypersetup{pageanchor=false}
\begin{titlepage}\thispagestyle{empty}
\begin{tikzpicture}[remember picture,overlay]
\shade[inner color=accent!13,outer color=white] ([xshift=-.5cm,yshift=-1cm]current page.north east) circle (5.1cm);
\shade[inner color=accentblue!10,outer color=white] ([xshift=.3cm,yshift=.5cm]current page.south west) circle (4.4cm);
\shade[left color=accent,right color=accentblue] (current page.north west) rectangle ([yshift=-.32cm]current page.north east);
\shade[left color=accentblue,right color=accentcyan] ([yshift=.22cm]current page.south west) rectangle (current page.south east);
\end{tikzpicture}
\begin{center}\vspace*{.3cm}
\begin{tikzpicture}\node[circle,shade,inner color=white,outer color=accent!18,draw=accentblue,line width=1.2pt,inner sep=7pt]{\includegraphics[width=3cm]{assets/escudo.png}};\end{tikzpicture}\par\medskip
{\Large\bfseries\color{accent}UNIVERSIDAD DE SAN CARLOS\\DE GUATEMALA}\par\smallskip
{\large\color{accentblue}Facultad de Ingeniería\\Escuela de Ciencias y Sistemas}\par\vfill
\begin{tikzpicture}\node[rectangle,rounded corners=10pt,shade,left color=accent,right color=accentblue,text=white,align=center,text width=.86\textwidth,inner sep=17pt]{{\Huge\bfseries MANUAL TÉCNICO}\par\medskip{\Large API REST, vistas y triggers\\SQL Server 2022 en Docker}};\end{tikzpicture}\par\medskip
{\Large\bfseries\color{accentblue}Comercial La Estrella · Fase 2}\par\vfill
\begin{tabular}{rl}
\textbf{Estudiante:}&Alex Ricardo Castañeda Rodríguez\\
\textbf{Carné:}&202300476\\
\textbf{Curso:}&Bases de Datos 1\\
\textbf{Período:}&Segundo semestre 2026\\
\textbf{Fecha:}&16 de octubre de 2026
\end{tabular}\par\vfill
{\small\color{muted}Guatemala, 2026}
\end{center}\end{titlepage}
\hypersetup{pageanchor=true}
\tableofcontents\clearpage
\section{Propósito, alcance y entregables}
Este manual explica cómo instalar, ejecutar, verificar y defender la segunda fase de Comercial La Estrella. El sistema conserva el modelo de 19 tablas de la fase 1 y lo implementa en SQL Server 2022. La API REST utiliza Node.js, Express, TypeScript y TypeORM; el motor se ejecuta en Docker y sus reglas operativas se aplican mediante restricciones y triggers de T-SQL.

El cliente de demostración es Postman. El enunciado no exige una interfaz frontend. DBeaver se utiliza para inspección estructural de solo lectura; durante la calificación, las altas, modificaciones y eliminaciones se realizan mediante la API. El diseño está preparado para uso local, con la API y el puerto SQL publicados en la interfaz de loopback.

\subsection{Correspondencia con el enunciado}
La sección 4 del enunciado solicita infraestructura, backend, colección de pruebas y documentación técnica. La documentación puede entregarse como README o PDF e incluye arranque del contenedor, ejecución del servidor y evidencias de los triggers. La hoja de calificación asigna 15 puntos a documentación.
''')
table(['Requisito', 'Implementación y ubicación'], [
    [esc('Infraestructura y DDL'), r'\path{docker-compose.yml}, \path{init.sql} y \path{docker/init.sh}.'],
    [esc('Backend completo'), r'\path{src/}, \path{package.json}, \path{package-lock.json} y \path{tsconfig.json}.'],
    [esc('CRUD de las 19 tablas'), r'Módulos en \path{src/routes/}; controlador compartido en \path{src/controllers/crud.ts}.'],
    [esc('Vistas y triggers'), r'Definidos en \path{init.sql}; los reportes se consultan por HTTP.'],
    [esc('Postman'), r'Colección principal, entorno local y colección de importación en \path{postman/}.'],
    [esc('Documentación y evidencias'), r'Este manual, README, referencia de API y \path{docs/evidencias/}.'],
    [esc('Repositorio'), r'\url{https://github.com/ricardious/SBD1_2S2026}.'],
], ['3.9cm', '12.2cm'])
add(r'''
\subsection{Cómo utilizar el manual}
Para ejecutar en una máquina nueva, seguir las secciones de requisitos, configuración, Docker, API e importación. Para volver a demostrar una instalación existente, utilizar el apartado de arranque diario y la guía de Postman. La referencia de entidades detalla campos y ejemplos; el anexo de peticiones relaciona cada operación con su código HTTP esperado. Los listados de vistas y triggers reproducen el código de la implementación.

\section{Arquitectura de la solución}
\begin{center}
\begin{tikzpicture}[node distance=7mm,box/.style={draw=accentblue!60,rounded corners=4pt,fill=codebg,text width=13cm,align=center,inner sep=7pt},arr/.style={-{Latex},thick,accentblue}]
\node[box] (client) {\textbf{Postman / cliente de importación}\\HTTP con cuerpos y respuestas JSON};
\node[box,below=of client] (api) {\textbf{Express + TypeScript}\\Rutas, validación Zod, controlador CRUD y manejo de errores};
\node[box,below=of api] (orm) {\textbf{TypeORM + controlador mssql}\\Repositorios, parámetros y conexiones agrupadas en pools};
\node[box,below=of orm] (db) {\textbf{SQL Server 2022 en Docker}\\Tablas, PK/FK, restricciones, índices, vistas y triggers};
\node[box,below=of db] (volume) {\textbf{Volumen persistente}\\Archivos de la base de datos en /var/opt/mssql};
\draw[arr] (client)--(api);\draw[arr] (api)--(orm);\draw[arr] (orm)--(db);\draw[arr] (db)--(volume);
\end{tikzpicture}
\end{center}
\subsection{Responsabilidad de cada capa}
\begin{itemize}
\item \textbf{Postman:} construye peticiones, sustituye variables y evalúa aserciones de respuesta. No se conecta directamente al motor.
\item \textbf{Express:} recibe HTTP, interpreta JSON y dirige la petición al módulo correspondiente. El cuerpo máximo configurado es 10 MB.
\item \textbf{Zod:} comprueba tipos, rangos, fechas, claves y campos permitidos antes de escribir.
\item \textbf{Controlador CRUD:} aplica el contrato común y usa repositorios; los casos especiales de venta y pago están explicitados.
\item \textbf{TypeORM:} convierte objetos a operaciones SQL. Los metadatos se declaran con EntitySchema; no se activa sincronización automática.
\item \textbf{SQL Server:} protege relaciones y reglas de negocio. El descuento de inventario y el estado de pago pertenecen al motor, no a un cálculo paralelo en Node.
\item \textbf{Docker Compose:} coordina el motor y la inicialización, el volumen, la comprobación de salud y la publicación del puerto.
\end{itemize}

\subsection{Recorrido de una petición de venta}
Un POST a detalle de venta llega a Express; la ruta obtiene sus metadatos, Zod valida el cuerpo y el repositorio ejecuta INSERT. SQL Server evalúa restricciones y activa Insert\_Detalle en la misma transacción. Si existe stock, descuenta y confirma; si falta stock, el trigger lanza un error y se revierte toda la sentencia. El middleware convierte el error de negocio en HTTP 400 con el mensaje Stock insuficiente. Tras una escritura correcta se consulta el registro y se devuelve HTTP 201.

\section{Organización del proyecto}
\begin{lstlisting}
Proyecto 2/
  .env.example             Plantilla sin credenciales reales
  docker-compose.yml       SQL Server y servicio db-init
  init.sql                 Tablas, permisos, vistas y triggers
  docker/init.sh           Ejecucion automatica del DDL
  data/                    Historico JSON y manifiesto
  src/
    config/                Entorno y conexiones SQL
    entities/              Metadatos y EntitySchema
    controllers/           CRUD y lotes
    middleware/            Errores HTTP
    routes/                Entidades, importacion y reportes
    services/              Validacion e importacion
    app.ts                 Aplicacion Express
    server.ts              Inicio y cierre de conexiones
  postman/                 Colecciones y entorno
  tests/                   Pruebas unitarias y de integracion
  scripts/                 Configuracion, importacion y entrega
  docs/                    Enunciado, guias, evidencias y manual
\end{lstlisting}
La carpeta node\_modules contiene dependencias instaladas y dist contiene JavaScript compilado. Ninguna se versiona. El archivo .env es local y privado. El histórico de datos sí forma parte de la entrega para reproducir la importación.

\section{Requisitos y preparación del equipo}
\subsection{Herramientas}
Se requiere Linux x86-64 con Docker Engine y el complemento Docker Compose, o Docker Desktop con contenedores Linux; Node.js 22 o superior; npm; Python 3 para las utilidades de preparación; y Postman. Python no interviene en las peticiones normales del backend. Para recompilar este documento se necesita XeLaTeX y las fuentes TeX Gyre Heros y TeX Gyre Cursor.

SQL Server tiene configurado un presupuesto interno de memoria de 2048 MB. No es un límite cgroup del contenedor ni una garantía sobre el consumo total. Se necesita margen adicional para el sistema operativo, la API, Postman, DBeaver y cualquier grabación. Los recursos disponibles dependen del resto de aplicaciones en ejecución.
\begin{lstlisting}
docker --version
docker compose version
node --version
npm --version
python3 --version
\end{lstlisting}
Los puertos predeterminados son 1433 para SQL Server y 3000 para la API. Si están ocupados, ajustar .env y la variable baseUrl de Postman. Ejecutar los comandos de este manual desde la raíz de Proyecto 2, salvo que se indique lo contrario.

\subsection{Obtener el código}
\begin{lstlisting}
git clone https://github.com/ricardious/SBD1_2S2026.git
cd "SBD1_2S2026/Proyecto 2"
\end{lstlisting}
Si ya se dispone de la carpeta local, abrir una terminal directamente en ella. El nombre contiene un espacio; por eso se entrecomilla al utilizar cd.

\section{Configuración de variables y credenciales}
\subsection{Creación inicial}
\begin{lstlisting}
python3 scripts/setup-env.py
npm ci
\end{lstlisting}
El generador toma la plantilla .env.example, genera secretos aleatorios y crea .env con permisos privados. Si el archivo existe, no lo sobrescribe. npm ci instala exactamente el árbol del archivo package-lock.json. Las contraseñas de este manual no se incluyen: cada instalación usa sus propias credenciales.
''')
table(['Variable', 'Propósito y valor de referencia'], [
    [code('MSSQL_SA_PASSWORD'), esc('Contraseña administrativa del motor, usada por Docker y db-init.')],
    [code('DB_HOST / DB_PORT'), esc('Conexión del backend: 127.0.0.1 y 1433 por defecto.')],
    [code('DB_NAME'), code('ComercialLaEstrella')],
    [code('DB_USER / DB_PASSWORD'), esc('Login estrella_api y su contraseña; operaciones habituales.')],
    [code('IMPORT_DB_USER'), code('estrella_import')],
    [code('IMPORT_DB_PASSWORD'), esc('Contraseña del login separado para la carga histórica.')],
    [code('IMPORT_KEY'), esc('Secreto de al menos 32 caracteres, enviado en X-Import-Key.')],
    [code('IMPORT_ENABLED'), esc('false normalmente; true solo durante la primera carga.')],
    [code('HOST / PORT'), esc('Dirección de escucha de la API: 127.0.0.1 y 3000.')],
], ['5.5cm', '10.6cm'])
add(r'''
\subsection{Reglas de configuración}
DB\_PASSWORD e IMPORT\_DB\_PASSWORD deben tener de 16 a 128 caracteres de los conjuntos A-Z, a-z, 0-9, guion, guion bajo y signo de exclamación. init.sh valida ese conjunto antes de sustituir valores en los literales de sqlcmd. Las variables numéricas y booleanas del backend se validan al iniciar; una configuración inválida impide el arranque.

Cambiar una contraseña en .env no rota automáticamente un login que ya existe dentro del volumen. El DDL solo crea logins ausentes. En una instalación existente se conservan las claves originales o se realiza una rotación administrativa coordinada. No se borra el volumen para corregir una contraseña.

\section{Arranque de SQL Server con Docker}
\subsection{Crear los servicios}
\begin{lstlisting}
docker compose up -d
docker compose ps -a
docker compose logs db-init
\end{lstlisting}
Se crean dos servicios. sqlserver mantiene el motor y los datos; db-init es una tarea que ejecuta init.sql cuando el motor está saludable. Es normal que db-init quede detenido después de finalizar: debe terminar con código 0. Comprobar ambos resultados; la salud del motor por sí sola no demuestra que el esquema esté listo.

La imagen de SQL Server 2022 está fijada por digest en Compose. La edición Developer se utiliza para desarrollo y evaluación. El puerto del contenedor se publica únicamente en 127.0.0.1. Los montajes del DDL son de solo lectura; la opción z permite el etiquetado compartido en sistemas con SELinux.

\subsection{Qué hace la inicialización}
\begin{enumerate}
\item Verifica la contraseña de los dos usuarios de aplicación.
\item Ejecuta sqlcmd con autenticación administrativa, confianza en el certificado local y salida con error si falla un lote.
\item Crea ComercialLaEstrella si no existe y crea las tablas ausentes.
\item Define restricciones, índices y la tabla de control de importación.
\item Crea o actualiza vistas y triggers.
\item Crea los logins y usuarios ausentes y concede permisos por objeto.
\end{enumerate}
La inicialización crea estructura; no carga registros de negocio. El histórico se envía por HTTP. Si se necesita volver a aplicar el script sin eliminar los datos:
\begin{lstlisting}
docker compose run --rm db-init
\end{lstlisting}
El script permite repetir su ejecución sobre el esquema esperado. No reemplaza una herramienta general de migraciones: las tablas existentes no se reconstruyen automáticamente cuando cambia su definición.

\subsection{Persistencia y detención}
\begin{lstlisting}
# Detener o volver a iniciar sin borrar datos
docker compose stop
docker compose start

# Reiniciar solamente el motor
docker compose restart sqlserver
\end{lstlisting}
Los archivos se guardan en el volumen sqlserver-data del proyecto Compose. docker compose down elimina los contenedores y la red, pero conserva el volumen. La opción down -v también elimina el volumen y sus datos; no se utiliza en el reinicio habitual ni antes de la demostración.

\section{Compilación y ejecución de la API}
\begin{lstlisting}
npm run build
npm start
\end{lstlisting}
build compila TypeScript a dist; start ejecuta dist/server.js. La terminal queda ocupada mientras se atienden peticiones. Para trabajar con recarga automática puede utilizarse npm run dev. Si se modifica el código y se usa npm start, primero se recompila; editar TypeScript no cambia un compilado previo por sí solo.

El servidor inicializa primero el pool de base de datos. Solo después abre el puerto HTTP. Al recibir SIGINT o SIGTERM cierra el servidor y las conexiones, evitando dejar el proceso de Node activo innecesariamente.
\begin{lstlisting}
curl http://127.0.0.1:3000/api/health
\end{lstlisting}
\textbf{Resultado esperado:} HTTP 200 y el siguiente objeto:
\begin{lstlisting}
{"estado":"ok","database":"SQL Server 2022"}
\end{lstlisting}
La comprobación ejecuta SELECT 1 contra el motor; confirma comunicación con SQL Server, no solo que Express esté escuchando.

\subsection{Arranque diario con la carga ya realizada}
\begin{enumerate}
\item Abrir Proyecto 2 y ejecutar docker compose up -d.
\item Verificar motor saludable e inicialización correcta.
\item Mantener IMPORT\_ENABLED=false e iniciar npm start.
\item Consultar health y el estado de importación.
\item Seleccionar el entorno local de Postman y comenzar una nueva ejecución.
\end{enumerate}
No es necesario importar de nuevo, reinstalar dependencias ni recrear la base para cada sesión. Reiniciar Node tampoco cambia los identificadores que Postman conserva.

\section{Migración del modelo y del histórico}
\subsection{Cambios entre Oracle y SQL Server}
La fase 2 mantiene las entidades, claves y dependencias de la fase 1. Los tipos se adaptan al motor: NUMBER de identificadores pasa a INT; importes a DECIMAL(12,2); VARCHAR2 a NVARCHAR para conservar Unicode; y fechas a DATETIME2(0). No se utiliza IDENTITY porque los identificadores originales deben preservarse.

persona concentra los datos compartidos de clientes y empleados. catalogo\_producto representa el par tienda-producto y almacena precio vigente y existencia por tienda. detalle\_venta conserva el precio histórico aplicado a una venta; este precio puede diferir del vigente sin que exista un error. La FK compuesta de venta hacia empleado garantiza que el empleado pertenece a la tienda indicada.

\subsection{Conteos de referencia}
La fuente es el libro dataset\_comercial\_la\_estrella.xlsx de la fase 1. data/historico.json contiene su conversión y data/manifest.json registra el origen y los conteos. Los 45 correos ausentes se conservan como NULL; un índice único filtrado excluye los nulos y mantiene la unicidad de los correos presentes.
''')
table(['Tabla', 'Filas históricas', 'Clave primaria'], [
    [code(t['table']), esc(f"{manifest['counts'][t['table']]:,}"), ', '.join(code(k) for k in t['keys'])]
    for t in schema
] + [[r'\textbf{TOTAL}', r'\textbf{9,068}', esc('19 tablas de negocio')]], ['5cm', '3cm', '8.1cm'])
add(r'''
\subsection{Primera importación: solo sobre una instalación vacía}
\begin{enumerate}
\item Detener la API y cambiar temporalmente IMPORT\_ENABLED a true en .env.
\item Iniciar la API y, desde otra terminal, ejecutar npm run import:historico.
\item Comprobar HTTP 201, el mensaje Historico importado y conciliado y total 9068.
\item Detener la API, restaurar IMPORT\_ENABLED=false y volver a iniciarla.
\item Consultar GET /api/admin/importacion; debe indicar importado=true, detalle.filas=9068 y habilitada=false.
\end{enumerate}
El script cliente envía el archivo mediante POST /api/admin/importacion con X-Import-Key. No escribe directamente en SQL. La colección de importación ofrece una alternativa manual: definir importKey localmente, elegir el archivo histórico en Body, modo binary, y enviar Content-Type application/json. No exportar el secreto.

\subsection{Transacción, seguridad y conciliación}
\begin{enumerate}
\item El servicio reserva una exclusión en memoria antes de su primera operación asíncrona.
\item Compara el SHA-256 canónico del cuerpo con el del archivo histórico incluido. Cambiar el orden de propiedades no cambia la representación canónica; alterar valores o el orden de las filas sí puede cambiarla.
\item Valida cada registro con las reglas de su entidad.
\item Abre el pool estrella\_import e inicia una transacción SERIALIZABLE.
\item Adquiere un bloqueo de aplicación exclusivo con sp\_getapplock y verifica ausencia de carga previa y de filas en las 19 tablas.
\item Activa un contexto de sesión de importación y carga en orden de dependencias, en bloques de 50 filas.
\item Vuelve a leer y compara todos los valores de cada tabla ordenados por clave; normaliza las fechas para una comparación estable.
\item Registra la carga en importacion\_historica, limpia el contexto y confirma. Ante cualquier fallo revierte la transacción.
\item Libera la conexión, destruye el pool especial y libera la exclusión, incluso cuando hay un error.
\end{enumerate}
La excepción histórica requiere simultáneamente pertenecer al rol importador y tener el contexto activo. Esto evita volver a descontar existencias que ya representan el estado histórico del Excel. Las PK, FK, CHECK e índices únicos siguen evaluándose. El usuario estrella\_api no pertenece a ese rol y no puede activar la excepción únicamente fijando el contexto.
''')
add(r'Hash registrado en la evidencia de carga:\par\smallskip\path{' + evidence['historico']['sha256'] + r'}\par')
add(r'''
\nota{El contador 9068 describe la importación original. Las pruebas posteriores crean registros adicionales; el total actual de las tablas puede ser mayor sin invalidar la conciliación histórica. No borrar la base para hacer coincidir esos números.}

\section{Contrato HTTP, validación y errores}
La dirección base es \url{http://127.0.0.1:3000/api}. Los cuerpos POST y PUT se envían como JSON con Content-Type application/json. Los identificadores se proporcionan explícitamente; no los asigna automáticamente el servidor.
''')
table(['Método', 'Ruta de ejemplo', 'Respuesta'], [
    [code('POST'), r'\path{/api/pais}', esc('201 y registro creado.')],
    [code('GET'), r'\path{/api/pais?limit=5&offset=0}', esc('200 con data, total, limit y offset.')],
    [code('GET'), r'\path{/api/pais/1}', esc('200 con objeto; 404 si no existe.')],
    [code('PUT'), r'\path{/api/pais/1}', esc('200 con registro actualizado.')],
    [code('DELETE'), r'\path{/api/pais/1}', esc('204, sin cuerpo de respuesta.')],
], ['2cm', '7cm', '7.1cm'])
add(r'''
PUT admite uno o más campos modificables: no obliga a reenviar el registro completo. No admite claves primarias, campos desconocidos ni un objeto vacío. En pago tampoco se admite trasladar el registro a otra venta mediante id\_venta.

\subsection{Listados y paginación}
limit es un entero de 1 a 500, con valor predeterminado 100; offset es un entero no negativo, con valor predeterminado 0. El listado se ordena por clave primaria. Los parámetros no reconocidos se rechazan. total representa el número total de registros de esa entidad, no solo los de la página.
\begin{lstlisting}
{
  "data": [{"id_pais": 1, "nombre": "Guatemala"}],
  "total": 3,
  "limit": 1,
  "offset": 0
}
\end{lstlisting}
El total del ejemplo corresponde al histórico de países; puede aumentar si se dejan registros de prueba.

\subsection{Tipos y restricciones de entrada}
\begin{itemize}
\item Los enteros se envían como números JSON, no como cadenas. IDs y cantidades deben ser positivos y caber en INT; existencia\_actual permite cero.
\item Los importes deben ser positivos, con máximo dos decimales y dentro de DECIMAL(12,2). El subtotal debe coincidir con cantidad por precio.
\item Los textos tienen longitud máxima según entidad y no pueden contener únicamente espacios. correo admite NULL o una dirección válida.
\item Las fechas aceptan YYYY-MM-DD o YYYY-MM-DDTHH:mm:ss. Se interpretan en UTC; en las respuestas pueden aparecer con Z y milisegundos. La entrada no utiliza sufijo Z porque el validador espera los formatos indicados.
\item Las claves de ruta deben ser enteros positivos sin signos ni decimales. Para claves compuestas se respetan los dos segmentos y su orden.
\end{itemize}

\needspace{19\baselineskip}\subsection{Códigos HTTP y lectura de fallos}
''')
table(['Código', 'Significado en esta API'], [
    ['200', esc('Consulta o actualización correcta.')], ['201', esc('Creación, lote o importación correcta.')],
    ['204', esc('Eliminación correcta; no hay JSON que mostrar.')], ['400', esc('Datos o JSON inválidos, histórico alterado o stock insuficiente.')],
    ['401', esc('Clave de importación incorrecta con la ruta habilitada.')], ['404', esc('Registro o ruta inexistente; importación deshabilitada.')],
    ['409', esc('Duplicado, referencias, operación protegida, carga previa o conflicto concurrente.')],
    ['413', esc('Cuerpo de la petición superior al tamaño permitido.')], ['500', esc('Error interno no clasificado; revisar terminal del servidor.')],
], ['2cm', '14.1cm'], keep=True)
add(r'''
Los mensajes de negocio se devuelven en error; la validación también puede incluir detalles con campo y mensaje. Los números SQL 2601 y 2627 se traducen a Registro duplicado; 547 a conflicto de integridad; 1205 y 1222 a conflicto concurrente. El error 51001 de los triggers se convierte en 400 y Stock insuficiente; el 51002 se comunica como 409. No se exponen consultas completas ni contraseñas en las respuestas de error interno.

\section{TypeORM y acceso a datos}
Los metadatos de src/entities/schema.json describen tabla, claves, tipos, longitudes y nulabilidad. src/entities/index.ts los valida y crea un EntitySchema por tabla, con esquema dbo. Las relaciones físicas y restricciones se mantienen en init.sql. No se duplican mediante sincronización automática del ORM.

\begin{itemize}
\item synchronize=false y migrationsRun=false: el esquema lo administra el DDL explícito.
\item El pool normal permite hasta cinco conexiones; el de importación, una. No se abre una sesión nueva por cada petición.
\item encrypt=true y trustServerCertificate=true permiten cifrado con el certificado local del contenedor. Esa confianza se ha definido para la instalación local.
\item useUTC=true conserva una interpretación uniforme de fechas; requestTimeout es 120000 ms.
\item disableOutputReturning=true evita OUTPUT sin INTO, incompatible con escrituras en tablas con triggers habilitados. Después de insertar o actualizar se consulta el resultado.
\end{itemize}
Las rutas de entidades llaman a una fábrica de CRUD; así conservan módulos separados y comparten el contrato de validación. Los nombres de tabla proceden de metadatos internos, nunca de un nombre arbitrario recibido por HTTP. Los valores se pasan como parámetros o mediante operaciones de repositorio.

\section{Inventario: trigger Insert\_Detalle}
\subsection{Qué es un trigger}
Un trigger DML es código almacenado que SQL Server ejecuta automáticamente como respuesta a INSERT, UPDATE o DELETE sobre una tabla. El cliente no lo invoca con una ruta especial. Forma parte de la transacción que modificó la tabla: si lanza un error, no se debe conservar una parte de la venta y otra parte del inventario.

Insert\_Detalle se define como AFTER INSERT, UPDATE, DELETE. Se ejecuta una vez por sentencia y trabaja con los conjuntos inserted y deleted. En INSERT solo hay filas nuevas; en DELETE solo anteriores; en UPDATE hay ambas versiones. No se presupone una sola fila.

\subsection{Cálculo del ajuste}
El trigger reúne las ventas afectadas, bloquea sus encabezados, comprueba que estén REGISTRADA y sin pagos, y agrupa por tienda y producto:
\[
\Delta_{t,p}=\sum\text{cantidad nueva}_{t,p}-\sum\text{cantidad anterior}_{t,p}
\qquad
\text{stock final}_{t,p}=\text{stock actual}_{t,p}-\Delta_{t,p}
\]
En una inserción de 2 unidades el delta es 2 y se descuentan 2. Si se modifica de 2 a 3, el delta es 1: solo se descuenta una unidad adicional. Si se elimina un detalle de 3, el delta es -3 y se devuelven tres.

\subsection{Actualización atómica y rollback}
La actualización del catálogo utiliza UPDLOCK y HOLDLOCK, junto con una condición que exige stock suficiente. Después compara las filas realmente actualizadas con el número de grupos del delta. Si falta un catálogo o alguna cantidad supera el disponible, lanza THROW 51001. SET XACT\_ABORT ON y el error impiden conservar ajustes parciales.

En un lote que solicita 4 y 7 unidades del mismo producto en una tienda con 10, se considera el total 11. No se aceptan ambas filas por separado. En competencia concurrente, las solicitudes no deben consumir simultáneamente las mismas últimas unidades; los bloqueos y las condiciones se evalúan en el motor. Un conflicto de bloqueo puede responder 409 y requerir reintento.

\subsection{Demostración mínima}
Crear un producto de prueba, su catálogo en tienda 1 con existencia 10 y una venta REGISTRADA. Pedir 11 unidades debe devolver 400, sin crear el detalle y conservando 10. Pedir 2 debe devolver 201; consultar el catálogo debe mostrar 8. Los dos resultados se verifican por HTTP, sin modificar directamente la tabla.

\section{Pagos: trigger Insert\_Pago y estados}
Insert\_Pago se ejecuta después de INSERT, UPDATE y DELETE en pago. Reúne ventas afectadas, toma bloqueos sobre los encabezados, rechaza ventas anuladas y evita recibir pagos si no existen detalles.
\[
T=\sum\text{subtotal de detalles}\qquad P=\sum\text{monto de pagos}
\]
Si T es mayor que cero y P es mayor o igual a T, el estado pasa a PAGADA; en otro caso, a REGISTRADA. La implementación acepta sobrepago y puede mostrar un saldo negativo: no debe afirmarse que lo prohíbe. Actualizar o eliminar un abono recalcula el estado con los importes restantes.

\subsection{Ejemplo de venta de Q50}
\begin{enumerate}
\item Registrar dos unidades con precio Q25 y subtotal Q50.
\item Registrar un primer pago de Q20; GET de la venta muestra REGISTRADA, total 50, pagado 20 y saldo 30.
\item Registrar un segundo pago de Q30; el motor cambia a PAGADA, total pagado 50 y saldo 0.
\item Reducir o eliminar el segundo pago en una prueba separada permite observar el regreso a REGISTRADA si el total pagado deja de cubrir la venta.
\end{enumerate}
El backend no asigna PAGADA como parte del POST de pago. SQL Server realiza la transición; el GET posterior permite observar su resultado.

\section{Protecciones complementarias del negocio}
\subsection{Validar\_Venta}
Una venta nueva debe comenzar REGISTRADA. No se permite marcar PAGADA manualmente. El trigger reconoce la actualización anidada originada por Insert\_Pago para permitir el cambio interno válido. Cuando una venta ya tiene detalles o pagos se protegen tienda, empleado, cliente y fecha; cambiar esos valores alteraría el significado de movimientos existentes.

Una venta REGISTRADA sin pagos puede cambiar a ANULADA. La transición agrupa sus detalles y devuelve existencias al catálogo una sola vez. Repetir la anulación se rechaza, por lo que no duplica la devolución. Una venta anulada queda protegida. Las FK impiden borrar ventas con registros asociados; no hay una eliminación en cascada de transacciones financieras.

\subsection{Proteger\_Catalogo y Proteger\_Estados}
Proteger\_Catalogo impide eliminar una combinación tienda-producto si existen detalles de ventas que necesitan ese contexto. Permite actualizar precio o existencias; no elimina el registro histórico del detalle.

Proteger\_Estados conserva el contrato fijo: 1=REGISTRADA, 2=PAGADA y 3=ANULADA. Los módulos CRUD existen para esa entidad, pero las escrituras incompatibles se rechazan con 409. Su prueba correcta es demostrar la protección, no cambiar los nombres del sistema.

\subsection{Resumen de dependencias}
Las altas respetan la secuencia de catálogos, personas, tiendas, empleados/clientes, productos, catálogo, ventas, detalles y pagos. Para borrar auxiliares se usa el orden inverso. Un 409 por FK significa que existe una referencia que debe tratarse conforme al negocio; no se desactiva la restricción para forzar la operación.

\section{Vistas y reportes SQL}
Una vista guarda una definición SELECT reutilizable. Las tres vistas solicitadas encapsulan JOIN y agregaciones en el motor. Los endpoints de reportes ejecutan SELECT sobre esos objetos y aplican un orden estable; no reconstruyen los reportes mediante relaciones del ORM.

\subsection{Vista\_Ventas\_Ubicacion}
Ruta: \path{GET /api/reportes/ventas-ubicacion}. Devuelve id\_tienda, tienda, municipio, departamento, pais, cantidad\_ventas y total\_facturado. Preagrupa los subtotales por venta antes de contar y sumar, y excluye ANULADA. Parte de las ventas existentes; una tienda sin ventas no aparece por el solo hecho de existir.

\subsection{Vista\_Top\_Productos}
Ruta: \path{GET /api/reportes/top-productos}. Devuelve codigo\_producto, nombre, categoria, marca, unidades\_vendidas y monto\_total. Agrega detalles de ventas no anuladas y usa BIGINT en la suma de unidades. El endpoint ordena por unidades descendentes y código de producto como desempate. El reporte no está limitado a los primeros diez: devuelve todos los productos presentes en esa agregación.

\subsection{Vista\_Saldos\_Pendientes y vista auxiliar}
Ruta: \path{GET /api/reportes/saldos-pendientes}. Devuelve id\_venta, total\_venta, total\_pagado y saldo\_pendiente para ventas REGISTRADA. Se apoya en Vista\_Consulta\_Ventas, que también enriquece los GET de venta con estado e importes. COALESCE convierte la ausencia de detalles o abonos en cero.

\subsection{Por qué se agregan detalles y pagos por separado}
Si una venta tiene dos detalles y tres pagos, unir ambos conjuntos directamente genera seis filas. Eso repetiría los subtotales tres veces y los pagos dos veces. Las expresiones de tabla comunes agrupan cada conjunto por id\_venta antes de unirlos al encabezado. El saldo se calcula como total de detalles menos total de pagos.

Todos los endpoints de reportes responden HTTP 200 con un objeto que contiene data como arreglo. En los resultados del controlador mssql, ciertos agregados BIGINT pueden representarse como cadenas JSON; por ejemplo, cantidad\_ventas o unidades\_vendidas. Los totales pueden cambiar después de las pruebas; una cifra fija de una captura no sustituye la comprobación de la fórmula.

\section{Postman: importación, variables y ejecución}
\subsection{Importar los archivos correctos}
En Postman seleccionar Import, Files y abrir los siguientes archivos de la carpeta postman:
\begin{itemize}
\item ComercialLaEstrella.postman\_collection.json: crea la colección Comercial La Estrella - Fase 2.
\item local.postman\_environment.json: crea el entorno Comercial La Estrella local.
\end{itemize}
Seleccionar el entorno arriba a la derecha. La colección aparece en Collections y el entorno en Environments. Importar JSON no ejecuta peticiones ni crea tablas o registros.
''')
table(['Carpeta', 'Uso'], [
    [code('00 Preparacion'), esc('Comprueba conexión, genera IDs y crea dependencias auxiliares.')],
    [code('01 CRUD por entidad'), esc('Prueba cada entidad; contiene 19 subcarpetas.')],
    [code('02 Limpieza auxiliares'), esc('Elimina las dependencias temporales del CRUD.')],
    [code('03 Triggers'), esc('Demuestra inventario, pagos y anulación con resultados observables.')],
    [code('04 Vistas'), esc('Consulta los tres reportes.')],
], ['5.6cm', '10.5cm'])
add(r'''
\subsection{Qué significan las llaves dobles}
Una expresión como \texttt{\{\{baseUrl\}\}} es una referencia a una variable. Antes de enviar, Postman sustituye su valor. baseUrl está en el entorno local y también como respaldo en la colección. Su valor predeterminado es http://127.0.0.1:3000/api.

runId, auxId y payId son variables de colección creadas por el script Pre-request de la primera petición, Iniciar ejecucion y comprobar conexion. Se pueden inspeccionar en Scripts de esa petición y en Variables de la colección después de ejecutarla.
\begin{lstlisting}
const id = 1500000000 + Math.floor(Math.random() * 100000000);
pm.collectionVariables.set('runId', id);
pm.collectionVariables.set('auxId', id + 1);
pm.collectionVariables.set('payId', id + 2);
\end{lstlisting}
El rango aleatorio reduce la probabilidad de colisión, pero no garantiza unicidad absoluta. Si se vuelve a enviar Crear con el mismo runId, el primer POST puede dar 201 y el segundo 409. Esto es esperado porque se intenta repetir la PK. Si un ID nuevo coincide con uno existente, volver a iniciar la preparación antes de comenzar otra ejecución.

\subsection{Cómo repetir mañana la demostración}
Ejecutar una vez la primera petición de preparación y continuar en el orden original. Esa petición genera nuevos IDs; no borra datos ni reinicia la base. Reiniciar Node o Docker no cambia las variables de Postman. No volver a ejecutar la primera petición a mitad de un CRUD: se perdería la referencia al registro que se pretendía consultar o eliminar.

La forma más reproducible es hacer clic derecho en la colección, Run collection, seleccionar todas las carpetas y ejecutar una iteración. El orden evita fallos por dependencias. Para pruebas manuales se utiliza Send y se conserva el mismo runId durante toda la secuencia. Test Results muestra las aserciones aprobadas o fallidas. Un código 400, 404 o 409 puede ser precisamente lo que la prueba espera.

\subsection{Ejemplo manual de CRUD}
Ejecutar primero la preparación. En pais: Crear devuelve 201, Listar 200, Buscar por clave 200, Actualizar 200, Eliminar 204 y Confirmar eliminacion 404. Tras la eliminación, el 404 demuestra que el registro ya no está. Los nombres Demo y los IDs altos permiten distinguir estos registros del histórico.

\subsection{Colección de importación}
Importacion.postman\_collection.json se reserva para una base vacía con la ruta de carga habilitada. No se ejecuta como parte de la demostración habitual. Si el histórico ya está cargado, basta con consultar su estado. El backend impide repetir la carga; no existe una petición de reinicio de base incluida en la colección.

\section{Lotes, atomicidad y concurrencia}
Las rutas POST /api/detalle\_venta/lote y POST /api/pago/lote admiten arreglos de 1 a 100 objetos con los mismos campos del POST individual. Devuelven 201 con insertados igual a la cantidad de filas. La inserción es una sola sentencia; el trigger considera el conjunto completo y cualquier error revierte el lote.

Atomicidad significa que se conserva todo el cambio o ninguno. La prueba de lotes debe incluir un caso cuyo consumo agregado exceda el stock y verificar que no permanezcan detalles ni descuentos parciales. La prueba concurrente lanza solicitudes que compiten por las últimas unidades y comprueba que no se sobrevende. No se concluye concurrencia correcta únicamente porque dos peticiones separadas funcionen en serie.

\section{Pruebas y resultados registrados}
\subsection{Comandos reproducibles}
\begin{lstlisting}
npm run build
npm test
# API encendida e historico cargado:
npm run test:integration
npm run postman
\end{lstlisting}
Las pruebas unitarias no necesitan la API levantada. Las de integración y Postman escriben registros reales mediante HTTP y requieren el histórico. No son una simulación sin efectos. El CLI oficial de Postman se incluye como dependencia de desarrollo; no depende de una instalación gráfica para ejecutar la colección.
''')
table(['Comprobación registrada', 'Resultado y alcance'], [
    [esc('Carga histórica'), esc('9068 filas; todos los campos de las 19 tablas conciliados antes del commit.')],
    [esc('Pruebas unitarias'), esc('4 correctas: validación de entradas y exclusión de importación.')],
    [esc('Integración HTTP'), esc('8 escenarios correctos; el ejecutor también cuenta el test padre.')],
    [esc('Postman CLI oficial'), esc('144 peticiones y 155 aserciones; 0 fallos.')],
    [esc('Persistencia'), esc('Estado de importación y venta PAGADA idénticos antes y después de reiniciar el motor.')],
    [esc('Dependencias'), esc('La evidencia guardada registra 0 vulnerabilidades en la auditoría de esa ejecución.')],
], ['5cm', '11.1cm'])
add(r'''
Estos números proceden de docs/evidencias/validacion.json y sus registros asociados; describen la ejecución guardada, no una garantía sobre cambios futuros. Los archivos registran fechas UTC del 17 de octubre, que pueden corresponder todavía al 16 de octubre en Guatemala. Para un resultado actualizado se vuelven a ejecutar las comprobaciones.

\subsection{Escenarios de integración}
\begin{enumerate}
\item Estado del histórico protegido y conciliado.
\item CRUD de catálogos y entidades relacionadas, incluyendo conflictos.
\item Stock insuficiente, rollback y ajustes por UPDATE y DELETE.
\item Abonos parciales, sobrepago, correcciones y protecciones.
\item Lotes con consumo agregado, rollback total y varios pagos.
\item Competencia concurrente por las últimas unidades.
\item Anulación con devolución única e impacto en reportes.
\item Comparación de las tres vistas con una referencia calculada desde los datos obtenidos por la API.
\end{enumerate}
En las evidencias de integración, los listados grandes se guardan como muestras identificadas. No deben interpretarse como si solo existieran las filas visibles en la muestra. La comprobación automatizada consulta las páginas necesarias.

\section{Evidencias de inventario y pagos}
Las imágenes siguientes se generaron a partir de respuestas reales guardadas por el CLI oficial de Postman. Son capturas de una representación HTML del registro HTTP, no capturas de la interfaz gráfica de Postman. Las respuestas y aserciones originales están en postman-oficial.json; los HTML permiten inspeccionar el mismo contenido con un navegador.

\subsection{Inventario: rechazo, conservación y descuento}
La secuencia muestra stock inicial 10, intento inválido de 11, respuesta Stock insuficiente y conservación del inventario. A continuación, una venta de 2 unidades produce stock 8. La evidencia combina la respuesta del POST y el GET posterior para comprobar el efecto en la base.
\evidencia{evidencias/inventario.png}{Respuestas reales del CLI de Postman: error de stock, rollback y descuento válido. Representación del registro HTTP.}
\clearpage
\subsection{Abonos y cambio automático de estado}
La segunda secuencia muestra una venta de total 50, un abono parcial de 20 y el abono restante de 30. El GET de la venta permite comprobar REGISTRADA antes de completar el pago y PAGADA con saldo cero después.
\evidencia{evidencias/pagos.png}{Respuestas reales del CLI de Postman: pagos parciales y transición automática a PAGADA. Representación del registro HTTP.}
\clearpage
\subsection{Comprobación de persistencia}
El archivo persistencia.json conserva el estado del histórico y la misma venta pagada antes y después de reiniciar SQL Server. El id de la venta de esa evidencia es 1546939428; total y pagado permanecen en 50 y saldo en 0. Es un ejemplo de la ejecución registrada, no el ID de cada nueva demostración.

Para reproducirla, consultar el estado de importación y una venta de prueba, guardar las respuestas, reiniciar únicamente sqlserver, esperar su disponibilidad y repetir los GET. Comparar identificadores, estados, importes y hash. Esta prueba verifica el volumen; no requiere borrar ni volver a importar nada.

\section{Inspección estructural con DBeaver}
Crear una conexión SQL Server hacia 127.0.0.1, puerto 1433 y base ComercialLaEstrella, usando las credenciales DB\_USER y DB\_PASSWORD de .env. Para el certificado local se utiliza encrypt=true y trustServerCertificate=true. No copiar las contraseñas al manual ni a capturas públicas.

En la instalación local se guardó la conexión Comercial La Estrella. Expandir base, esquemas, dbo y tablas para mostrar su estructura; las vistas y triggers se inspeccionan en sus nodos correspondientes. El modo de solo lectura del cliente ayuda a evitar cambios accidentales, pero no convierte por sí mismo al login de la API en un usuario SQL con permisos exclusivamente SELECT.

Durante la evaluación no ejecutar INSERT, UPDATE ni DELETE directamente desde DBeaver. Las operaciones de negocio se muestran en Postman y las consultas de estructura se mantienen separadas de las pruebas CRUD.

\section{Guion detallado para la demostración}
\begin{enumerate}
\item Mostrar el repositorio y ubicar Compose e init.sql en la raíz del proyecto. Explicar que SQL Server se ejecuta dentro de Docker y la API en Node en el equipo.
\item Mostrar docker compose ps -a y el resultado de db-init. Identificar motor saludable, inicializador terminado correctamente y volumen persistente.
\item Ejecutar health y consultar admin/importacion. Explicar los 9068 registros históricos y por qué los conteos actuales pueden incluir pruebas.
\item Seleccionar el entorno local e iniciar una sola vez la preparación. Explicar baseUrl y los IDs generados por el script.
\item Demostrar CRUD de pais. Leer el cuerpo de creación, consultar, actualizar, eliminar y justificar el 404 final.
\item Mostrar una ruta de clave compuesta y explicar por qué catálogo necesita tienda más producto y detalle necesita venta más producto.
\item Ejecutar las pruebas de inventario. Justificar 400 al pedir 11 con stock 10 y el GET que confirma 10; luego vender 2 y comprobar 8.
\item Ejecutar abonos 20 y 30 de la venta de 50. Mostrar el GET entre ambos y el estado PAGADA final; ubicar Insert\_Pago en SQL.
\item Mostrar anulación sin pagos y devolución única. Explicar por qué repetirla se rechaza.
\item Ejecutar las tres vistas y explicar las columnas, JOIN, exclusión de anuladas y preagregación.
\item Abrir Test Results o el resumen del runner; interpretar fallos esperados frente a aserciones fallidas.
\item Mostrar el PDF, la colección exportada y el código. Realizar cualquier ejercicio práctico con validación y una prueba HTTP del comportamiento modificado.
\end{enumerate}

\subsection{Preparación de una grabación}
Antes de grabar, realizar una ejecución completa para confirmar conexión y orden; mantener visibles los códigos y el JSON; ampliar texto si hace falta y ocultar credenciales. Para la toma definitiva iniciar otra preparación y seguir la misma secuencia. No depender de un ID de una sesión anterior ni reiniciar a mitad de una transacción de demostración. Mostrar el resultado del test junto con la respuesta evita interpretar un 400 esperado como un fallo del proyecto.

\section{Solución de problemas}
''')
table(['Síntoma', 'Comprobación y acción'], [
    [esc('ECONNREFUSED en Postman'), esc('Verificar npm start, baseUrl, puerto 3000 y health. Mantener abierta la terminal de la API.')],
    [esc('La API no inicia por SQL'), esc('Revisar motor saludable, logs de db-init y credenciales del volumen. Una contraseña editada en .env no cambia un login existente.')],
    [esc('Variables sin resolver'), esc('Seleccionar el entorno correcto y ejecutar la primera petición de preparación. Revisar Variables de la colección.')],
    [esc('409 al repetir Crear'), esc('Ya existe esa clave. No repetir el POST sobre el mismo ID salvo para demostrar el conflicto; comenzar una ejecución nueva desde preparación.')],
    [esc('404 después de eliminar'), esc('Es el resultado esperado de Confirmar eliminacion. Revisar la aserción correspondiente.')],
    [esc('409 al borrar una entidad'), esc('Tiene referencias o una protección de negocio. Eliminar auxiliares en orden inverso y no desactivar FK.')],
    [esc('400 por stock'), esc('Consultar el catálogo de la tienda correcta; comprobar cantidad y clave compuesta. El intento fallido no debe descontar nada.')],
    [esc('400 por fecha o decimal'), esc('Usar los formatos de fecha admitidos y números JSON con hasta dos decimales; no enviar símbolos de moneda.')],
    [esc('Importación devuelve 404'), esc('La ruta está deshabilitada. Si el histórico ya existe, esto es normal y no debe habilitarse para repetirlo.')],
    [esc('Código editado sin efecto'), esc('Recompilar antes de npm start o utilizar npm run dev para recarga de desarrollo.')],
    [esc('Más filas que el manifiesto'), esc('Las pruebas agregan datos Demo/QA. Diferenciar el histórico importado de los registros actuales.')],
    [esc('db-init aparece Exited'), esc('Es normal si terminó con código 0. Si terminó con otro código, revisar su log antes de continuar.')],
], ['5cm', '11.1cm'])
add(r'''
\clearpage\section{Seguridad, límites y entrega reproducible}
Los logins de aplicación no son administradores. estrella\_api recibe permisos CRUD por tabla y SELECT de vistas/control; estrella\_import tiene permisos para la carga y su registro de control, y pertenece al rol importador. Ninguno necesita crear tablas desde la API. El login sa se reserva para el bootstrap de la infraestructura.

La aplicación no implementa autenticación general de usuarios, autorización por roles HTTP ni exposición pública. Su alcance es evaluación local. La protección de importación combina habilitación temporal, clave de cabecera, archivo permitido, rol SQL y transacción. No es un endpoint de carga arbitraria para cualquier conjunto de datos.

El archivo .env, node\_modules, dist, logs y los comprimidos de entrega se excluyen de Git. El ZIP se genera bajo demanda con npm run package y usa el formato exigido por el enunciado, [BD1]\_ProyectoFase2\_202300476.zip. No hace falta mantenerlo en el repositorio. El script excluye las credenciales y los artefactos de ejecución; quien recibe la entrega genera su propio .env, instala dependencias y compila.

\subsection{Documentación editable}
La fuente de este manual es docs/Manual\_Tecnico\_Fase2.tex. El generador scripts/generate-manual.py obtiene los campos de las entidades, ejemplos de Postman, respuestas esperadas y conteos desde los archivos del proyecto. El diseño conserva la portada institucional y la paleta morada y azul del manual de la fase 1.
\begin{lstlisting}
# Desde Proyecto 2: regenerar LaTeX y compilar el PDF
python3 scripts/generate-manual.py --build
\end{lstlisting}
El PDF final se guarda en docs/output/pdf/Manual\_Tecnico\_Fase2.pdf. La compilación utiliza un directorio temporal; no deja archivos auxiliares de LaTeX en la entrega. Si se ajusta contenido narrativo generado, editar el generador y regenerar para conservar la reproducibilidad.

\clearpage\section{Preguntas de estudio y respuestas}
''')
qas = [
    ('¿Qué diferencia hay entre API y base de datos?', 'La API ofrece HTTP y valida la entrada; SQL Server almacena registros y aplica integridad y reglas transaccionales. Postman habla con la API.'),
    ('¿Por qué TypeORM si existe init.sql?', 'TypeORM facilita el acceso parametrizado y los repositorios. El DDL explícito permite revisar y reproducir constraints, vistas y triggers sin depender de sincronización automática.'),
    ('¿Por qué el stock no pertenece al producto?', 'Una tienda puede tener precio y existencia distintos para el mismo producto; por eso el stock depende de la clave tienda-producto.'),
    ('¿Qué contienen inserted y deleted?', 'Son conjuntos de filas de la sentencia que activó el trigger. inserted contiene versiones nuevas y deleted versiones anteriores; UPDATE usa ambos.'),
    ('¿Quién cambia la venta a PAGADA?', 'El trigger Insert_Pago en SQL Server compara totales y actualiza el estado. Node comunica el resultado y el GET lo permite observar.'),
    ('¿Qué es rollback?', 'Deshacer los cambios de una transacción fallida. Un detalle con stock insuficiente no debe dejar un descuento parcial de inventario.'),
    ('¿Qué diferencia hay entre PK y FK?', 'La PK identifica de manera única una fila. La FK exige que la referencia exista en otra clave válida y evita registros huérfanos.'),
    ('¿Por qué no unir detalles y pagos directamente?', 'Porque varios detalles y varios pagos se multiplican en el JOIN. Se suman por separado y luego se unen por venta.'),
    ('¿Qué cambia al reiniciar el backend?', 'Se reinician el proceso y sus conexiones; los datos permanecen en SQL y las variables de Postman no se regeneran.'),
    ('¿Qué cambia al ejecutar la primera petición de Postman?', 'Su Pre-request genera IDs para una nueva prueba y después comprueba health. No borra tablas ni vuelve a cargar el histórico.'),
    ('¿Por qué se omite el descuento en la carga original?', 'El dataset ya contiene existencias históricas. Tratar esos detalles como ventas nuevas descontaría dos veces. La excepción es controlada y exclusiva para el archivo original.'),
    ('¿Una respuesta roja significa error de la prueba?', 'No necesariamente. Si se está probando un rechazo y la respuesta coincide con lo esperado, la aserción pasa aunque el código HTTP sea 400, 404 o 409.'),
]
for q, a in qas:
    add(r'\needspace{4\baselineskip}\textbf{' + esc(q) + r'}\par ' + esc(a) + r'\par')

add(r'\clearpage\appendix\section{Referencia detallada de las 19 entidades}')
add(r'''Las siguientes fichas se obtienen de los metadatos reales y de la colección entregada. Cada una muestra clave, ruta individual, campos, dependencias y cuerpos de ejemplo. Para todas las entidades, POST y GET de listado utilizan /api/ seguido del nombre de tabla; GET individual, PUT y DELETE usan la ruta individual. Los ejemplos con llaves dobles se envían desde Postman después de la preparación. No son JSON independiente hasta que Postman sustituye las variables.
''')
purposes = {
    'pais': ('Catálogo de países para ubicar departamentos.', 'No depende de otras entidades. El nombre es único.'),
    'departamento': ('División territorial asociada a un país.', 'id_pais referencia pais. El nombre es único dentro de cada país.'),
    'municipio': ('Municipio utilizado por personas y tiendas.', 'id_departamento referencia departamento. El nombre es único dentro del departamento.'),
    'tipo_tienda': ('Clasificación comercial de las tiendas.', 'No depende de otras entidades. El nombre es único.'),
    'tipo_identificacion': ('Tipos de documento de los clientes.', 'No depende de otras entidades. El nombre es único.'),
    'cargo': ('Catálogo de cargos del personal.', 'No depende de otras entidades. El nombre es único.'),
    'categoria': ('Categoría de los productos.', 'No depende de otras entidades. El nombre es único.'),
    'marca': ('Marca comercial de los productos.', 'No depende de otras entidades. El nombre es único.'),
    'estado_venta': ('Estados fijos del ciclo de venta.', '1 REGISTRADA, 2 PAGADA, 3 ANULADA. Nombres y claves del sistema protegidos; escrituras de prueba devuelven 409.'),
    'metodo_pago': ('Formas de pago permitidas.', 'No depende de otras entidades. El nombre es único.'),
    'persona': ('Datos personales compartidos por clientes y empleados.', 'id_municipio referencia municipio. correo es nullable y único solo cuando no es NULL.'),
    'tienda': ('Establecimiento donde se gestionan inventario y ventas.', 'Referencia municipio y tipo_tienda. Su nombre es único.'),
    'empleado': ('Asignación de una persona a tienda y cargo.', 'Referencia persona, tienda y cargo. Una persona tiene una sola fila de empleado; la clave alternativa empleado-tienda es referenciada por venta.'),
    'cliente': ('Identificación comercial de una persona compradora.', 'Referencia persona y tipo_identificacion. Persona es única y el par tipo-número de documento también.'),
    'producto': ('Datos maestros de productos, sin stock global.', 'Referencia categoria y marca. El precio y las existencias se mantienen en catalogo_producto.'),
    'catalogo_producto': ('Precio vigente y stock de un producto en una tienda.', 'Referencia tienda y producto. Precio positivo, stock no negativo y clave compuesta. No se elimina si hay detalles asociados.'),
    'venta': ('Encabezado de la transacción comercial.', 'Referencia cliente, estado_venta y el par empleado-tienda. Debe comenzar REGISTRADA; consultar devuelve estado y totales calculados.'),
    'detalle_venta': ('Producto, cantidad y precio histórico de una venta.', 'Referencia venta y producto. El trigger exige catálogo de la tienda, stock suficiente y venta registrada sin pagos. subtotal=cantidad*precio_unitario.'),
    'pago': ('Abono aplicado a una venta por un método de pago.', 'Referencia venta y metodo_pago. Monto positivo. No se permite trasladar id_venta en PUT; su trigger recalcula el estado.'),
}
entity_items = {i['name'].split(' ')[0]: i for i in collection['item'][1]['item']}
for index, spec in enumerate(schema):
    name = spec['table']
    if index and (index >= 10 or index % 2 == 0):
        add(r'\clearpage')
    add(r'\needspace{24\baselineskip}\subsection{' + esc(name) + '}')
    add(esc(purposes[name][0]) + r'\par ' + esc(purposes[name][1]))
    route = '/api/' + name + ''.join('/:' + k for k in spec['keys'])
    add(r'\textbf{Ruta individual:} \path{' + route + r'}\par')
    rows = []
    for field, meta in spec['fields'].items():
        typ = {'integer': 'INT', 'decimal': 'DECIMAL(12,2)', 'date': 'DATETIME2(0)', 'string': f"NVARCHAR({meta.get('length', 300)})"}[meta['type']]
        rule = 'PK; requerido en POST, inmutable en PUT' if field in spec['keys'] else 'Requerido en POST; modificable en PUT'
        if meta.get('nullable'): rule = 'Campo requerido en POST; admite NULL'
        if name == 'pago' and field == 'id_venta':rule = 'Requerido en POST; inmutable en PUT'
        rows.append([code(field), code(typ), esc(rule)])
    table(['Campo', 'Tipo SQL', 'Contrato de escritura'], rows, ['5cm', '4.3cm', '6.8cm'], keep=True)
    requests = entity_items[name]['item']
    create = next((q for q in requests if q['name'] in ['Crear', 'POST duplicado']), None)
    update = next((q for q in requests if q['name'] in ['Actualizar', 'PUT protegido']), None)
    if create:
        add(r'\textbf{Cuerpo de POST de la colección:}')
        listing(create['request']['body']['raw'])
    if update:
        add(r'\textbf{Cuerpo de PUT de la colección:}')
        listing(update['request']['body']['raw'])
    if name == 'estado_venta':
        add(esc('Estos cuerpos son pruebas de rechazo: el POST duplicado y el PUT protegido deben responder 409. No crean nuevos estados.'))
    elif name in ['detalle_venta', 'pago']:
        add(esc('La subcarpeta incluye una petición previa de preparación. Ejecutarla antes del CRUD y conservar el orden de toda la colección.'))

add(r'\clearpage\section{Matriz de todas las peticiones de Postman}')
add(r'''Esta matriz se genera desde los scripts de prueba de la colección. Los códigos de rechazo son resultados esperados. Las verificaciones adicionales indican qué valor funcional comprobar junto con el estado HTTP. Una ejecución completa utiliza 144 peticiones y 155 aserciones en la versión documentada.
''')


def request_rows(items):
    rows = []
    for item in items:
        scripts = '\n'.join('\n'.join(ev['script']['exec']) for ev in item.get('event', []) if ev['listen'] == 'test')
        status = re.search(r'to\.have\.status\((\d+)\)', scripts)
        extra = []
        for prop, value in re.findall(r'pm\.response\.json\(\)\.([\w.]+)\)\.to\.eql\(([^)]+)\)', scripts):
            extra.append(prop + '=' + value)
        if "to.be.an('array')" in scripts:extra.append('data es un arreglo')
        desc = esc(item['name'])
        if extra:desc += r'\newline{\scriptsize ' + esc('; '.join(extra)) + '}'
        rows.append([desc, code(item['request']['method']), status.group(1) if status else '-', r'\path{' + item['request']['url'].replace('{{baseUrl}}', '') + '}'])
    return rows


for folder in collection['item']:
    nested = any('item' in item for item in folder['item'])
    space = 7 if nested else max(15, 2 * len(folder['item']) + 4)
    add(r'\needspace{' + str(space) + r'\baselineskip}\subsection{' + esc(folder['name']) + '}')
    if nested:
        for entity in folder['item']:
            add(r'\needspace{15\baselineskip}\subsubsection{' + esc(entity['name']) + '}')
            table(['Petición / validación', 'Método', 'HTTP', 'Ruta relativa a baseUrl'], request_rows(entity['item']), ['5.3cm', '1.7cm', '1.2cm', '7.9cm'], keep=True)
    else:
        table(['Petición / validación', 'Método', 'HTTP', 'Ruta relativa a baseUrl'], request_rows(folder['item']), ['5.3cm', '1.7cm', '1.2cm', '7.9cm'], keep=True)

add(r'\clearpage\section{Implementación SQL de las vistas y triggers}')
add(r'''Los listados siguientes se incluyen directamente desde init.sql para mantener correspondencia con el código entregado. El esquema completo de tablas, logins y permisos se consulta en ese archivo. Estos fragmentos explican el comportamiento; no se ejecutan manualmente sobre los datos durante la calificación.
''')
sql_lines = (ROOT / 'init.sql').read_text().splitlines()
for kind, names in [('VIEW', ['Vista_Ventas_Ubicacion', 'Vista_Top_Productos', 'Vista_Consulta_Ventas', 'Vista_Saldos_Pendientes']), ('TRIGGER', ['Insert_Detalle', 'Insert_Pago', 'Validar_Venta', 'Proteger_Catalogo', 'Proteger_Estados'])]:
    for name in names:
        start = next(i for i, line in enumerate(sql_lines) if line.startswith('CREATE OR ALTER ' + kind + ' dbo.' + name + ' '))
        end = next(i for i in range(start + 1, len(sql_lines)) if sql_lines[i] == 'GO')
        add(r'\par\medskip\noindent\begin{minipage}{\textwidth}\subsection{' + esc(name) + '}')
        add(r'\lstinputlisting[language=SQL,firstline=' + str(start + 1) + ',lastline=' + str(end) + r']{../init.sql}')
        add(r'\end{minipage}\par\medskip')

add(r'''\clearpage\section{Fuentes y trazabilidad}
\begin{enumerate}
\item Enunciado oficial: ProyectoFase2\_SBD1\_2S2026.pdf, sección 4 de entregables y rúbrica de documentación. Se incluye en docs.
\item Hoja de calificación: Hoja\_Calificacion\_Proyecto\_Fase\_2\_BD1.pdf. Se incluye en docs; documentación vale 15 puntos.
\item Modelo y dataset de la fase 1: documentos previos del repositorio y origen registrado en data/manifest.json.
\item Código fuente de la fase 2: init.sql; docker-compose.yml; src/config; src/entities; src/controllers; src/routes; src/services; scripts y tests.
\item Colección entregada: postman/ComercialLaEstrella.postman\_collection.json y local.postman\_environment.json. De aquí se obtienen los ejemplos y códigos de la matriz.
\item Evidencia original: docs/evidencias/postman-oficial.json, integracion.json, persistencia.json y validacion.json. Las imágenes de inventario y pagos representan respuestas de ese registro.
\item Repositorio del proyecto: \url{https://github.com/ricardious/SBD1_2S2026}. La implementación se integró a develop y main mediante los PR 1 y 2; el presente manual amplía la documentación de esa implementación.
\end{enumerate}
\end{document}
''')

source = DOCS / f'{NAME}.tex'
source.write_text('\n\n'.join(parts) + '\n')
print(f'LaTeX generado: {source}')
parser = argparse.ArgumentParser()
parser.add_argument('--build', action='store_true')
args = parser.parse_args()
if args.build:
    output = DOCS / 'output/pdf'
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bd1-manual-') as tmp:
        command = ['latexmk', '-xelatex', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error', f'-outdir={tmp}', source.name]
        process = subprocess.run(command, cwd=DOCS, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (output / 'compilacion.log').write_text(process.stdout)
        if process.returncode:
            print(process.stdout[-10000:])
            raise SystemExit(process.returncode)
        shutil.copy2(Path(tmp) / f'{NAME}.pdf', output / f'{NAME}.pdf')
        print(f'PDF generado: {output / (NAME + ".pdf")}')
