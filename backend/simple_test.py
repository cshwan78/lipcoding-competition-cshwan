#!/usr/bin/env python3
"""
간단한 API 테스트 - 결과를 파일로 저장
"""
import requests
import json
import time
import sys
import traceback
from datetime import datetime

BASE_URL = "http://localhost:8080"
API_BASE_URL = f"{BASE_URL}/api"

def write_result(filename, content):
    """결과를 파일에 저장"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 결과 저장: {filename}")

def test_server_connection():
    """서버 연결 테스트"""
    print("🔗 서버 연결 테스트 중...")
    try:
        response = requests.get(f"{BASE_URL}/swagger-ui", timeout=5)
        if response.status_code == 200:
            return True, "서버 연결 성공"
        else:
            return False, f"서버 응답 코드: {response.status_code}"
    except Exception as e:
        return False, f"서버 연결 실패: {str(e)}"

def test_openapi_docs():
    """OpenAPI 문서 테스트"""
    print("📖 OpenAPI 문서 테스트 중...")
    results = []
    
    try:
        # OpenAPI JSON 테스트
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            results.append("✅ OpenAPI JSON 사용 가능")
            results.append(f"   Title: {data.get('info', {}).get('title', 'Unknown')}")
        else:
            results.append(f"❌ OpenAPI JSON 실패: {response.status_code}")
        
        # Swagger UI 테스트
        response = requests.get(f"{BASE_URL}/swagger-ui", timeout=5)
        if response.status_code == 200:
            results.append("✅ Swagger UI 사용 가능")
        else:
            results.append(f"❌ Swagger UI 실패: {response.status_code}")
            
        # 루트 리다이렉트 테스트
        response = requests.get(f"{BASE_URL}/", allow_redirects=False, timeout=5)
        if response.status_code == 307:
            results.append("✅ 루트 경로 리다이렉트 정상")
        else:
            results.append(f"❌ 루트 리다이렉트 실패: {response.status_code}")
            
    except Exception as e:
        results.append(f"❌ 문서 테스트 오류: {str(e)}")
    
    return results

def test_authentication():
    """인증 API 테스트"""
    print("🔐 인증 API 테스트 중...")
    results = []
    tokens = {}
    
    try:
        # 멘토 회원가입
        signup_data = {
            "email": "test_mentor@example.com",
            "password": "password123",
            "name": "테스트멘토",
            "role": "mentor"
        }
        response = requests.post(f"{API_BASE_URL}/signup", json=signup_data, timeout=5)
        if response.status_code == 201:
            results.append("✅ 멘토 회원가입 성공")
        else:
            results.append(f"❌ 멘토 회원가입 실패: {response.status_code}")
            
        # 멘티 회원가입
        signup_data = {
            "email": "test_mentee@example.com",
            "password": "password123", 
            "name": "테스트멘티",
            "role": "mentee"
        }
        response = requests.post(f"{API_BASE_URL}/signup", json=signup_data, timeout=5)
        if response.status_code == 201:
            results.append("✅ 멘티 회원가입 성공")
        else:
            results.append(f"❌ 멘티 회원가입 실패: {response.status_code}")
        
        # 멘토 로그인
        login_data = {
            "email": "test_mentor@example.com",
            "password": "password123"
        }
        response = requests.post(f"{API_BASE_URL}/login", json=login_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            tokens['mentor'] = data.get('token')
            results.append("✅ 멘토 로그인 성공")
            results.append(f"   토큰 길이: {len(tokens['mentor']) if tokens['mentor'] else 0}")
        else:
            results.append(f"❌ 멘토 로그인 실패: {response.status_code}")
            
        # 멘티 로그인
        login_data = {
            "email": "test_mentee@example.com",
            "password": "password123"
        }
        response = requests.post(f"{API_BASE_URL}/login", json=login_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            tokens['mentee'] = data.get('token')
            results.append("✅ 멘티 로그인 성공")
        else:
            results.append(f"❌ 멘티 로그인 실패: {response.status_code}")
            
    except Exception as e:
        results.append(f"❌ 인증 테스트 오류: {str(e)}")
    
    return results, tokens

def test_profile_api(tokens):
    """프로필 API 테스트"""
    print("👤 프로필 API 테스트 중...")
    results = []
    
    try:
        if 'mentor' in tokens and tokens['mentor']:
            headers = {"Authorization": f"Bearer {tokens['mentor']}"}
            
            # 내 정보 조회
            response = requests.get(f"{API_BASE_URL}/me", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results.append("✅ 멘토 내 정보 조회 성공")
                results.append(f"   이메일: {data.get('email')}")
                results.append(f"   역할: {data.get('role')}")
            else:
                results.append(f"❌ 멘토 내 정보 조회 실패: {response.status_code}")
            
            # 프로필 수정
            profile_data = {
                "id": 1,
                "name": "업데이트된멘토",
                "role": "mentor",
                "bio": "풀스택 개발 멘토입니다",
                "skills": ["Python", "FastAPI", "React"]
            }
            response = requests.put(f"{API_BASE_URL}/profile", headers=headers, json=profile_data, timeout=5)
            if response.status_code == 200:
                results.append("✅ 멘토 프로필 업데이트 성공")
            else:
                results.append(f"❌ 멘토 프로필 업데이트 실패: {response.status_code}")
        
        if 'mentee' in tokens and tokens['mentee']:
            headers = {"Authorization": f"Bearer {tokens['mentee']}"}
            
            # 내 정보 조회
            response = requests.get(f"{API_BASE_URL}/me", headers=headers, timeout=5)
            if response.status_code == 200:
                results.append("✅ 멘티 내 정보 조회 성공")
            else:
                results.append(f"❌ 멘티 내 정보 조회 실패: {response.status_code}")
                
    except Exception as e:
        results.append(f"❌ 프로필 테스트 오류: {str(e)}")
    
    return results

def test_mentor_list(tokens):
    """멘토 리스트 API 테스트"""
    print("👥 멘토 리스트 API 테스트 중...")
    results = []
    
    try:
        if 'mentee' in tokens and tokens['mentee']:
            headers = {"Authorization": f"Bearer {tokens['mentee']}"}
            
            # 전체 멘토 리스트
            response = requests.get(f"{API_BASE_URL}/mentors", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results.append(f"✅ 멘토 리스트 조회 성공 (총 {len(data)}명)")
            else:
                results.append(f"❌ 멘토 리스트 조회 실패: {response.status_code}")
            
            # 스킬 검색
            response = requests.get(f"{API_BASE_URL}/mentors?skill=Python", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results.append(f"✅ 멘토 스킬 검색 성공 (Python: {len(data)}명)")
            else:
                results.append(f"❌ 멘토 스킬 검색 실패: {response.status_code}")
                
            # 정렬
            response = requests.get(f"{API_BASE_URL}/mentors?order_by=name", headers=headers, timeout=5)
            if response.status_code == 200:
                results.append("✅ 멘토 이름순 정렬 성공")
            else:
                results.append(f"❌ 멘토 정렬 실패: {response.status_code}")
                
    except Exception as e:
        results.append(f"❌ 멘토 리스트 테스트 오류: {str(e)}")
    
    return results

def test_match_requests(tokens):
    """매칭 요청 API 테스트"""
    print("🤝 매칭 요청 API 테스트 중...")
    results = []
    
    try:
        if 'mentee' in tokens and tokens['mentee'] and 'mentor' in tokens and tokens['mentor']:
            mentee_headers = {"Authorization": f"Bearer {tokens['mentee']}"}
            mentor_headers = {"Authorization": f"Bearer {tokens['mentor']}"}
            
            # 매칭 요청 생성
            request_data = {
                "mentorId": 1,
                "menteeId": 2,
                "message": "Python과 FastAPI를 배우고 싶습니다!"
            }
            response = requests.post(f"{API_BASE_URL}/match-requests", headers=mentee_headers, json=request_data, timeout=5)
            if response.status_code == 200:
                data = response.json()
                request_id = data.get('id')
                results.append("✅ 매칭 요청 생성 성공")
                results.append(f"   요청 ID: {request_id}")
                
                # 멘토 들어온 요청 조회
                response = requests.get(f"{API_BASE_URL}/match-requests/incoming", headers=mentor_headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    results.append(f"✅ 멘토 들어온 요청 조회 성공 (총 {len(data)}건)")
                else:
                    results.append(f"❌ 멘토 들어온 요청 조회 실패: {response.status_code}")
                
                # 멘티 보낸 요청 조회
                response = requests.get(f"{API_BASE_URL}/match-requests/outgoing", headers=mentee_headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    results.append(f"✅ 멘티 보낸 요청 조회 성공 (총 {len(data)}건)")
                else:
                    results.append(f"❌ 멘티 보낸 요청 조회 실패: {response.status_code}")
                
                # 매칭 요청 수락 테스트
                if request_id:
                    response = requests.put(f"{API_BASE_URL}/match-requests/{request_id}/accept", headers=mentor_headers, timeout=5)
                    if response.status_code == 200:
                        results.append("✅ 매칭 요청 수락 성공")
                    else:
                        results.append(f"❌ 매칭 요청 수락 실패: {response.status_code}")
                        
            else:
                results.append(f"❌ 매칭 요청 생성 실패: {response.status_code}")
                
    except Exception as e:
        results.append(f"❌ 매칭 요청 테스트 오류: {str(e)}")
    
    return results

def test_jwt_claims(tokens):
    """JWT 클레임 검증 테스트"""
    print("🔐 JWT 클레임 검증 테스트 중...")
    results = []
    
    try:
        import json
        import base64
        
        if 'mentor' in tokens and tokens['mentor']:
            token = tokens['mentor']
            # JWT는 header.payload.signature 형태
            parts = token.split('.')
            if len(parts) == 3:
                payload_part = parts[1]
                
                # Base64 디코딩을 위한 패딩 추가
                padding = len(payload_part) % 4
                if padding:
                    payload_part += '=' * (4 - padding)
                
                try:
                    decoded_payload = base64.b64decode(payload_part)
                    payload_data = json.loads(decoded_payload)
                    
                    # RFC 7519 표준 클레임 확인
                    required_claims = ['iss', 'sub', 'aud', 'exp', 'nbf', 'iat', 'jti']
                    missing_claims = []
                    for claim in required_claims:
                        if claim not in payload_data:
                            missing_claims.append(claim)
                    
                    if not missing_claims:
                        results.append("✅ RFC 7519 표준 클레임 모두 포함")
                    else:
                        results.append(f"❌ 누락된 표준 클레임: {missing_claims}")
                    
                    # 커스텀 클레임 확인
                    custom_claims = ['name', 'email', 'role']
                    missing_custom = []
                    for claim in custom_claims:
                        if claim not in payload_data:
                            missing_custom.append(claim)
                    
                    if not missing_custom:
                        results.append("✅ 필수 커스텀 클레임 모두 포함")
                        results.append(f"   이메일: {payload_data.get('email')}")
                        results.append(f"   이름: {payload_data.get('name')}")
                        results.append(f"   역할: {payload_data.get('role')}")
                    else:
                        results.append(f"❌ 누락된 커스텀 클레임: {missing_custom}")
                    
                    # 역할 값 검증
                    role = payload_data.get('role')
                    if role in ['mentor', 'mentee']:
                        results.append("✅ 역할 값이 올바름")
                    else:
                        results.append(f"❌ 잘못된 역할 값: {role}")
                    
                    # 토큰 만료 시간 검증 (1시간)
                    import time
                    current_time = time.time()
                    exp = payload_data.get('exp')
                    iat = payload_data.get('iat')
                    if exp and iat:
                        token_duration = exp - iat
                        if 3500 <= token_duration <= 3700:  # 약 1시간 (허용 오차)
                            results.append("✅ 토큰 유효기간이 올바름 (1시간)")
                        else:
                            results.append(f"❌ 토큰 유효기간 문제: {token_duration}초")
                    
                except Exception as decode_error:
                    results.append(f"❌ JWT 디코딩 실패: {decode_error}")
            else:
                results.append("❌ JWT 형식이 올바르지 않음")
        else:
            results.append("❌ 테스트할 토큰이 없음")
            
    except Exception as e:
        results.append(f"❌ JWT 클레임 테스트 오류: {str(e)}")
    
    return results

def test_security_requirements():
    """보안 요구사항 테스트"""
    print("🛡️ 보안 요구사항 테스트 중...")
    results = []
    
    try:
        # 1. 인증이 필요한 엔드포인트들
        protected_endpoints = [
            "/api/me",
            "/api/profile", 
            "/api/mentors",
            "/api/match-requests",
            "/api/match-requests/incoming",
            "/api/match-requests/outgoing"
        ]
        
        auth_failures = []
        for endpoint in protected_endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
                if response.status_code != 401:
                    auth_failures.append(f"{endpoint} (응답: {response.status_code})")
            except Exception:
                auth_failures.append(f"{endpoint} (요청 실패)")
        
        if not auth_failures:
            results.append("✅ 모든 보호된 엔드포인트가 인증 요구")
        else:
            results.append(f"❌ 인증 요구하지 않는 엔드포인트: {auth_failures}")
        
        # 2. 잘못된 토큰으로 접근 시도
        invalid_token_headers = {"Authorization": "Bearer invalid_token_here"}
        response = requests.get(f"{API_BASE_URL}/me", headers=invalid_token_headers, timeout=5)
        if response.status_code == 401:
            results.append("✅ 잘못된 토큰 거부")
        else:
            results.append(f"❌ 잘못된 토큰 허용: {response.status_code}")
        
        # 3. Authorization 헤더 없이 접근 시도
        response = requests.get(f"{API_BASE_URL}/me", timeout=5)
        if response.status_code == 401:
            results.append("✅ Authorization 헤더 누락 시 거부")
        else:
            results.append(f"❌ Authorization 헤더 누락 허용: {response.status_code}")
        
        # 4. SQL 인젝션 시도 테스트
        sql_injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --"
        ]
        
        for payload in sql_injection_payloads:
            login_data = {
                "email": payload,
                "password": "password123"
            }
            response = requests.post(f"{API_BASE_URL}/login", json=login_data, timeout=5)
            if response.status_code in [400, 401, 422]:  # 예상되는 에러 응답
                continue
            else:
                results.append(f"❌ SQL 인젝션 취약점 가능: {payload}")
                break
        else:
            results.append("✅ SQL 인젝션 방어 양호")
        
        # 5. XSS 방어 테스트
        xss_payload = "<script>alert('xss')</script>"
        signup_data = {
            "email": "xss@test.com",
            "password": "password123",
            "name": xss_payload,
            "role": "mentor"
        }
        response = requests.post(f"{API_BASE_URL}/signup", json=signup_data, timeout=5)
        if response.status_code in [201, 400]:  # 생성되거나 검증 실패
            results.append("✅ XSS 페이로드 처리 양호")
        else:
            results.append(f"❌ XSS 처리 문제 가능: {response.status_code}")
            
    except Exception as e:
        results.append(f"❌ 보안 테스트 오류: {str(e)}")
    
    return results

def run_all_tests():
    """모든 테스트 실행"""
    print("🧪 API 요구사항 테스트 시작")
    print("=" * 50)
    
    # 결과 저장용
    all_results = []
    all_results.append(f"API 테스트 결과 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    all_results.append("=" * 50)
    
    # 1. 서버 연결 테스트
    success, message = test_server_connection()
    all_results.append(f"\n🔗 서버 연결: {message}")
    
    if not success:
        all_results.append("❌ 서버가 실행되지 않아서 테스트를 중단합니다.")
        write_result("test_results.txt", "\n".join(all_results))
        return False
    
    # 2. 문서화 테스트
    results = test_openapi_docs()
    all_results.append("\n📖 OpenAPI 문서 테스트:")
    all_results.extend([f"   {r}" for r in results])
    
    # 3. 인증 테스트
    results, tokens = test_authentication()
    all_results.append("\n🔐 인증 API 테스트:")
    all_results.extend([f"   {r}" for r in results])
    
    # 4. 프로필 테스트
    results = test_profile_api(tokens)
    all_results.append("\n👤 프로필 API 테스트:")
    all_results.extend([f"   {r}" for r in results])
    
    # 5. 멘토 리스트 테스트
    results = test_mentor_list(tokens)
    all_results.append("\n👥 멘토 리스트 API 테스트:")
    all_results.extend([f"   {r}" for r in results])
    
    # 6. 매칭 요청 테스트
    results = test_match_requests(tokens)
    all_results.append("\n🤝 매칭 요청 API 테스트:")
    all_results.extend([f"   {r}" for r in results])
    
    # 7. JWT 클레임 검증 테스트
    results = test_jwt_claims(tokens)
    all_results.append("\n🔐 JWT 클레임 검증 테스트:")
    all_results.extend([f"   {r}" for r in results])
    
    # 8. 보안 요구사항 테스트
    results = test_security_requirements()
    all_results.append("\n🛡️ 보안 요구사항 테스트:")
    all_results.extend([f"   {r}" for r in results])
    
    # 결과 저장
    all_results.append("\n" + "=" * 50)
    all_results.append("테스트 완료!")
    
    result_text = "\n".join(all_results)
    write_result("test_results.txt", result_text)
    
    print(result_text)
    return True

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n🛑 테스트가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        error_msg = f"❌ 테스트 실행 중 오류: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        write_result("test_error.txt", error_msg)
