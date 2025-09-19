import random
from datetime import datetime , timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update
from fastapi import HTTPException
from app.models.user import User, ResetPassword
from app.models.course import Enrollment, Course
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from typing import Optional

class UserCRUD:

    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        res=await db.execute(select(User).where(User.email == email))
        return res.scalar_one_or_none()
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        res=await db.execute(select(User).where(User.username == username))
        return res.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        res=await db.execute(select(User).where(User.id == user_id))
        return res.scalar_one_or_none()

    async def create(self, db: AsyncSession, user_in: UserCreate) -> User:
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=hashed_password,
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            role=user_in.role
        )
        try:
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except IntegrityError:
            await db.rollback()
            raise ValueError("User with this email or username already exists")

    async def authenticate(self, db: AsyncSession, username: str, password: str) -> Optional[User]:
        user = await self.get_by_username(db, username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def update(self, db: AsyncSession, user_id: int, user_in: UserUpdate) -> Optional[User]:
        user = await self.get_by_id(db, user_id)
        if not user:
            return HTTPException(status_code=404, detail="User not found")
        
        update_data = user_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    async def get_my_course(self,db:AsyncSession,id:int):
        try:
            result = await db.execute(
            select(Course)
            .join(Enrollment)
            .where(Enrollment.student_id == id)
        )
            courses = result.scalars().all()
            if not courses:
                return {"message": "You do not have any courses yet"}
            return (f"Your courses:", courses)
        except Exception as e:
            raise e
        
    async def verify_reset_code(self, db: AsyncSession, reset_id: int, code: str) -> bool:
        """Verify OTP code for password reset"""
        try:
            res = await db.execute(
                select(ResetPassword).where(
                    ResetPassword.id == reset_id,
                    ResetPassword.code == int(code)
                )
            )
            reset_record = res.scalar_one_or_none()
            
            if not reset_record:
                raise HTTPException(status_code=400, detail='Invalid OTP code')
            
            # Check if code is expired (5 minutes)
            if datetime.now() > reset_record.created_at + timedelta(minutes=5):
                # Delete expired record
                await db.delete(reset_record)
                await db.commit()
                raise HTTPException(status_code=403, detail='OTP code has expired')
                
            return True
            
        except ValueError:
            raise HTTPException(status_code=400, detail='Invalid OTP code format')
        
    async def update_password_by_email(self, db: AsyncSession, email: str, new_password: str) -> bool:
        """Update user password by email"""
        hashed_password = get_password_hash(new_password)
        try:
            result = await db.execute(
                update(User)
                .where(User.email == email)
                .values(hashed_password=hashed_password)
            )
            await db.commit()
            
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
                
            return True
            
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update password: {str(e)}")
        
    async def create_reset_password_request(self, db: AsyncSession, email: str) -> tuple[int, str]:
        """Create password reset request and return reset_id and OTP code"""
        # Check if user exists
        user = await self.get_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User with this email not found")
        
        # Generate 4-digit OTP
        otp_code = random.randint(1000, 9999)
        
        # Delete any existing reset requests for this email
        existing_result = await db.execute(
            select(ResetPassword).where(ResetPassword.email == email)
        )
        existing_records = existing_result.scalars().all()
        for record in existing_records:
            await db.delete(record)
        await db.commit()
        
        # Create new reset request
        reset_request = ResetPassword(
            email=email,
            code=otp_code,
            created_at=datetime.now()
        )
        
        db.add(reset_request)
        await db.commit()
        await db.refresh(reset_request)
        
        return reset_request.id, str(otp_code)
    
    async def complete_password_reset(self, db: AsyncSession, reset_id: int, email: str) -> bool:
        """Complete password reset by deleting the reset record"""
        try:
            result = await db.execute(
                select(ResetPassword).where(
                    ResetPassword.id == reset_id,
                    ResetPassword.email == email
                )
            )
            reset_record = result.scalar_one_or_none()
            
            if reset_record:
                await db.delete(reset_record)
                await db.commit()
                
            return True
            
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to complete reset: {str(e)}")



        
     
        

user_crud = UserCRUD()