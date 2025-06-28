from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum

class UserRole(str, Enum):
    MENTOR = "mentor"
    MENTEE = "mentee"

class MatchRequestStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

# Auth models
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: UserRole

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    token: str

# Profile models
class ProfileResponse(BaseModel):
    name: str
    bio: str
    imageUrl: str
    skills: Optional[List[str]] = None

class UserResponse(BaseModel):
    id: int
    email: str
    role: UserRole
    profile: ProfileResponse

class UpdateProfileRequest(BaseModel):
    id: int
    name: str
    role: UserRole
    bio: str
    image: Optional[str] = None
    skills: Optional[List[str]] = None

# Match request models
class MatchRequestCreate(BaseModel):
    mentorId: int
    menteeId: int
    message: str

class MatchRequestResponse(BaseModel):
    id: int
    mentorId: int
    menteeId: int
    message: str
    status: MatchRequestStatus

class MatchRequestOutgoing(BaseModel):
    id: int
    mentorId: int
    menteeId: int
    status: MatchRequestStatus
