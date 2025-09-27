from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

bearer_scheme = HTTPBearer()


async def get_user_id_from_jwt(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> int:
    try:
        # Decode without verification as per user's request
        # In a real application, you would verify the token with a secret key
        payload = jwt.decode(token.credentials, "", options={"verify_signature": False})
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: sub claim missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = int(sub)
        return user_id
    except (JWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
