from flask_restx import Namespace

Dalle = Namespace(
    name="Dalle_API",
    description="DALLE AI로부터 생성된 이미지를 받는 API.",
)

Konlpy = Namespace(
    name="Konlpy_API",
    description="Konlpy AI로부터 단어와 일치하는 URL을 조회하는 API.",
)