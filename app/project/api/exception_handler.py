# project/api/exception_handler.py

from django.db.models import ProtectedError
from django.db import IntegrityError
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
from itertools import islice
import logging

logger = logging.getLogger('ctrctsapp')

# === Opcional: mapea nombres de constraints a errores por campo ===
# Recomendado si defines UniqueConstraint(name="uq_party_name_ci") u otros.
UNIQUE_CONSTRAINT_MAP = {
    # "uq_party_name_ci": {"name": ["A party with this name already exists."]},
}

# === Heurísticas por campo si no hay constraint name fiable ===
# Busca fragmentos en el mensaje de la BD y devuelve errores por campo.
UNIQUE_FIELD_GUESSES = [
    (" name ", {"name": ["A party with this name already exists."]}),
    ("'name'", {"name": ["A party with this name already exists."]}),
    ('"name"', {"name": ["A party with this name already exists."]}),
    (" email ", {"email": ["A party with this email already exists."]}),
    ("'email'", {"email": ["A party with this email already exists."]}),
    ('"email"', {"email": ["A party with this email already exists."]}),
]

def _payload_unique_from_message(msg_lower: str):
    # 1) Por nombre de constraint explícito (más robusto entre motores)
    for constraint, payload in UNIQUE_CONSTRAINT_MAP.items():
        if constraint.lower() in msg_lower:
            return payload

    # 2) Heurística por campo (portátil y rápida)
    for needle, payload in UNIQUE_FIELD_GUESSES:
        if needle in msg_lower:
            return payload

    # 3) Fallback genérico si no se pudo inferir campo
    return {"detail": "Unique constraint violated."}

def custom_exception_handler(exc, context):
    """
    Handler global:
      - ProtectedError → 409 (in use) con ejemplos
      - IntegrityError (FK/constraint) → 409 (in use)
      - IntegrityError (UNIQUE) → 400 con errores por campo (para formularios)
      - Delega el resto al handler por defecto de DRF
    """
    # --- ProtectedError: típico en DELETE con on_delete=PROTECT ---
    if isinstance(exc, ProtectedError):
        protected = getattr(exc, "protected_objects", None)

        examples = None
        if protected:
            try:
                examples = [str(o) for o in islice(protected, 3)]
            except TypeError:
                examples = [str(o) for o in list(protected)[:3]]

        payload = {
            "detail": "This record is in use and cannot be deleted. Inactivate it instead.",
            "code": "in_use",
        }
        if examples:
            payload["examples"] = examples
        logger.info("ProtectedError handled as 409 Conflict")
        return Response(payload, status=status.HTTP_409_CONFLICT)

    # --- IntegrityError: FK/constraint o UNIQUE ---
    if isinstance(exc, IntegrityError):
        msg = (str(exc) or "")
        msg_lower = msg.lower()

        # a) FK / constraint de "in use" (no es UNIQUE) → 409
        if ("foreign key" in msg_lower) or ("constraint" in msg_lower and "unique" not in msg_lower):
            logger.info("IntegrityError(FK/constraint) handled as 409 Conflict: %s", msg)
            return Response(
                {
                    "detail": "This record is in use and cannot be deleted. Inactivate it instead.",
                    "code": "in_use",
                },
                status=status.HTTP_409_CONFLICT,
            )

        # b) UNIQUE → 400 con errores por campo
        if "unique" in msg_lower or "duplicate entry" in msg_lower:
            # MySQL suele traer "Duplicate entry '... for key '...'"
            payload = _payload_unique_from_message(msg_lower)
            logger.info("IntegrityError(UNIQUE) handled as 400 Bad Request: %s", msg)
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        # c) Fallback: si no calza en nada anterior, delega
        logger.warning("IntegrityError not matched, delegating to DRF default: %s", msg)
        return drf_exception_handler(exc, context)

    # --- Otros casos: delega al handler por defecto ---
    return drf_exception_handler(exc, context)
