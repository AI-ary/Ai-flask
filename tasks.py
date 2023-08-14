import openai
from celery import Celery
from googletrans import Translator
from konlpy.tag import Kkma

from config.databaseConfig import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_SCHEMA

# app = Celery('config',  backend='rpc://', broker='amqp://gdiary:gdiary123@gdiary_host/gdiary_host', include=['text.views'])
# celery = Celery('tasks', backend='rpc://', broker='pyamqp://guest@gd_rabbitmq//', include=["tasks"])

celery = Celery('tasks',
                broker='pyamqp://guest:guest@rabbit:5672/',
                backend='redis://gd_ai_redis:6379/0',
                include=["tasks"])

# Celery 결과의 유효 기간을 설정합니다.
celery.conf.result_expires = 300  # 결과가 5분(300초) 후에 만료됩니다.


# 자연어 처리 AI
@celery.task(name='konlpy_ai')
def decode(contents):
    analyzer = Kkma()
    nouns = analyzer.nouns(contents)
    return nouns


# 달리 AI
DRAW_CUTE_CHARACTER = "Draw it as a clean, simple and cute character, ultra-detailed, 8k, " \
                      "realistic drawing, digital art"


@celery.task(name='dalle2_ai')
def make_image(story, api_key):
    openai.api_key = api_key  # 전달된 API 키 설정
    translator = Translator()
    story_en = translator.translate(story + DRAW_CUTE_CHARACTER, 'en').text
    response = openai.Image.create(
        prompt=story_en,
        n=4,
        size="1024x1024"
    )
    return response
