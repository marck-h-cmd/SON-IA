"""
Utilidades de seguridad
"""

import hashlib
import secrets
from typing import Optional


def hash_sensitive_data(data: str) -> str:
    """Hashea datos sensibles (SHA-256)"""
    return hashlib.sha256(data.encode()).hexdigest()


def generate_token(length: int = 32) -> str:
    """Genera un token seguro aleatorio"""
    return secrets.token_hex(length)


def mask_document_number(doc_number: str) -> str:
    """
    Enmascara número de documento para logs.
    Ej: 12345678 -> 1234****
    """
    if len(doc_number) <= 4:
        return "****"
    return doc_number[:4] + "*" * (len(doc_number) - 4)


def sanitize_input(text: str) -> str:
    """Sanitiza input de usuario"""
    # Remover caracteres peligrosos
    dangerous_chars = ["<", ">", "\"", "'", ";", "--"]
    sanitized = text
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")
    return sanitized.strip()