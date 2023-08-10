from flask import request, jsonify
import time
import openai
import os
from controller import bp
from tasks import make_image

# OpenAI API Key 설정
openai.api_key = os.getenv('OPEN_AI_KEY')


@bp.route('/api/dalle', methods=['POST'])
def generate_image():
    global image_urls
    json_data = request.json
    story = json_data.get("story")
    image_data = make_image.delay(story, os.getenv('OPEN_AI_KEY'))

    while True:
        if not image_data.ready():
            time.sleep(5)
            print("    delay...    ")
            continue
        else:
            image_results = image_data.get()  # 결과를 가져옴
            image_urls = [data['url'] for data in image_results['data']]
            break
    # 이미지 URL을 JSON 형태로 응답합니다.
    return jsonify({'image_urls': image_urls})
