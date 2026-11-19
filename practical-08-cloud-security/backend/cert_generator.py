import datetime
import ipaddress
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_tls_pki():
    """
    Generates a 2048-bit RSA key and self-signed X.509 TLS certificate with SAN.
    Strictly enterprise/generic naming with zero university/college names.
    """
    # 1. Generate Private Key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 2. Build Certificate Subject & Issuer
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Cloud Infrastructure Security Services"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Platform Security Engineering"),
        x509.NameAttribute(NameOID.COMMON_NAME, "cloud-service.internal"),
    ])

    san = x509.SubjectAlternativeName([
        x509.DNSName("cloud-service.internal"),
        x509.DNSName("api.cloud-defense.internal"),
        x509.DNSName("vault.cloud-defense.internal"),
        x509.DNSName("localhost"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
    ])

    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=365))
        .add_extension(san, critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(private_key, hashes.SHA256())
    )

    # Export PEM representations
    cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    fingerprint = cert.fingerprint(hashes.SHA256()).hex(":").upper()

    metadata = {
        "common_name": "cloud-service.internal",
        "organization": "Cloud Infrastructure Security Services",
        "organizational_unit": "Platform Security Engineering",
        "country": "US",
        "state": "California",
        "key_algorithm": "RSA 2048-bit",
        "signature_algorithm": "SHA256withRSA",
        "serial_number": hex(cert.serial_number)[2:].upper(),
        "valid_from": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "valid_until": (now + datetime.timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "sha256_fingerprint": fingerprint,
        "san_domains": [
            "cloud-service.internal",
            "api.cloud-defense.internal",
            "vault.cloud-defense.internal",
            "localhost",
            "127.0.0.1"
        ],
        "certificate_pem": cert_pem,
        "private_key_pem": priv_pem
    }

    return metadata
