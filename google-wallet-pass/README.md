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

## Requisitos (una sola vez)

1. Entra a [Google Pay & Wallet Console](https://pay.google.com/business/console) y crea una cuenta de emisor. Copia el **Issuer ID** (número largo).
2. En Google Cloud crea una **cuenta de servicio**, descarga su clave JSON y habilita la API "Google Wallet API".
3. En la consola de Wallet, en *Usuarios*, agrega el correo de la cuenta de servicio con rol *Desarrollador*.
4. Mientras la cuenta esté en modo demo, Google antepone "[TEST ONLY]" al pase. Para probar en tu teléfono agrega tu Gmail como *tester* en la misma consola.

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

El enlace es largo pero cabe en un correo. Puedes pegarlo en un mensaje desde tu propia
cuenta o servir `preview.html` con un botón que apunte al enlace (Vercel, GitHub Pages, lo que prefieras).
