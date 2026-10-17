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
''')

proof = json.loads((DOCS / 'evidencias/manual-http.json').read_text())
fixture = proof['fixtureId']
operations = proof['peticiones']


def operation(method, path, status=None):
    return next(q for q in operations if q['method'] == method and q['path'] == path and (status is None or q['status'] == status))


def captured_request(item):
    add(r'\textbf{Operación ejecutada:} \path{' + item['method'] + ' /api' + item['path'] + '}')
    if item['request'] is not None:
        listing(json.dumps(item['request'], ensure_ascii=False, indent=2))
    add(r'\textbf{Respuesta recibida: HTTP ' + str(item['status']) + '}')
    if item['response'] is not None:
        listing(json.dumps(item['response'], ensure_ascii=False, indent=2))


def gallery(title, entries):
    add(r'\Needspace{28\baselineskip}\subsubsection*{' + esc(title) + '}')
    for index, (filename, caption) in enumerate(entries):
        add(r'\begin{figure}[H]\centering\includegraphics[width=\textwidth]{evidencias/capturas-api/' + filename + r'.png}\caption{' + esc(caption) + r'}\end{figure}')


content = (DOCS / 'manual/Contenido.tex').read_text()
for chunk in re.split(r'(% (?:TABLA_HISTORICO|TABLA_RUTAS|EVIDENCIA_ARRANQUE|EVIDENCIA_CRUD|EVIDENCIA_INVENTARIO|EVIDENCIA_PAGOS|EVIDENCIA_REPORTES))', content):
    if chunk == '% TABLA_HISTORICO':
        table(['Tabla', 'Filas originales', 'Clave primaria'], [
            [code(t['table']), esc(f"{manifest['counts'][t['table']]:,}"), ', '.join(code(k) for k in t['keys'])] for t in schema
        ] + [[r'\textbf{Total}', r'\textbf{9,068}', '19 tablas de negocio']], ['5cm', '3cm', '8.1cm'])
    elif chunk == '% TABLA_RUTAS':
        add(r'\subsection{Rutas por entidad}')
        add('Los listados y altas utilizan el nombre de la entidad; las operaciones sobre un registro añaden las claves de esta tabla. Las rutas de lote preceden a las rutas individuales para evitar interpretar lote como un ID.')
        table(['Entidad', 'Ruta individual a partir de /api'], [
            [code(t['table']), r'\path{/' + t['table'] + ''.join('/:' + k for k in t['keys']) + '}'] for t in schema
        ], ['5cm', '11.1cm'])
    elif chunk == '% EVIDENCIA_ARRANQUE':
        add(r'\subsection{Comprobación sobre la instalación en servicio}')
        add('Las capturas se obtuvieron directamente en un navegador que consultó la API local. Muestran el JSON servido por el backend, con el formato de lectura del navegador. No se reconstruyeron las respuestas en una página de presentación ni se simula la interfaz de Postman. La ejecución y sus códigos HTTP se conservaron en el registro de operaciones asociado.')
        gallery('Disponibilidad y estado de la carga', [
            ('01_conexion', 'GET /api/health sobre el servidor activo: estado ok y conexión con SQL Server 2022.'),
            ('02_carga', 'GET /api/admin/importacion: histórico confirmado, 9068 filas originales y ruta de carga deshabilitada.'),
        ])
    elif chunk == '% EVIDENCIA_CRUD':
        add(r'\subsection{Comprobación del ciclo de actualización y eliminación}')
        add('La operación registrada creó un país auxiliar, modificó su nombre mediante PUT y consultó el objeto actualizado. Después lo eliminó con DELETE y verificó la ausencia mediante GET. El registro de la ejecución confirmó 201, 200, 204 y 404 en los pasos correspondientes. Las capturas muestran el contenido obtenido antes y después de la eliminación.')
        gallery('Actualización y eliminación verificadas', [
            ('03_crud_actualizado', f'GET /api/pais/{fixture}: nombre actualizado conservado en el registro de prueba.'),
            ('04_crud_eliminado', f'GET /api/pais/{fixture} después de DELETE: Registro no encontrado, correspondiente al HTTP 404 registrado.'),
        ])
    elif chunk == '% EVIDENCIA_INVENTARIO':
        add(r'\subsection{Petición rechazada y resultado conservado}')
        captured_request(operation('POST', '/detalle_venta', 400))
        add('Después del rechazo se consultó también el detalle y se obtuvo 404. Esto confirma que la transacción no dejó registrado el movimiento que intentaba vender 11 unidades. La siguiente petición utilizó cantidad 2, precio 25 y subtotal 50; respondió 201 y permitió observar el descuento a 8.')
        gallery('Existencias antes y después de las operaciones', [
            ('05_stock_inicial', f'Catálogo del producto {fixture} en tienda 1, antes de registrar detalles: existencia_actual 10.'),
            ('06_stock_tras_rechazo', 'Consulta posterior al POST rechazado por stock: se conservan las 10 unidades.'),
            ('07_stock_descontado', 'Consulta posterior al POST válido de dos unidades: existencia_actual 8.'),
        ])
    elif chunk == '% EVIDENCIA_PAGOS':
        add(r'\subsection{Abonos ejecutados sobre la misma venta}')
        p1 = operation('POST', '/pago', 201)
        add('Primer abono enviado por HTTP:')
        listing(json.dumps(p1['request'], ensure_ascii=False, indent=2))
        add('El segundo abono conserva la venta y utiliza un ID de pago distinto y monto 30. Ambos POST respondieron 201. Las consultas siguientes corresponden a esa misma venta y permiten comprobar que el estado cambió por el registro de los abonos, sin un PUT manual que asignara PAGADA.')
        gallery('Conciliación observada en la API', [
            ('08_abono_parcial', f'GET /api/venta/{fixture} después del abono de Q20: REGISTRADA, total 50, pagado 20 y saldo 30.'),
            ('09_venta_pagada', 'La misma venta después del abono restante de Q30: PAGADA, total_pagado 50 y saldo_pendiente 0.'),
        ])
    elif chunk == '% EVIDENCIA_REPORTES':
        add(r'\subsection{Resultados consultados en el servidor}')
        add('Las capturas siguientes muestran el inicio de cada respuesta JSON obtenida directamente del endpoint. Se visualiza un extracto por el tamaño de la ventana; el registro de la ejecución conserva los arreglos completos. Las cifras corresponden al estado de la base tras las pruebas y no deben interpretarse como totales exclusivos del archivo histórico.')
        gallery('Consultas de las vistas', [
            ('10_ventas_ubicacion', 'GET /api/reportes/ventas-ubicacion: extracto de tiendas con ubicación, cantidad de ventas e importe facturado.'),
            ('11_top_productos', 'GET /api/reportes/top-productos: extracto ordenado por unidades vendidas; incluye categoría, marca e importe.'),
            ('12_saldos', 'GET /api/reportes/saldos-pendientes: extracto de ventas registradas con total, pagado y saldo calculado.'),
        ])
    else:
        add(chunk)

add(r'\clearpage\appendix\section{Implementación de las consultas y controles transaccionales}')
add('Los fragmentos de este anexo corresponden a las vistas y triggers que ejecuta la instalación descrita. Sus reglas se aplican en el motor cuando la API escribe o consulta los registros; no requieren ejecución manual de sentencias durante la operación del cliente.')
lines = (ROOT / 'init.sql').read_text().splitlines()
comments = {
    'Vista_Ventas_Ubicacion': 'La agregación previa por venta permite contar encabezados sin multiplicarlos por sus detalles. El filtro de estado se aplica antes de agrupar la facturación por establecimiento.',
    'Vista_Top_Productos': 'La agrupación utiliza el identificador del producto junto con sus dimensiones descriptivas; dos productos con el mismo nombre no se fusionan. Las ventas anuladas quedan excluidas.',
    'Vista_Consulta_Ventas': 'Los detalles y pagos se reducen a una fila por venta antes de unirlos. Los LEFT JOIN conservan ventas que todavía no tienen movimientos y COALESCE presenta sus importes como cero.',
    'Vista_Saldos_Pendientes': 'La selección reutiliza los importes consolidados y limita el resultado a REGISTRADA. No vuelve a calcular pagos ni modifica el estado al consultar.',
    'Insert_Detalle': 'El conjunto de ventas se bloquea antes del ajuste. El delta agrupa inserted y deleted, por lo que INSERT, UPDATE y DELETE utilizan la misma regla. La comparación con @@ROWCOUNT detecta catálogos ausentes o disponibilidad insuficiente y provoca el rechazo de toda la sentencia.',
    'Insert_Pago': 'La comprobación de venta anulada y de detalle previo precede al recálculo. La condición de cobertura utiliza la suma vigente después de insertar, modificar o eliminar pagos. La actualización del encabezado se origina dentro del motor.',
    'Validar_Venta': 'La validación distingue una transición automática desde Insert_Pago de una edición directa. Impide trasladar movimientos a otros datos de encabezado y devuelve inventario solamente cuando se pasa de REGISTRADA a ANULADA sin pagos.',
    'Proteger_Catalogo': 'La validación busca claves presentes en deleted que ya no están en inserted y comprueba si dan contexto a detalles. Así protege la desaparición de la asociación sin impedir el ajuste legítimo de existencias.',
    'Proteger_Estados': 'El control conserva los IDs y nombres que utilizan las operaciones y el histórico. Las pruebas de escritura sobre este catálogo deben terminar en conflicto y no en la creación de un cuarto estado.',
}
for kind, names in [('VIEW', ['Vista_Ventas_Ubicacion', 'Vista_Top_Productos', 'Vista_Consulta_Ventas', 'Vista_Saldos_Pendientes']), ('TRIGGER', ['Insert_Detalle', 'Insert_Pago', 'Validar_Venta', 'Proteger_Catalogo', 'Proteger_Estados'])]:
    for name in names:
        start = next(i for i, line in enumerate(lines) if line.startswith('CREATE OR ALTER ' + kind + ' dbo.' + name + ' '))
        end = next(i for i in range(start + 1, len(lines)) if lines[i] == 'GO')
        add(r'\par\medskip\noindent\begin{minipage}{\textwidth}\subsection{' + esc(name) + '}')
        add(esc(comments[name]))
        add(r'\lstinputlisting[language=SQL,firstline=' + str(start + 1) + ',lastline=' + str(end) + r']{../init.sql}')
        add(r'\end{minipage}\par\medskip')
add(r'\section{Referencias de la implementación}')
add(r'\begin{itemize}\item Enunciado ProyectoFase2\_SBD1\_2S2026 y hoja de calificación de la fase 2.\item Modelo y dataset de Comercial La Estrella de la fase 1.\item Código y colecciones del repositorio: \url{https://github.com/ricardious/SBD1_2S2026}.\item Registro de operaciones y capturas directas de la API, con identificador de escenario, fecha UTC y hash de las imágenes.\end{itemize}')
add(r'\end{document}')

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
