import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.crud.user import user_crud
from app.schemas.user import Token, UserCreate, UserInDB, PasswordResetRequest, PasswordResetVerify


logger= logging.getLogger(__name__)
router = APIRouter()

@router.post("/register")
async def register(user_in: UserCreate=Depends(), db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    try:
        user = await user_crud.create(db, user_in=user_in)
        logger.info(f"User registered: {user.email}")
        return user
    except ValueError as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Login and get access token"""
    user = await user_crud.authenticate(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/reset-password", response_model=dict)
async def request_password_reset(
    request: PasswordResetRequest = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Request password reset - sends OTP to email"""
    try:
        # Create reset request and get OTP
        reset_id, otp_code = await user_crud.create_reset_password_request(db, request.email)
        
        # Send OTP via email
        from app.core.email import email_service
        email_sent = await email_service.send_otp_email(request.email, otp_code, expires_minutes=5)
        
        if not email_sent:
            logger.warning(f"Failed to send OTP email to {request.email}")
            # Note: We still return success for security reasons
        
        logger.info(f"Password reset requested for email: {request.email}")
        return {
            "message": "If the email exists, an OTP code has been sent",
            "reset_id": reset_id
        }
        
    except HTTPException:
        # For security, we don't reveal if email exists or not
        logger.warning(f"Password reset attempt for non-existent email: {request.email}")
        return {
            "message": "If the email exists, an OTP code has been sent",
            "reset_id": 0  # Dummy ID for non-existent emails
        }
    except Exception as e:
        logger.error(f"Password reset request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request"
        )

@router.post("/reset-password/verify")
async def verify_password_reset(
    verify_data: PasswordResetVerify = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Verify OTP and reset password"""
    try:
        # First verify the OTP code
        await user_crud.verify_reset_code(db, verify_data.reset_id, verify_data.otp_code)
        
        # Get the reset request to find the email
        from app.models.user import ResetPassword
        from sqlalchemy import select
        
        result = await db.execute(
            select(ResetPassword).where(ResetPassword.id == verify_data.reset_id)
        )
        reset_record = result.scalar_one_or_none()
        
        if not reset_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset request"
            )
        
        # Update the password
        await user_crud.update_password_by_email(
            db, 
            reset_record.email, 
            verify_data.new_password
        )
        
        # Clean up the reset request
        await user_crud.complete_password_reset(db, verify_data.reset_id, reset_record.email)
        
        logger.info(f"Password successfully reset for email: {reset_record.email}")
        return {"message": "Password has been successfully reset"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )
