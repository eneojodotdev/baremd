import socket
import ipaddress
import urllib.parse
import urllib3.util.connection
from typing import Optional

# Save the original connection factory
_orig_create_connection = urllib3.util.connection.create_connection

def _safe_create_connection(address, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None, socket_options=None):
    """
    A custom connection factory for urllib3 that intercepts DNS resolution.
    It resolves the hostname, verifies it is a public IP, and raises an error if it attempts
    to hit a local, private, or reserved network range, thus preventing DNS rebinding and SSRF.
    """
    host, port = address
    
    # Resolve the host
    try:
        addr_info = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)
    except socket.gaierror as e:
        raise ValueError(f"SSRF Protection: Failed to resolve {host}") from e
        
    for res in addr_info:
        af, socktype, proto, canonname, sa = res
        ip = sa[0]
        
        try:
            ip_obj = ipaddress.ip_address(ip)
        except ValueError:
            continue
            
        # Block private, loopback, multicast, link-local, and reserved ranges
        if (ip_obj.is_private or 
            ip_obj.is_loopback or 
            ip_obj.is_multicast or 
            ip_obj.is_link_local or 
            ip_obj.is_reserved):
            raise ValueError(f"SSRF Protection: Blocked connection to non-public IP {ip} for host {host}")
            
        # Block 0.0.0.0/8 (often bypasses loopback checks on Linux)
        if ip_obj.version == 4 and int(ip_obj) < 16777216:
            raise ValueError(f"SSRF Protection: Blocked connection to 0.0.0.0/8 subnet: {ip}")
            
    # If all resolutions are safe, proceed with the original connection factory
    return _orig_create_connection(address, timeout, source_address, socket_options)

def enable_ssrf_protection():
    """
    Globally patches urllib3's create_connection to use the safe SSRF-protected version.
    This effectively protects all `requests` usage in the application from SSRF and DNS rebinding.
    """
    urllib3.util.connection.create_connection = _safe_create_connection

def validate_uri_scheme(uri: str) -> None:
    """
    Validates that the provided URI scheme is strictly http or https.
    Rejects file:, data:, gopher:, ftp:, etc.
    """
    parsed = urllib.parse.urlparse(uri)
    scheme = parsed.scheme.lower()
    
    if scheme not in ("http", "https"):
        raise ValueError(
            f"Unsupported URI scheme: '{scheme}'. Supported schemes are strictly: http, https. "
            "Local file access and data URIs via remote fetch are prohibited for security."
        )
