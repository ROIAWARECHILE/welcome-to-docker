#!/usr/bin/env python3
"""
Envía email_itinerario.html desde TU cuenta de Gmail (u otro SMTP) a la
dirección indicada, reemplazando WALLET_LINK por el enlace del pase.

Uso:
  SMTP_USER=tucuenta@gmail.com SMTP_PASS='contraseña de aplicación' \
  python3 send_email.py --to trayenkooliva@gmail.com --wallet-link "$(cat add_to_wallet_link.txt)"

Para Gmail crea una "contraseña de aplicación" en la seguridad de tu cuenta;
la contraseña normal no funciona. El remitente es tu propia cuenta.
"""
import argparse
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--to", required=True)
    ap.add_argument("--wallet-link", default="#", help="Enlace que imprime make_pass.py")
    ap.add_argument("--subject", default="Tu itinerario: Santiago de Chile a Rio de Janeiro")
    ap.add_argument("--from-name", default="Demo Itinerario")
    ap.add_argument("--smtp-host", default=os.environ.get("SMTP_HOST", "smtp.gmail.com"))
    ap.add_argument("--smtp-port", type=int, default=int(os.environ.get("SMTP_PORT", "587")))
    args = ap.parse_args()

    user, password = os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS")
    if not user or not password:
        print("Define SMTP_USER y SMTP_PASS en el entorno.", file=sys.stderr)
        return 2

    html = (HERE / "email_itinerario.html").read_text(encoding="utf-8").replace("WALLET_LINK", args.wallet_link)

    msg = EmailMessage()
    msg["Subject"] = args.subject
    msg["From"] = f"{args.from_name} <{user}>"
    msg["To"] = args.to
    msg.set_content("Tu itinerario a Rio de Janeiro, del 10 al 14 de marzo de 2027. Abre este correo en un cliente con HTML.")
    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP(args.smtp_host, args.smtp_port) as s:
        s.starttls()
        s.login(user, password)
        s.send_message(msg)
    print(f"Enviado a {args.to} desde {user}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
