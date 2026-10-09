import truststore

# Trust the OS certificate store so corporate TLS-interception CAs are accepted.
truststore.inject_into_ssl()

__version__ = "0.1.0"
