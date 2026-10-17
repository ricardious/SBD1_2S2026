"""Ejecuta un escenario HTTP y captura sus GET en un navegador real.
Requiere API local disponible, histórico cargado y agent-browser con Chromium.
Crea registros de demostración; no modifica el archivo histórico.
"""
import re,json,subprocess,urllib.request,urllib.error,secrets,datetime,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/"docs/evidencias/capturas-api";out.mkdir(exist_ok=True)
base="http://127.0.0.1:3000/api";id=1700000000+secrets.randbelow(90000000)
records=[];pictures=[]
cli=["npx","--yes","agent-browser","--session","fase2-manual"]
def command(*args):
 return subprocess.run(cli+list(args),check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout
def call(method,path,body=None,status=200):
 data=json.dumps(body).encode() if body is not None else None
 request=urllib.request.Request(base+path,data=data,method=method,headers={"Content-Type":"application/json"})
 try: response=urllib.request.urlopen(request)
 except urllib.error.HTTPError as error:response=error
 raw=response.read();value=json.loads(raw) if raw else None
 assert response.status==status,(method,path,response.status,value)
 records.append(dict(fecha_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),method=method,path=path,request=body,status=response.status,response=value))
 return value

def capture(name,path):
 command("open",base+path)
 snapshot=command("snapshot")
 ref=re.search(r'checkbox "Pretty-print".*ref=(e[0-9]+)',snapshot).group(1)
 command("check","@"+ref)
 command("screenshot",str(out/(name+".png")))
 pictures.append(dict(archivo=name+".png",url=base+path,fecha_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=hashlib.sha256((out/(name+".png")).read_bytes()).hexdigest()))
 print("Capturada",name,flush=True)

command("open",base+"/health")
command("set","viewport","850","420","2")
call("GET","/health");capture("01_conexion","/health")
call("GET","/admin/importacion");capture("02_carga","/admin/importacion")
call("POST","/pais",{"id_pais":id,"nombre":f"Manual pais {id}"},201)
call("PUT",f"/pais/{id}",{"nombre":f"Manual pais actualizado {id}"})
capture("03_crud_actualizado",f"/pais/{id}")
call("DELETE",f"/pais/{id}",status=204)
call("GET",f"/pais/{id}",status=404);capture("04_crud_eliminado",f"/pais/{id}")
call("POST","/producto",{"id_producto":id,"nombre":f"Manual producto {id}","descripcion":"Evidencia tecnica: inventario y pagos","id_categoria":1,"id_marca":1},201)
call("POST","/catalogo_producto",{"id_tienda":1,"id_producto":id,"precio_vigente":25,"existencia_actual":10},201)
catalog=f"/catalogo_producto/1/{id}"
capture("05_stock_inicial",catalog)
venta={"id_venta":id,"fecha_venta":"2026-10-16T12:00:00","id_tienda":1,"id_empleado":1,"id_cliente":1,"id_estado_venta":1}
call("POST","/venta",venta,201)
def detail(q):return {"id_venta":id,"id_producto":id,"cantidad":q,"precio_unitario":25,"subtotal":q*25}
failed=call("POST","/detalle_venta",detail(11),400);assert failed["error"]=="Stock insuficiente"
assert call("GET",catalog)["existencia_actual"]==10
call("GET",f"/detalle_venta/{id}/{id}",status=404)
capture("06_stock_tras_rechazo",catalog)
call("POST","/detalle_venta",detail(2),201)
assert call("GET",catalog)["existencia_actual"]==8
capture("07_stock_descontado",catalog)
call("POST","/pago",{"id_pago":id,"id_venta":id,"id_metodo_pago":1,"monto":20},201)
v=call("GET",f"/venta/{id}");assert v["estado"]=="REGISTRADA" and v["saldo_pendiente"]==30
capture("08_abono_parcial",f"/venta/{id}")
call("POST","/pago",{"id_pago":id+1,"id_venta":id,"id_metodo_pago":1,"monto":30},201)
v=call("GET",f"/venta/{id}");assert v["estado"]=="PAGADA" and v["saldo_pendiente"]==0
capture("09_venta_pagada",f"/venta/{id}")
for name,path in [("10_ventas_ubicacion","/reportes/ventas-ubicacion"),("11_top_productos","/reportes/top-productos"),("12_saldos","/reportes/saldos-pendientes")]:
 call("GET",path);capture(name,path)
report=dict(fixtureId=id,capturas=pictures,peticiones=records,origen="Capturas directas del navegador consultando la API local. Sin reconstruccion HTML ni sustitucion de respuestas.")
(root/"docs/evidencias/manual-http.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
command("close")
print("Fixture",id,"Peticiones",len(records),"Capturas",len(pictures),flush=True)
