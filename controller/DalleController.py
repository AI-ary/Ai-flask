from flask import request, jsonify
import openai
import os
from googletrans import Translator

from controller import bp

# OpenAI API Key 설정
openai.api_key = os.getenv('OPEN_AI_KEY')

DRAW_CUTE_CHARACTER = "Draw it as a clean, simple and cute character, ultra-detailed, 8k, " \
                      "realistic drawing, digital art"


@bp.route('/api/dalle', methods=['POST'])
def generate_image():
    # POST 요청으로 받은 JSON 데이터에서 'story' 키의 값을 가져옵니다.
    json_data = request.json
    story = json_data.get("story")

    # 번역기를 만든다.
    translator = Translator()
    # 영어로 번역
    story_en = translator.translate(story + DRAW_CUTE_CHARACTER, 'en').text

    # OpenAI API를 사용하여 이미지 생성 요청
    response = openai.Image.create(
        prompt=story_en,
        n=4,
        size="1024x1024"
    )

    # 생성된 이미지의 URL을 추출합니다.
    image_urls = [data['url'] for data in response['data']]

    # 이미지 URL을 JSON 형태로 응답합니다.
    return jsonify({'image_url': image_urls})
