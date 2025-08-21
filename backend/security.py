import re
import bleach
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel, validator, EmailStr
import logging

logger = logging.getLogger(__name__)


class SecurityUtils:
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitiza strings removiendo caracteres peligrosos"""
        if not value:
            return ""

        # Remover caracteres peligrosos
        value = bleach.clean(value, strip=True)

        # Limitar longitud
        if len(value) > max_length:
            value = value[:max_length]

        # Remover patrones de SQL injection básicos
        dangerous_patterns = [
            r'(\bDROP\b|\bDELETE\b|\bUPDATE\b|\bINSERT\b|\bSELECT\b|\bUNION\b)',
            r'(--|\/\*|\*\/)',
            r'(\bEXEC\b|\bEXECUTE\b)',
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Contenido potencialmente peligroso detectado: {pattern}")
                raise HTTPException(
                    status_code=400,
                    detail="Contenido no válido detectado"
                )

        return value.strip()

    @staticmethod
    def validate_email_domain(email: str) -> bool:
        """Valida que el email tenga un dominio válido"""
        blocked_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
        domain = email.split('@')[1].lower() if '@' in email else ''
        return domain not in blocked_domains


# Middleware de rate limiting básico (en producción usar Redis)
class RateLimiter:
    def __init__(self):
        self.requests = {}

    def is_allowed(self, client_ip: str, max_requests: int = 100, window_seconds: int = 3600):
        """Rate limiting básico por IP"""
        import time
        current_time = time.time()

        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Limpiar requests antiguos
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < window_seconds
        ]

        # Verificar límite
        if len(self.requests[client_ip]) >= max_requests:
            return False

        # Registrar nueva request
        self.requests[client_ip].append(current_time)
        return True


rate_limiter = RateLimiter()


# Validadores de seguridad para schemas
class SecureContactoCreate(BaseModel):
    nombre: str
    correo: EmailStr
    mensaje: str

    @validator('nombre')
    def validate_nombre(cls, v):
        cleaned = SecurityUtils.sanitize_string(v, max_length=100)
        if len(cleaned) < 2:
            raise ValueError('Nombre debe tener al menos 2 caracteres')
        return cleaned

    @validator('correo')
    def validate_correo(cls, v):
        if not SecurityUtils.validate_email_domain(v):
            raise ValueError('Dominio de email no permitido')
        return v

    @validator('mensaje')
    def validate_mensaje(cls, v):
        cleaned = SecurityUtils.sanitize_string(v, max_length=2000)
        if len(cleaned) < 10:
            raise ValueError('Mensaje debe tener al menos 10 caracteres')
        return cleaned


class SecureProgramaCreate(BaseModel):
    nombre: str
    descripcion: str

    @validator('nombre')
    def validate_nombre(cls, v):
        cleaned = SecurityUtils.sanitize_string(v, max_length=100)
        if len(cleaned) < 3:
            raise ValueError('Nombre de programa debe tener al menos 3 caracteres')
        return cleaned

    @validator('descripcion')
    def validate_descripcion(cls, v):
        cleaned = SecurityUtils.sanitize_string(v, max_length=5000)
        if len(cleaned) < 20:
            raise ValueError('Descripción debe tener al menos 20 caracteres')
        return cleaned


# Middleware de seguridad
async def security_middleware(request: Request, call_next):
    """Middleware para aplicar medidas de seguridad"""
    client_ip = request.client.host

    # Rate limiting
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Demasiadas requests. Intenta más tarde."
        )

    # Headers de seguridad
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response