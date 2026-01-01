from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.structlog_config import set_user_id

bearer_scheme = HTTPBearer()


async def get_user_id_from_jwt(
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> int:
    """
    Extract user_id from JWT token and inject into logging context.

    This dependency:
    1. Decodes the JWT token (without signature verification for dev)
    2. Extracts the 'sub' claim as user_id
    3. Sets user_id in structlog context for all subsequent logs
    4. Stores user_id in request.state for other middleware/handlers
    """
    try:
        # Decode without verification as per user's request
        # In a real application, you would verify the token with a secret key
        payload = jwt.decode(token.credentials, "", algorithms=["HS256"], options={"verify_signature": False})
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: sub claim missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = int(sub)

        # Inject user_id into structlog context for all subsequent logs
        set_user_id(str(user_id))

        # Also store in request.state for other handlers
        request.state.user_id = user_id

        return user_id
    except (JWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
