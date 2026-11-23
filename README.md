# Stockito_ManagementApp
Aplicación de gestión de almacenamiento para negocios pequeños como tiendas/almacenes, cuenta con gestión de stock, historial de ventas y distintos inicios de sesión dependiendo el usuario empleado/dueño.


Port from HTML to Python v.3.8.10
Para mantener el programa compatible con sistemas operativos más antigüos.



# STOCKITO

**Sistema de punto de venta (POS) y control de stock para comercios chicos**: kioscos, almacenes y despensas.

STOCKITO permite vender, cobrar, controlar el stock, llevar la caja por turnos y emitir tickets y reportes en PDF. Funciona en una sola computadora, se instala con un instalador de Windows y guarda los datos en una base SQLite local.

> **Estado del proyecto:** prototipo funcional (v1.0). Los tickets que emite **no son comprobantes fiscales** (ver [Limitaciones](#limitaciones-conocidas)).

<!-- Agregar capturas de pantalla en una carpeta /docs/capturas y enlazarlas acá -->

---

## Índice

1. [Funcionalidades](#funcionalidades)
2. [Requisitos](#requisitos)
3. [Tecnologías y programas utilizados](#tecnologías-y-programas-utilizados)
4. [Estructura del proyecto](#estructura-del-proyecto)
5. [Instalación y uso](#instalación-y-uso)
6. [Cómo generar el instalador de Windows](#cómo-generar-el-instalador-de-windows)
7. [Arquitectura y datos](#arquitectura-y-datos)
8. [Limitaciones conocidas](#limitaciones-conocidas)
9. [Hoja de ruta](#hoja-de-ruta)
10. [Créditos y licencia](#créditos-y-licencia)

---

## Funcionalidades

### Acceso y roles
- Primer ingreso guiado: se cargan los datos del local (nombre, dirección, CUIT opcional y condición frente al IVA) y la contraseña del **Dueño**.
- Dos roles: **Dueño** y **Empleado**. El dueño crea empleados desde la pestaña *Equipo*, con contraseña propia o generada, y puede generar una contraseña nueva o quitar empleados.
- Contraseñas guardadas como hash SHA-256 (no en texto plano).

| Función | Dueño | Empleado |
|---|:---:|:---:|
| Ventas, cobro y tickets | ✔ | ✔ |
| Corte y ventas del turno actual | ✔ | ✔ |
| Productos (agregar, editar, borrar) y códigos de barras | ✔ | ✔ |
| Ver la ganancia | ✔ | ✖ |
| Historial de turnos por fecha, con desglose y PDF | ✔ | ✖ |
| Equipo (empleados y contraseñas) y datos del local | ✔ | ✖ |

### Ventas
- Búsqueda por descripción o código, filtro por departamento y tarjetas de producto con color por departamento.
- **Escaneo de código de barras directo al ticket**: aunque el cursor no esté en el buscador, el producto se agrega solo, con aviso sonoro. Funciona con lectores con o sin "Enter" al final.
- Ticket con cantidades editables (＋/－) y total.
- **Productos sin código** (pan, fiambres, venta por monto): se agregan al instante con descripción y monto (tecla `F3`).
- **Control de stock en la venta:** no se pueden agregar productos sin stock ni más unidades que las disponibles.
- Formas de cobro: **efectivo** (con "paga con", vuelto y billetes rápidos), **transferencia** y **fiado** (con el nombre de la persona).
- Después de cobrar: **guardar el ticket en PDF** (formato de 80 mm) o **imprimir** (abre el menú de impresoras del sistema).
- Atajos de teclado: `F2` buscar, `F3` producto sin código, `F12` cobrar, `Enter` confirmar, `Esc` cancelar.

### Productos y stock
- Alta con descripción, costo, **% de ganancia (1 a 100)** que calcula el precio de venta, y opción de **redondear precios hacia arriba a números enteros**.
- El código de barras es opcional: si se deja vacío, el sistema asigna un código interno válido.
- Descripciones siempre en **mayúsculas**.
- Edición directa en la tabla de costo, precio, stock y % de ganancia. Borrado con botón rojo y confirmación.
- **Alertas de stock:** las filas con 1 unidad o menos se marcan en rojo con la etiqueta *REPONER* o *SIN STOCK*, y después de una venta aparece un aviso emergente con un recuadro por cada producto (naranja: poco stock; rojo: agotado).

### Generador de códigos de barras
- Genera **EAN-13** (ISO/IEC 15420) con dígito verificador, a partir de un producto o de un número propio.
- Usa el prefijo `2` (circulación restringida de GS1), pensado para **uso interno del local**.
- Permite asignar el código al producto, **imprimir la etiqueta** o **guardarla en PDF** (60 × 40 mm).

### Caja, turnos y corte
- **Primer turno del día:** pide contar el dinero de la caja.
- **Cambio de turno / empleado:** no pide contar. Registra cuánto debería haber en efectivo y el siguiente turno arranca con ese monto.
- **Finalizar día:** pide contar el efectivo, muestra la diferencia y cierra el día.
- Al cerrar un turno se exporta un **PDF con el desglose** de ese turno.
- **Egresos y movimientos de dinero:** pago a proveedor (efectivo o transferencia), otro egreso y cambio de efectivo por transferencia (o al revés). No permite sacar más efectivo del que hay en caja.
- **Corte:** dinero al empezar, ventas en efectivo, cobros de fiados, movimientos, efectivo esperado, transferencias, fiado, total vendido, tickets y ganancia.
- **Fiados pendientes** por persona, con registro de cobros.
- **Ventas del turno:** lista con hora, detalle, forma de pago y monto; cada ticket se puede reimprimir o guardar en PDF.
- **Historial de turnos** (dueño): calendario por fecha, desglose y PDF de cada turno.

### Interfaz
- Menú lateral desplegable (☰): se abre al pasar el mouse en la computadora y con un toque en el celular.
- Diseño responsive con modo claro y oscuro automático.
- Pantalla de bienvenida con primeros pasos y textos de ayuda en cada sección.

---

## Requisitos

### Para usar la aplicación (usuario final)

| Requisito | Detalle |
|---|---|
| Sistema operativo | Windows 7 (SP1 con actualizaciones), 8, 10 u 11 con el instalador generado con Python 3.8 |
| Navegador | Edge, Chrome o Firefox instalado (en Windows 10/11 abre como ventana de aplicación) |
| Internet | Opcional. Se usa para guardar PDF (carga la librería jsPDF) y para la tipografía; sin internet esas dos cosas no funcionan |
| Hardware opcional | Lector de códigos de barras USB (funciona como teclado) e impresora |

### Para desarrollar o armar el instalador

| Programa | Versión | Uso |
|---|---|---|
| Python | **3.8.10** para compatibilidad con Windows 7/8/10/11, o una versión actual si solo se apunta a Windows 10/11 | Ejecutar el servidor y compilar |
| PyInstaller | La última compatible con la versión de Python (se instala sola con `pip`) | Generar el programa `stockito.exe` |
| Inno Setup | 6.x | Generar `STOCKITO-Instalador.exe` |
| Pillow (opcional) | Cualquiera | Solo para volver a generar el ícono `.ico` |

---

## Tecnologías y programas utilizados

**Interfaz**
- HTML, CSS y JavaScript sin frameworks, en un único archivo (`stockito.html`).
- [jsPDF](https://github.com/parallax/jsPDF) 2.5.1 (licencia MIT), cargada desde cdnjs, para los PDF de tickets, etiquetas y turnos.
- Google Fonts: *Schibsted Grotesk* (licencia OFL).
- Web Crypto API (SHA-256) y Web Audio API (aviso sonoro al escanear).

**Servidor y datos**
- Python (solo biblioteca estándar): `http.server`, `sqlite3`, `json`, `threading`, `argparse`, `urllib`.
- SQLite como base de datos local.

**Empaquetado y distribución**
- PyInstaller (modo `--onedir --windowed`) para crear el ejecutable.
- Inno Setup para crear el instalador, con acceso directo y menú Inicio.
- Pillow para generar el ícono multi-tamaño (16 a 256 px).

---

## Estructura del proyecto

```
stockito/
├── stockito.py                   # Servidor local en Python + base SQLite + copias de seguridad
├── stockito.html                 # Aplicación completa (interfaz y lógica)
├── stockito.ico                  # Ícono (16, 24, 32, 48, 64, 128 y 256 px)
├── LEEME.txt                     # Instrucciones breves en español
├── .gitignore                    # Evita subir archivos generados y datos reales
└── README.md
```

---

## Instalación y uso

### Opción A: con el instalador (recomendada para los locales)
1. Ejecutar `STOCKITO-Instalador.exe` y avanzar con "Siguiente".
2. Abrir **STOCKITO** desde el acceso directo del escritorio.
3. En el primer ingreso, cargar los datos del local y la contraseña del dueño.
4. Para cerrar el programa por completo: *Inicio → STOCKITO → Cerrar STOCKITO*.

### Opción B: desde el código fuente
```bash
python stockito.py              # arranca y abre la ventana en http://127.0.0.1:8765
python stockito.py --puerto 9000
python stockito.py --no-abrir   # no abre el navegador automáticamente
python stockito.py --cerrar     # cierra la instancia que está corriendo
```
`stockito.py` y `stockito.html` deben estar en la misma carpeta.

---

## Cómo generar el instalador de Windows

1. Instalar **Python 3.8.10** (marcando *Add Python to PATH*) e **Inno Setup 6**.
2. Ejecutar `1_construir_instalador.bat` (requiere internet la primera vez, para instalar PyInstaller).
3. El instalador queda en `salida\STOCKITO-Instalador.exe`.

Para publicar una mejora, se modifican los archivos y se vuelve a ejecutar el mismo `.bat`. Los datos de los locales no se pierden al actualizar.

---

## Arquitectura y datos

- `stockito.py` levanta un servidor HTTP **solo en `127.0.0.1`** y sirve `stockito.html`.
- Al servir la página, Python reemplaza las dos únicas líneas que guardaban datos en el navegador por llamadas al servidor. El archivo HTML no se modifica.
- Endpoints: `GET /` (página), `GET /api/state` (estado), `POST /api/state` (guardar) y `POST /api/apagar` (cerrar). Los pedidos `POST` con origen de otra página se rechazan.
- Todo el estado de la aplicación se guarda como un documento JSON en la tabla `kv` de SQLite.
- **Ubicación de los datos** en la versión instalada: `%LOCALAPPDATA%\STOCKITO\stockito.db`, con copias diarias en `copias_de_seguridad\` (se conservan las últimas 30). Desinstalar el programa no borra los datos.
- Al ejecutar desde el código fuente, los datos quedan junto a `stockito.py`.

---

## Limitaciones conocidas

- **Los tickets no son fiscales.** Dicen "Comprobante no fiscal – documento no válido como factura". Para operar legalmente se necesita factura electrónica con ARCA (CAE) o un controlador fiscal homologado. La emisión desde el sistema no está implementada.
- **La seguridad es básica.** Las contraseñas y los permisos se verifican en la interfaz, y el hash SHA-256 no usa sal. Por eso el servidor escucha solo en la propia computadora y **no debe exponerse a la red ni a internet**.
- Una sola caja por instalación: no hay sincronización entre varias computadoras ni acceso desde el celular.
- No hay registro de auditoría (quién cambió qué) ni anulación de ventas.
- Los PDF y la tipografía dependen de internet.
- El instalador no está firmado digitalmente, por lo que Windows puede mostrar "editor desconocido".
- Windows 7 y 8 ya no reciben actualizaciones de seguridad, y sus navegadores tampoco. Se recomienda Windows 10 u 11 para uso productivo.

---

## Hoja de ruta

- [ ] Mover el login, los roles y la lógica de ventas al servidor.
- [ ] Facturación electrónica con ARCA.
- [ ] Varias cajas y vista desde el celular del dueño, con servidor y conexión cifrada.
- [ ] Registro de auditoría y anulación de ventas con motivo.
- [ ] Exportación a Excel y copias de seguridad en la nube.
- [ ] Incluir jsPDF y la tipografía dentro del programa para funcionar sin internet.
- [ ] Firma digital del instalador.
- [ ] Integración con impresoras de tickets, lectores y cajón de dinero.

---

## Créditos y licencia

- Diseño, producto y pruebas: **NiloFleming**.
- Librerías de terceros: jsPDF (MIT), Schibsted Grotesk (OFL), PyInstaller e Inno Setup (según sus licencias).
- **Licencia:todos los derechos están reservados.

STOCKITO - instalador para Windows
==================================

QUE HAY EN ESTA CARPETA
  stockito.py / stockito.html / stockito.ico   el programa, la pantalla y el logo
 
LO QUE HACE EL DUENO DEL LOCAL (sin instalar nada mas)
  1. Doble clic en STOCKITO-Instalador.exe  ->  Siguiente, Siguiente, Instalar.
  2. Queda el icono de STOCKITO en el escritorio. Doble clic y se abre.
  3. Para cerrarlo del todo: Inicio > STOCKITO > "Cerrar STOCKITO".

DONDE QUEDAN LOS DATOS
  %LOCALAPPDATA%\STOCKITO\stockito.db            toda la informacion del local
  %LOCALAPPDATA%\STOCKITO\copias_de_seguridad\   una copia por dia (las ultimas 30)
  Desinstalar el programa NO borra los datos. Los datos son por usuario de Windows.

NOTAS
  * Windows puede mostrar "editor desconocido" al instalar: el instalador no esta firmado.
    Se evita con un certificado de firma de codigo (se paga por año).
  * El programa escucha solo en esa PC. No exponerlo a la red ni a internet.
  * Para los PDF y la tipografia hace falta internet.

