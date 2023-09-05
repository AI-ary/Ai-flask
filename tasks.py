import openai
from celery import Celery
from googletrans import Translator
from konlpy.tag import Kkma
from kombu import Queue

celery = Celery('tasks',
                broker='pyamqp://guest:guest@rabbit:5672/',
                backend='redis://ai_redis:6000/0',
                include=["tasks"])

# Celery 결과의 유효 기간을 설정합니다.
celery.conf.result_expires = 300  # 결과가 5분(300초) 후에 만료됩니다.
celery.conf.task_queues = (
    Queue('dalle_tasks', routing_key='dalle.#'),
    Queue('konlpy_tasks', routing_key='konlpy.#'),
)


# worker 개수를 설정하지 않은 경우에는 기본적으로 사용 가능한 CPU 코어의 개수에 따라 worker가 생성됩니다.

# 자연어 처리 AI
@celery.task(name='konlpy_ai')
def decode(story):
    analyzer = Kkma()
    nouns = analyzer.nouns(story)
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
