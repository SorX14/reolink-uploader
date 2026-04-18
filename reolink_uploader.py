#!/usr/bin/env python
import os
import requests
from base64 import b64encode
from pathlib import Path
from dotenv import load_dotenv
import json
import sys
import logging
from logging import Formatter

# Disable SSL warnings for self-signed certificates.
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Formatter with timestamp
formatter = Formatter("%(asctime)s - %(levelname)s - %(message)s")

# File handler
file_handler = logging.FileHandler(Path(__file__).parent / "reolink-uploader.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def main():
    load_dotenv()

    logger.info("Starting reolink uploader script")

    # Load the camera credentials
    config_path = Path(__file__).parent / ".camera_credentials.json"
    with open(config_path) as f:
        cameras = json.load(f)

    # Probably some fancy python way to get arguments but IDGAF
    if len(sys.argv) != 2:
        print("No camera name provided")
        sys.exit(1)

    camera_name = sys.argv[1]

    if camera_name not in cameras:
        logger.error(f"Error: {camera_name} not found in .camera_credentials.json")
        sys.exit(1)

    upload_certificate(cameras[camera_name])


# Source: https://gist.github.com/velzend/895c18d533b3992f3a0cc128f27c0894
def upload_certificate(camera: dict):
    base_url = camera.get("url")
    username = camera.get("username")
    password = camera.get("password")

    if not all([base_url, username, password]):
        logger.error("Camera config missing required fields")
        sys.exit(1)

    cert_dir = Path(__file__).parent.parent / "certs" / base_url
    cert_path = cert_dir / "cert.pem"
    key_path = cert_dir / "key.pem"

    if not cert_path.exists() or not key_path.exists():
        logger.error(f"Certificate files not found: {cert_path} or {key_path}")
        sys.exit(1)

    logger.info(f"Found cert {cert_path} and key {key_path}")

    login_req = [
        {
            "cmd": "Login",
            "param": {"User": {"userName": username, "password": password}},
        }
    ]

    resp = requests.post(
        f"https://{base_url}/cgi-bin/api.cgi?cmd=Login", json=login_req, verify=False
    )

    resp.raise_for_status()
    token = resp.json()[0]["value"]["Token"]["name"]

    logger.info(f"Retrieved token: {token}")

    cert_bytes = Path(cert_path).read_bytes()
    key_bytes = Path(key_path).read_bytes()

    cert_req = [
        {
            "cmd": "ImportCertificate",
            "action": 0,
            "param": {
                "importCertificate": {
                    "crt": {
                        "size": len(cert_bytes),
                        "name": "server.crt",
                        "content": b64encode(cert_bytes).decode("UTF-8"),
                    },
                    "key": {
                        "size": len(key_bytes),
                        "name": "server.key",
                        "content": b64encode(key_bytes).decode("UTF-8"),
                    },
                }
            },
        }
    ]

    resp = requests.post(
        f"https://{base_url}/cgi-bin/api.cgi?cmd=ImportCertificate&token={token}",
        json=cert_req,
        verify=False,
    )
    resp.raise_for_status()
    data = resp.json()
    if data[0]["value"]["rspCode"] != 200:
        logger.error(f"Unexpected response: {data}")
        raise SystemExit(f"Unexpected response: {data}")
    logger.info(f"Camera {base_url} certificate updated")


if __name__ == "__main__":
    main()
