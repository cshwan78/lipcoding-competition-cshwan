from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, RedirectResponse
from typing import List, Optional
import base64
import uuid
import io
import json
import json
from models import (
    UserRole, MatchRequestStatus, SignupRequest, LoginRequest, LoginResponse,
    ProfileResponse, UserResponse, MatchRequestCreate, MatchRequestResponse,
    MatchRequestOutgoing, UpdateProfileRequest
)
from auth import *

app = FastAPI(
    title="Mentor-Mentee Matching API",
    description="API for matching mentors and mentees in a mentoring platform",
    version="1.0.0",
    docs_url="/swagger-ui",  # 요구사항에 맞게 변경
    openapi_url="/openapi.json"  # 요구사항에 맞게 명시
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트엔드 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# 메모리 저장소
users_db = {}  # {id: user_data}
profiles_db = {}  # {user_id: profile_data}
match_requests_db = {}  # {id: match_request_data}
images_db = {}  # {user_id: base64_image_data}
user_counter = 1
request_counter = 1

# 기본 프로필 이미지 URL
DEFAULT_MENTOR_IMAGE = "https://placehold.co/500x500.jpg?text=MENTOR"
DEFAULT_MENTEE_IMAGE = "https://placehold.co/500x500.jpg?text=MENTEE"

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = users_db.get(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@app.get("/")
async def root():
    """루트 경로 - Swagger UI로 리다이렉트"""
    return RedirectResponse(url="/swagger-ui")

# 1. 인증 API
@app.post("/api/signup", status_code=201)
async def signup(request: SignupRequest):
    global user_counter
    
    # 이메일 중복 확인
    for user in users_db.values():
        if user["email"] == request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # 사용자 생성
    user_id = user_counter
    user_counter += 1
    
    user_data = {
        "id": user_id,
        "email": request.email,
        "password": get_password_hash(request.password),
        "name": request.name,
        "role": request.role.value
    }
    
    users_db[user_id] = user_data
    
    # 기본 프로필 생성
    default_image_url = DEFAULT_MENTOR_IMAGE if request.role == UserRole.MENTOR else DEFAULT_MENTEE_IMAGE
    profile_data = {
        "name": request.name,
        "bio": "",
        "imageUrl": default_image_url,
    }
    
    if request.role == UserRole.MENTOR:
        profile_data["skills"] = []
    
    profiles_db[user_id] = profile_data
    
    return {"message": "User created successfully"}

@app.post("/api/login")
async def login(request: LoginRequest):
    # 사용자 찾기
    user = None
    for u in users_db.values():
        if u["email"] == request.email:
            user = u
            break
    
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # JWT 토큰 생성
    token_data = {
        "sub": str(user["id"]),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"]
    }
    
    access_token = create_access_token(token_data)
    
    return LoginResponse(token=access_token)

@app.get("/main")
async def main_page():
    """로그인 후 메인 페이지로 리다이렉트"""
    return RedirectResponse(url="http://localhost:3000")

# 2. 사용자 정보 API
@app.get("/api/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    profile = profiles_db.get(user_id, {})
    
    return UserResponse(
        id=user_id,
        email=current_user["email"],
        role=current_user["role"],
        profile=ProfileResponse(**profile)
    )

@app.get("/api/images/{role}/{id}")
async def get_profile_image(role: str, id: int, current_user: dict = Depends(get_current_user)):
    """프로필 이미지 반환"""
    image_data = images_db.get(id)
    
    if image_data:
        # Base64 디코딩해서 이미지 반환
        try:
            # data:image/jpeg;base64, 같은 prefix가 있다면 제거
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            return Response(content=image_bytes, media_type="image/jpeg")
        except Exception as e:
            print(f"Error decoding image: {e}")
    
    # 기본 이미지 URL로 리다이렉트
    default_url = DEFAULT_MENTOR_IMAGE if role == "mentor" else DEFAULT_MENTEE_IMAGE
    return RedirectResponse(url=default_url)

@app.put("/api/profile")
async def update_profile(request: UpdateProfileRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    # 사용자 정보 업데이트
    users_db[user_id]["name"] = request.name
    
    # 프로필 정보 업데이트
    profile_data = {
        "name": request.name,
        "bio": request.bio,
        "imageUrl": f"/api/images/{current_user['role']}/{user_id}"
    }
    
    if current_user["role"] == "mentor" and request.skills:
        profile_data["skills"] = request.skills
    
    profiles_db[user_id] = profile_data
    
    # 이미지 저장
    if request.image:
        images_db[user_id] = request.image
    
    return UserResponse(
        id=user_id,
        email=current_user["email"],
        role=current_user["role"],
        profile=ProfileResponse(**profile_data)
    )

# 3. 멘토 리스트 API
@app.get("/api/mentors")
async def get_mentors(
    skill: Optional[str] = None,
    order_by: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """멘토 리스트 조회 (멘티만 접근 가능)"""
    if current_user["role"] != "mentee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentees can access mentor list"
        )
    
    mentors = []
    for user_id, user in users_db.items():
        if user["role"] == "mentor":
            profile = profiles_db.get(user_id, {})
            mentor_data = {
                "id": user_id,
                "email": user["email"],
                "role": user["role"],
                "profile": profile
            }
            
            # 스킬 필터링
            if skill:
                if "skills" in profile and skill.lower() in [s.lower() for s in profile["skills"]]:
                    mentors.append(mentor_data)
            else:
                mentors.append(mentor_data)
    
    # 정렬
    if order_by == "name":
        mentors.sort(key=lambda x: x["profile"].get("name", ""))
    elif order_by == "skill":
        mentors.sort(key=lambda x: ",".join(x["profile"].get("skills", [])))
    else:
        mentors.sort(key=lambda x: x["id"])
    
    return mentors

# 4. 매칭 요청 API
@app.post("/api/match-requests")
async def create_match_request(request: MatchRequestCreate, current_user: dict = Depends(get_current_user)):
    """매칭 요청 생성 (멘티만 가능)"""
    global request_counter
    
    if current_user["role"] != "mentee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentees can send match requests"
        )
    
    # 멘토 존재 확인
    mentor = users_db.get(request.mentorId)
    if not mentor or mentor["role"] != "mentor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mentor not found"
        )
    
    # 중복 요청 확인
    for req in match_requests_db.values():
        if (req["menteeId"] == current_user["id"] and 
            req["mentorId"] == request.mentorId and 
            req["status"] == "pending"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request already sent to this mentor"
            )
    
    # 매칭 요청 생성
    request_id = request_counter
    request_counter += 1
    
    match_request = {
        "id": request_id,
        "mentorId": request.mentorId,
        "menteeId": request.menteeId,
        "message": request.message,
        "status": "pending"
    }
    
    match_requests_db[request_id] = match_request
    
    return MatchRequestResponse(**match_request)

@app.get("/api/match-requests/incoming")
async def get_incoming_requests(current_user: dict = Depends(get_current_user)):
    """들어온 매칭 요청 조회 (멘토만 가능)"""
    if current_user["role"] != "mentor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentors can view incoming requests"
        )
    
    requests = []
    for req in match_requests_db.values():
        if req["mentorId"] == current_user["id"]:
            requests.append(MatchRequestResponse(**req))
    
    return requests

@app.get("/api/match-requests/outgoing")
async def get_outgoing_requests(current_user: dict = Depends(get_current_user)):
    """보낸 매칭 요청 조회 (멘티만 가능)"""
    if current_user["role"] != "mentee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentees can view outgoing requests"
        )
    
    requests = []
    for req in match_requests_db.values():
        if req["menteeId"] == current_user["id"]:
            requests.append(MatchRequestOutgoing(
                id=req["id"],
                mentorId=req["mentorId"],
                menteeId=req["menteeId"],
                status=req["status"]
            ))
    
    return requests

