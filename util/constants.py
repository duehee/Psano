"""
공통 상수 정의
- 여러 파일에서 사용하는 상수를 한 곳에서 관리
"""

# 총 질문 수 (형성기 완료 기준)
MAX_QUESTIONS = 365

# 대화기 해금 임계값 (answered_total >= 이 값이면 talk 가능)
TALK_UNLOCK_THRESHOLD = MAX_QUESTIONS

# 세션당 질문 수 (기본값)
DEFAULT_SESSION_QUESTION_LIMIT = 5

# 가치축별 질문 수 (5개 축, 각 쌍당 기본값)
DEFAULT_PAIR_QUESTION_COUNT = 73

# 허용된 가치 키 (psano_personality 컬럼명) - 순서 보장을 위해 튜플 사용
VALUE_KEYS_ORDERED = (
    "self_direction",
    "conformity",
    "stimulation",
    "security",
    "hedonism",
    "tradition",
    "achievement",
    "benevolence",
    "power",
    "universalism",
)

# set 버전 (빠른 검색용)
ALLOWED_VALUE_KEYS = frozenset(VALUE_KEYS_ORDERED)