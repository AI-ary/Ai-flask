from functools import wraps

from flask_restx import Namespace

Dalle = Namespace(
    name="Dalle_API",
    description="DALLE AI로부터 생성된 이미지를 받는 API.",
)

Konlpy = Namespace(
    name="Konlpy_API",
    description="Konlpy AI로부터 단어와 일치하는 URL을 조회하는 API.",
)


def handle_exceptions(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            return {"error": str(ve)}, 400  # Bad Request
        except Exception as e:
            return {"error": str(e)}, 500  # Internal Server Error

    return decorated_function


INPUT_STORY_ERROR = "일기 내용을 입력해주세요"
