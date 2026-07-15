import os
import unittest
import certifi


class SSLConfigurationTests(unittest.TestCase):
    def test_configure_ssl_certificates_sets_certifi_bundle(self):
        from src.tools.ssl_utils import configure_ssl_certificates

        os.environ.pop("SSL_CERT_FILE", None)
        os.environ.pop("REQUESTS_CA_BUNDLE", None)
        os.environ.pop("CURL_CA_BUNDLE", None)

        configure_ssl_certificates()

        self.assertEqual(os.environ["SSL_CERT_FILE"], certifi.where())
        self.assertEqual(os.environ["REQUESTS_CA_BUNDLE"], certifi.where())
        self.assertEqual(os.environ["CURL_CA_BUNDLE"], certifi.where())


if __name__ == "__main__":
    unittest.main()