@app.put("/api/match-requests/{request_id}/accept")
async def accept_match_request(request_id: int, current_user: dict = Depends(get_current_user)):
    """매칭 요청 수락 (멘토만 가능)"""
    if current_user["role"] != "mentor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentors can accept requests"
        )
    
    request_data = match_requests_db.get(request_id)
    if not request_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    if request_data["mentorId"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot accept other mentor's request"
        )
    
    # 요청 수락
    request_data["status"] = "accepted"
    
    # 다른 대기중인 요청들을 자동으로 거절
    for req in match_requests_db.values():
        if (req["mentorId"] == current_user["id"] and 
            req["id"] != request_id and 
            req["status"] == "pending"):
            req["status"] = "rejected"
    
    return MatchRequestResponse(**request_data)

@app.put("/api/match-requests/{request_id}/reject")
async def reject_match_request(request_id: int, current_user: dict = Depends(get_current_user)):
    """매칭 요청 거절 (멘토만 가능)"""
    if current_user["role"] != "mentor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentors can reject requests"
        )
    
    request_data = match_requests_db.get(request_id)
    if not request_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    if request_data["mentorId"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot reject other mentor's request"
        )
    
    request_data["status"] = "rejected"
    
    return MatchRequestResponse(**request_data)

@app.delete("/api/match-requests/{request_id}")
async def cancel_match_request(request_id: int, current_user: dict = Depends(get_current_user)):
    """매칭 요청 취소 (멘티만 가능)"""
    if current_user["role"] != "mentee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentees can cancel requests"
        )
    
    request_data = match_requests_db.get(request_id)
    if not request_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    if request_data["menteeId"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot cancel other mentee's request"
        )
    
    request_data["status"] = "cancelled"
    
    return MatchRequestResponse(**request_data)
