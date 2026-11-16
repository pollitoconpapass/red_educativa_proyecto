# Capa de aplicación — SDN EduNet (Ryu + Mininet)

Controlador Ryu que programa en los switches OpenFlow la ACL de acceso a documentos
calculada desde `DOCUMENTO` y `PERMISO_ACCESO` de la BD `red_educativa`.

## Cómo funciona

- Cada documento `id_documento = N` se sirve en `http://<ip_del_autor>:8000+N/`.
  El puerto identifica al documento, por eso OpenFlow puede autorizarlo por separado.
- Al conectar un switch, el controlador lee la BD y, por cada host y cada documento
  **sin fila en `PERMISO_ACCESO`**, instala un `drop` de prioridad 100. El reenvío
  normal (switch L2 aprendido) queda en prioridad 10.
- Los hosts `invitado-*` no tienen `id_usuario`, así que no tienen permisos.

| Switch | Sede        | Hosts                        |
| ------ | ----------- | ---------------------------- |
| s1     | Lima        | doc-carlos (1), est-luis (3) |
| s2     | La Libertad | doc-ana (2), est-maria (4)   |
| s3     | Junín       | est-pedro (5), invitado-1    |
| s4     | Arequipa    | est-lucia (6), invitado-2    |
| s5     | Loreto      | invitado-3, invitado-4       |

El detalle de IP/MAC/`id_usuario` está en `edunet/config.py`.

## Estructura

```
capa_aplicacion/
├── sdn_controlador.py      # app Ryu (se ejecuta con ryu-manager)
├── topologia.py            # topología Mininet
├── servidor_documentos.py  # servidor HTTP de documentos de un autor
├── requirements.txt
├── config/                 # lógica reutilizable
│   ├── config.py           # sedes, hosts, IP/MAC/id_usuario
│   ├── db.py               # conexión y consultas a MySQL
│   └── politica.py         # ACL calculada desde PERMISO_ACCESO
└── tests/
    └── test_politica.py
```

Los tres scripts se ejecutan desde `capa_aplicacion/`, así se importa el paquete
`edunet` sin tocar `sys.path`.

## Instalación (VM Ubuntu con Mininet)

```bash
sudo apt install -y mininet python3-pip
pip3 install -r requirements.txt
```

`.env` (raíz del proyecto) debe apuntar a la BD de la capa de datos:

```
URL=jdbc:mysql://4.149.122.251:3306/red_educativa
USERNAME=appuser
PASSWORD=...
```

También se aceptan las claves por separado (`SERVER_HOST`, `PORT`, `DATABASE`)
y variables de entorno con esos mismos nombres.

La BD tiene que estar levantada antes de arrancar el controlador: si no responde,
el controlador no arranca (no se deja la red sin política).

### Si la capa de datos está en otra VM

El código no cambia: solo el `URL` del `.env` apunta a la IP de la VM de datos.
En la VM de datos hay que permitir el acceso remoto:

```bash
# /etc/mysql/mysql.conf.d/mysqld.cnf
bind-address = 0.0.0.0
sudo systemctl restart mysql
```

Y abrir el puerto 3306 **solo para la IP de la VM de aplicación** (regla de entrada
del NSG de Azure y, si está activo, `ufw`). El usuario `appuser@'%'` ya está en
`capa_datos/creacion_permisos.sql`.

## Arranque

```bash
# Terminal 1
ryu-manager sdn_controlador.py

# Terminal 2
sudo python3 topologia.py
```

Dentro de la CLI de Mininet, levantar el servidor de documentos de un autor:

```
mininet> doc-carlos python3 servidor_documentos.py 1 &
mininet> doc-ana python3 servidor_documentos.py 2 &
mininet> est-luis python3 servidor_documentos.py 3 &
mininet> est-maria python3 servidor_documentos.py 4 &
```

## Pruebas funcionales

```
mininet> est-luis curl -s --max-time 3 http://10.0.1.11:8301/   # 200 (permiso 502)
mininet> est-luis curl -s --max-time 3 http://10.0.2.11:8302/   # sin salida: bloqueado
mininet> est-maria curl -s --max-time 3 http://10.0.1.11:8301/  # 200 (permiso 503)
mininet> est-pedro curl -s --max-time 3 http://10.0.2.11:8302/  # 200 (permiso 505)
mininet> est-lucia curl -s --max-time 3 http://10.0.1.11:8301/  # sin salida: bloqueado
mininet> doc-carlos curl -s --max-time 3 http://10.0.1.12:8303/ # 200 (permiso 507)
mininet> invitado-1 curl -s --max-time 3 http://10.0.1.11:8301/ # sin salida: bloqueado
```

Evidencia de las reglas instaladas:

```bash
sudo ovs-ofctl -O OpenFlow13 dump-flows s1 | grep "tcp_dst=8302"
```

## Prueba unitaria

```bash
cd capa_aplicacion
python3 -m unittest discover -s tests -v
```

## Límites conocidos

- La política se instala al conectar cada switch: si cambian los permisos en la BD
  hay que reiniciar el controlador. `shortcut: reaplicar reglas en caliente, cuando la BD cambie durante la demo`
- El usuario se identifica por la MAC fija del host: quien falsifique esa MAC evita la ACL.
- Solo se filtra TCP a los puertos de documentos; el resto del tráfico es reenvío L2 normal.
