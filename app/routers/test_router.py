from typing import Any

import pytest
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.auth.dependencies import bearer_scheme

router = APIRouter()


@router.get("/jwt", summary="Return JWT payload from bearer token", tags=["test"])
async def read_jwt_payload(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict[str, Any]:
    """Read JWT payload from the provided Bearer token. This endpoint follows the project's dev
    behavior and does not verify the signature; it simply decodes and returns the payload.
    """
    try:
        payload = jwt.decode(token.credentials, "", options={"verify_signature": False})
        return {"payload": payload}
    except (JWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not decode JWT: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.get("/error/500", summary="Test 500 error handling", tags=["test"])
@pytest.mark.skip(reason="These are demo endpoints, not actual tests")
@pytest.mark.asyncio
async def test_500_error():
    """Test endpoint to trigger a 500 internal server error for testing error handlers."""
    # This will trigger an unhandled exception
    raise Exception("This is a test 500 error")


@router.get("/error/http", summary="Test HTTPException handling", tags=["test"])
@pytest.mark.skip(reason="These are demo endpoints, not actual tests")
@pytest.mark.asyncio
async def test_http_error():
    """Test endpoint to trigger an HTTPException."""
    raise HTTPException(status_code=400, detail="This is a test HTTP error")


@router.get("/error/zero-division", summary="Test zero division error", tags=["test"])
@pytest.mark.skip(reason="These are demo endpoints, not actual tests")
@pytest.mark.asyncio
async def test_zero_division_error():
    """Test endpoint to trigger a zero division error."""
    # This will trigger a ZeroDivisionError
    result = 1 / 0
    return {"result": result}
