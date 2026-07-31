from app.core.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.enums.role import UserRole


from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse,
)


class AuthService:
    """
    Service layer for authentication and user management.
    
    Handles business logic for user registration, password hashing,
    and JWT token generation.
    """

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(self.db)

    def register_user(self, request: RegisterRequest) -> UserResponse:
        """
        Registers a new user in the platform.

        Args:
            request (RegisterRequest): The user registration details including email and password.

        Returns:
            UserResponse: The newly created user object (excluding sensitive data).

        Raises:
            HTTPException (400): If the provided email is already registered.
        """
        user = self.user_repo.get_by_email(request.email)
        if user:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        hashed_password = hash_password(request.password)

        user_data = User(
            email=request.email,
            password_hash=hashed_password,
            first_name=request.first_name,
            last_name=request.last_name
        )

        new_user = self.user_repo.create(user_data)
        return UserResponse.model_validate(new_user)

    def login_user(self, request: LoginRequest) -> TokenResponse:
        """
        Authenticates a user and generates a JWT access token.

        Args:
            request (LoginRequest): The user's login credentials.

        Returns:
            TokenResponse: A response containing the JWT access token and token type.

        Raises:
            HTTPException (401): If the email is not found or the password does not match.
        """
        user = self.user_repo.get_by_email(request.email)
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        access_token = create_access_token(
            data={
                "sub": str(user.id), 
                "role": user.role.value if hasattr(user, 'role') and user.role else UserRole.USER.value,
                "first_name": user.first_name,
                "last_name": user.last_name or ""
            }
        )
        
        return TokenResponse(access_token=access_token, token_type="bearer")