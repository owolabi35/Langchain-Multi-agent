import os
import certifi


def configure_ssl_certificates() -> str:
    """Ensure requests and SSL use a valid certificate bundle on this machine."""
    ca_bundle = certifi.where()
    os.environ["SSL_CERT_FILE"] = ca_bundle
    os.environ["REQUESTS_CA_BUNDLE"] = ca_bundle
    os.environ["CURL_CA_BUNDLE"] = ca_bundle
    return ca_bundle
