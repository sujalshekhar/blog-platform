from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user account.

    Creates a new user with the specified email, password, and personal details.
    The email must be unique across the platform.
    """
    return AuthService(db).register_user(request)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate user and generate JWT token.

    Validates the provided email and password. On success, returns an OAuth2 
    compatible Bearer token that must be included in the Authorization header 
    for subsequent authenticated requests.
    """
    request = LoginRequest(email=form_data.username, password=form_data.password)
    return AuthService(db).login_user(request)