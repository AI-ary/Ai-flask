from flask import request
from flask_restx import Resource, fields
import openai
import os

from controller import Dalle
from tasks import celery

# OpenAI API Key 설정
openai.api_key = os.getenv('OPEN_AI_KEY')

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
    def post(self):
        """일기 내용을 요청시 task_id를 응답해 줍니다."""
        story = request.json.get("story")
        task = celery.send_task('dalle2_ai', kwargs={'story': story, 'api_key': openai.api_key}, queue='dalle_tasks')
        task_id = task.id
        return {"task_id": task_id}


@Dalle.route('/task')
class GetDalleStatus(Resource):
    @Dalle.expect(input_task_id)
    @Dalle.response(200, 'Success', output_task_status)
    def post(self):
        """task_id 요청시 task_status를 응답해 줍니다."""
        task_id = request.json.get("task_id")
        status = celery.AsyncResult(task_id, app=celery)
        return {"status": str(status.state)}


@Dalle.route('/result')
class GetDalleResult(Resource):
    @Dalle.expect(input_task_id)
    @Dalle.response(200, 'Success', output_task_result)
    def post(self):
        """task_id 요청시 task_result를 응답해 줍니다."""
        task_id = request.json.get("task_id")
        image_results = celery.AsyncResult(task_id).result
        image_urls = [data['url'] for data in image_results['data']]
        return {"image_urls": image_urls}
