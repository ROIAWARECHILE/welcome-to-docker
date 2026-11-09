# Pase de Google Wallet de prueba: itinerario Santiago → Rio

Pase **genérico** de Google Wallet (tarjeta de itinerario) con los datos del viaje
del 10 al 14 de marzo de 2027. Se emite desde **tu propia cuenta** de emisor y
con una marca ficticia ("Demo Itinerario"). No es una tarjeta de embarque ni
imita a la aerolínea, la agencia, el hotel ni la rentadora.

## Archivos

| Archivo | Qué es |
|---|---|
| `trip.json` | Datos del viaje (vuelos, hotel, auto, viajeros, total). Edítalo si cambia algo. |
| `make_pass.py` | Construye la clase y el objeto del pase y firma el enlace "Agregar a Google Wallet". |
| `wallet_class.json` | Clase generada (plantilla de la tarjeta). |
| `wallet_object.json` | Objeto generado (el pase con los datos). |
| `preview.html` | Vista previa aproximada de cómo se ve la tarjeta en el teléfono. |
| `email_itinerario.html` | Correo de itinerario (marca ficticia) con botón "Agregar a Google Wallet". |
| `send_email.py` | Envía ese correo desde tu propia cuenta por SMTP, insertando el enlace del pase. |

## Requisitos (una sola vez)

1. Entra a [Google Pay & Wallet Console](https://pay.google.com/business/console) y crea una cuenta de emisor. Copia el **Issuer ID** (número largo).
2. En Google Cloud crea una **cuenta de servicio**, descarga su clave JSON y habilita la API "Google Wallet API".
3. En la consola de Wallet, en *Usuarios*, agrega el correo de la cuenta de servicio con rol *Desarrollador*.
4. Una cuenta recién creada está en **modo demo**: Google antepone "[TEST ONLY]" a todos sus pases y solo los pueden agregar los correos registrados como *tester*. Esa etiqueta la pone Google, no el pase, así que no se puede quitar desde el JSON ni desde el script.
5. Para que el pase salga **sin "[TEST ONLY]"** hay que pedir acceso de producción: en la consola, en *Google Wallet API* → *Publishing access*, completa el formulario (nombre de la empresa, sitio, caso de uso y capturas del pase) y espera la aprobación de Google. Una vez aprobada la cuenta, vuelve a ejecutar el script y el enlace genera el pase limpio.

## Generar el pase

```bash
pip install cryptography
python3 make_pass.py --issuer-id TU_ISSUER_ID --service-account /ruta/clave.json
```

El script imprime un enlace `https://pay.google.com/gp/v/save/...` y lo guarda en
`add_to_wallet_link.txt` (ignorado por git). Ábrelo en el teléfono con la sesión de
Google de prueba y toca **Agregar a Google Wallet**. La clase y el objeto van
incrustados en el JWT, así que no hace falta crearlos antes por la API REST.

Si lo ejecutas sin `--service-account`, solo regenera los dos JSON para revisarlos.

## Qué lleva la tarjeta

- Título: Demo Itinerario (prueba). Cabecera: Santiago de Chile → Rio de Janeiro, 10 al 14 mar. 2027.
- Ida y vuelta con horarios SCL 04:46 → GIG 09:00 y GIG 10:45 → SCL 15:33 (JetSMART, directo).
- Hotel Royal Rio Palace, Copacabana, check in/out, 4 noches, 2 adultos, política de cancelación.
- Auto chico Foco, retiro y devolución en Rua Luís Belart 70, conductor, políticas.
- Viajeros, equipaje incluido y total.
- QR con el texto `DEMO-ITINERARIO|...` y leyenda "Pase de prueba, no es un documento de viaje".

No incluye RUT ni fechas de nacimiento: un pase no los necesita y evita exponerlos.

## Enviarlo por correo

`email_itinerario.html` es un correo de itinerario con tarjetas de vuelo, hotel y auto y un botón
que apunta al enlace del pase (marcador `WALLET_LINK`). Para enviarlo desde tu Gmail:

1. En la seguridad de tu cuenta de Google crea una **contraseña de aplicación**.
2. Ejecuta:

```bash
SMTP_USER=tucuenta@gmail.com SMTP_PASS='contraseña de aplicación' \
python3 send_email.py --to trayenkooliva@gmail.com --wallet-link "$(cat add_to_wallet_link.txt)"
```

El remitente es tu propia cuenta con el nombre "Demo Itinerario". Si prefieres publicarlo en
Vercel o GitHub Pages, sube el HTML tal cual y reemplaza `WALLET_LINK` a mano.
