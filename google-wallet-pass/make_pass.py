#!/usr/bin/env python3
"""
Genera un pase genérico de Google Wallet (tarjeta de itinerario) a partir de
trip.json y firma el enlace "Agregar a Google Wallet" con tu cuenta de servicio.

Uso:
  python3 make_pass.py --issuer-id 3388000000012345678 \
      --service-account /ruta/clave-cuenta-servicio.json

Sin --service-account solo escribe wallet_class.json y wallet_object.json
para revisarlos. Con la clave, además imprime el enlace para abrir en el
teléfono y lo guarda en add_to_wallet_link.txt.

Dependencia: cryptography  (pip install cryptography)
"""
import argparse
import base64
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def row(label: str, value: str) -> dict:
    return {"id": label.lower().replace(" ", "_"), "header": label, "body": value}


def build(trip: dict, issuer_id: str, class_suffix: str, object_suffix: str):
    class_id = f"{issuer_id}.{class_suffix}"
    object_id = f"{issuer_id}.{object_suffix}"

    ida, vuelta = trip["vuelo_ida"], trip["vuelo_vuelta"]
    hotel, auto = trip["hotel"], trip["auto"]

    wallet_class = {
        "id": class_id,
        "classTemplateInfo": {
            "cardTemplateOverride": {
                "cardRowTemplateInfos": [
                    {"twoItems": {
                        "startItem": {"firstValue": {"fields": [{"fieldPath": "object.textModulesData['ida']"}]}},
                        "endItem": {"firstValue": {"fields": [{"fieldPath": "object.textModulesData['vuelta']"}]}},
                    }},
                    {"twoItems": {
                        "startItem": {"firstValue": {"fields": [{"fieldPath": "object.textModulesData['hotel']"}]}},
                        "endItem": {"firstValue": {"fields": [{"fieldPath": "object.textModulesData['auto']"}]}},
                    }},
                ]
            }
        },
    }

    text_modules = [
        row("Ida", f"{ida['fecha']} · {ida['aerolinea']} · {ida['origen']} {ida['salida']} → {ida['destino']} {ida['llegada']} ({ida['tipo']}, {ida['duracion']})"),
        row("Vuelta", f"{vuelta['fecha']} · {vuelta['aerolinea']} · {vuelta['origen']} {vuelta['salida']} → {vuelta['destino']} {vuelta['llegada']} ({vuelta['tipo']}, {vuelta['duracion']})"),
        row("Hotel", f"{hotel['nombre']} ({hotel['estrellas']}★) · {hotel['direccion']} · Check in {hotel['checkin']} · Check out {hotel['checkout']} · {hotel['noches']} noches, {hotel['adultos']} adultos"),
        row("Auto", f"{auto['categoria']} · {auto['modelo']} · {auto['proveedor']} · Retiro {auto['retiro']} · Devolución {auto['devolucion']} · {auto['oficina']}"),
        row("Viajeros", ", ".join(trip["viajeros"])),
        row("Conductor", auto["conductor"]),
        row("Equipaje", trip["equipaje"]),
        row("Politicas", f"Hotel: {hotel['cancelacion']}. Auto: cambios {auto['cambios'].lower()}, cancelación {auto['cancelacion'].lower()}."),
        row("Total", trip["total"]),
    ]
    # Los ids deben ser únicos y sin acentos para poder referenciarlos en la plantilla.
    for m in text_modules:
        m["id"] = m["id"].replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

    wallet_object = {
        "id": object_id,
        "classId": class_id,
        "state": "ACTIVE",
        "genericType": "GENERIC_TYPE_UNSPECIFIED",
        "hexBackgroundColor": "#0b5d3b",
        "cardTitle": {"defaultValue": {"language": "es", "value": trip["issuer_name"]}},
        "header": {"defaultValue": {"language": "es", "value": f"{trip['origen']} → {trip['destino']}"}},
        "subheader": {"defaultValue": {"language": "es", "value": f"{ida['fecha']} – {vuelta['fecha']}"}},
        "textModulesData": text_modules,
        "barcode": {
            "type": "QR_CODE",
            "value": f"DEMO-ITINERARIO|{trip['contacto']}|{ida['origen']}-{ida['destino']}|{ida['fecha']}",
            "alternateText": "Pase de prueba, no es un documento de viaje",
        },
        "validTimeInterval": {
            "start": {"date": "2027-03-01T00:00:00Z"},
            "end": {"date": "2027-03-15T23:59:59Z"},
        },
    }
    return wallet_class, wallet_object


def sign_jwt(payload: dict, sa: dict) -> str:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding

    key = serialization.load_pem_private_key(sa["private_key"].encode(), password=None)
    header = {"alg": "RS256", "typ": "JWT", "kid": sa.get("private_key_id")}
    claims = {
        "iss": sa["client_email"],
        "aud": "google",
        "typ": "savetowallet",
        "iat": int(time.time()),
        "origins": [],
        "payload": payload,
    }
    signing_input = b".".join(
        b64url(json.dumps(p, separators=(",", ":"), ensure_ascii=False).encode()).encode()
        for p in (header, claims)
    )
    sig = key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    return (signing_input + b"." + b64url(sig).encode()).decode()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--issuer-id", default="ISSUER_ID", help="Issuer ID de Google Pay & Wallet Console")
    ap.add_argument("--service-account", help="Ruta al JSON de la cuenta de servicio")
    ap.add_argument("--trip", default=str(HERE / "trip.json"))
    ap.add_argument("--class-suffix", default="itinerario_demo_v1")
    ap.add_argument("--object-suffix", default="itinerario_rio_mar2027")
    args = ap.parse_args()

    trip = json.loads(Path(args.trip).read_text(encoding="utf-8"))
    wallet_class, wallet_object = build(trip, args.issuer_id, args.class_suffix, args.object_suffix)

    (HERE / "wallet_class.json").write_text(json.dumps(wallet_class, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (HERE / "wallet_object.json").write_text(json.dumps(wallet_object, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Escritos wallet_class.json y wallet_object.json")

    if not args.service_account:
        print("Sin --service-account: no se firmó el enlace. Agrega la clave para generarlo.")
        return 0
    if args.issuer_id == "ISSUER_ID":
        print("Falta --issuer-id (lo obtienes en Google Pay & Wallet Console).", file=sys.stderr)
        return 2

    sa = json.loads(Path(args.service_account).read_text(encoding="utf-8"))
    token = sign_jwt({"genericClasses": [wallet_class], "genericObjects": [wallet_object]}, sa)
    link = f"https://pay.google.com/gp/v/save/{token}"
    (HERE / "add_to_wallet_link.txt").write_text(link + "\n", encoding="utf-8")
    print("\nAbre este enlace en el teléfono con Google Wallet:\n")
    print(link)
    return 0


if __name__ == "__main__":
    sys.exit(main())
