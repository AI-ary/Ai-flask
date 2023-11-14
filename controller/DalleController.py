from io import BytesIO
from urllib.parse import urlparse
from flask import request
from flask_restx import Resource, fields
from PIL import Image
import openai
import os
import requests
import concurrent.futures

from config.S3Connection import s3_connection
from config.S3bucketConfig import S3_BUCKET_NAME, S3_BUCKET_REGION
from controller import Dalle, handle_exceptions, INPUT_STORY_ERROR
from tasks import celery

# OpenAI API Key 설정
openai.api_key = os.getenv('OPEN_AI_KEY')

# s3 클라이언트 생성
s3_client = s3_connection()

# Swagger model 설정
input_story = Dalle.model('Dalle Input Story', {'story': fields.String(required=True, description='Diary story')})
output_task_id = Dalle.inherit('Dalle Output Task ID', {
    'task_id': fields.String(description='Dalle Task ID')
})
input_task_id = Dalle.model('Dalle Input Task ID', {'task_id': fields.String(required=True, description='Task ID')})
output_task_status = Dalle.inherit('Dalle Output Task Status', {
    'status': fields.String(description='Dalle Task Status')
})
output_task_result = Dalle.model('Dalle Output Task Result', {
    'image_urls': fields.List(fields.String(description='Image URL'))
})


@Dalle.route('/')
class GenerateImage(Resource):
    @Dalle.expect(input_story)
    @Dalle.response(201, 'Success', output_task_id)
    @handle_exceptions
    def post(self):
        """일기 내용을 요청시 task_id를 응답해 줍니다."""
        story = request.json.get("story")
        if story == "":
            raise ValueError(INPUT_STORY_ERROR)

        task = celery.send_task('dalle3_ai', kwargs={'story': story, 'api_key': openai.api_key}, queue='dalle_tasks')
        task_id = task.id
        return {"task_id": task_id}


@Dalle.route('/status')
class GetDalleStatus(Resource):
    @Dalle.expect(input_task_id)
    @Dalle.response(200, 'Success', output_task_status)
    @handle_exceptions
    def post(self):
        """task_id 요청시 task_status를 응답해 줍니다."""
        task_id = request.json.get("task_id")
        status = celery.AsyncResult(task_id, app=celery)
        return {"status": str(status.state)}


@Dalle.route('/result')
class GetDalleResult(Resource):
    @Dalle.expect(input_task_id)
    @Dalle.response(200, 'Success', output_task_result)
    @handle_exceptions
    def post(self):
        """task_id 요청시 task_result를 응답해 줍니다."""
        task_id = request.json.get("task_id")
        image_results = celery.AsyncResult(task_id).result
        image_urls = [image_results]

        s3_image_urls = []

        # 병렬 다운로드를 위한 함수 정의
        def download_and_upload_image(image_url):
            s3_url = upload_image_to_s3(image_url)
            s3_image_urls.append(s3_url)

        # 백그라운드 스레드 풀을 사용하여 병렬 다운로드 실행
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(download_and_upload_image, image_urls)

        return {"image_urls": s3_image_urls}


# 이미지 압축 및 업로드 함수 수정
def upload_image_to_s3(image_url):
    parsed_url = urlparse(image_url)
    file_name = 'images/dalle/' + os.path.basename(parsed_url.path)

    # 이미지 다운로드
    response = requests.get(image_url)
    image_data = response.content

    # 이미지 압축
    with BytesIO() as output:
        img = Image.open(BytesIO(image_data))
        img.save(output, format="WebP", quality=85)
        output.seek(0)
        compressed_image_data = output.read()

    # S3에 업로드
    s3_client.Bucket(S3_BUCKET_NAME).put_object(
        Body=compressed_image_data,
        Key=file_name,
        ContentType='image/webp'
    )

    s3_url = f"https://{S3_BUCKET_NAME}.s3.{S3_BUCKET_REGION}.amazonaws.com/{file_name}"

    return s3_url
