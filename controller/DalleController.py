from flask import request
import openai
import os
from controller import bp
from tasks import celery

# OpenAI API Key 설정
openai.api_key = os.getenv('OPEN_AI_KEY')


@bp.route('/api/dalle', methods=['POST'])
def generate_image():
    json_data = request.json
    story = json_data.get("story")
    task = celery.send_task('dalle2_ai', kwargs={
        'story': story, 'api_key': openai.api_key})
    task_id = task.id
    return {"task_id": task_id}


@bp.route('/api/dalle/task', methods=['POST'])
def get_task_status():
    json_data = request.json
    task_id = json_data.get("task_id")
    status = celery.AsyncResult(task_id, app=celery)
    return {"status": str(status.state)}


@bp.route('/api/dalle/result', methods=['POST'])
def get_task_result():
    json_data = request.json
    task_id = json_data.get("task_id")
    image_results = celery.AsyncResult(task_id).result
    image_urls = [data['url'] for data in image_results['data']]
    return image_urls
