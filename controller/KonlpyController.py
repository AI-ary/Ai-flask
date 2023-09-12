from flask import jsonify, request

from controller import Konlpy
from models.keyword_image import Drawings
from tasks import celery
from flask_restx import Resource, fields

# Swagger model 설정
input_story = Konlpy.model('Konlpy Input story', {'contents': fields.String(required=True, description='Diary story')})
output_task_id = Konlpy.inherit('Konlpy Output Task ID', {
    'task_id': fields.String(description='Konlpy Task ID')
})
input_task_id = Konlpy.model('Konlpy Input Task ID', {'task_id': fields.String(required=True, description='Task ID')})
output_task_status = Konlpy.inherit('Konlpy Output Task Status', {
    'status': fields.String(description='Konlpy Task Status')
})
output_task_result = Konlpy.model('Konlpy Output Task Result', {
    'keyword_images_dict': fields.Raw(description='Images Dictionary URL')
})


@Konlpy.route('/')
class GenerateKeyword(Resource):

    @Konlpy.expect(input_story)
    @Konlpy.response(201, 'Success', output_task_id)
    def post(self):
        story = request.json.get('story')
        task = celery.send_task('konlpy_ai', kwargs={'story': story}, queue='konlpy_tasks')
        task_id = task.id
        return {"task_id": task_id}


@Konlpy.route('/status')
class GetKonlpyStatus(Resource):
    @Konlpy.expect(input_task_id)
    @Konlpy.response(200, 'Success', output_task_status)
    def post(self):
        task_id = request.json.get("task_id")
        status = celery.AsyncResult(task_id, app=celery)
        return {"status": str(status.state)}


@Konlpy.route('/result')
class GetKonlpyResult(Resource):
    @Konlpy.expect(input_task_id)
    @Konlpy.response(200, 'Success', output_task_result)
    def post(self):
        task_id = request.json.get("task_id")
        diary_keyword = celery.AsyncResult(task_id).result

        drawings_images_dict = {}
        for word in diary_keyword:
            drawings_data_list = Drawings.query.filter_by(keyword=word).limit(10).all()
            if drawings_data_list:
                drawings_images_dict[word] = [keyword_data.image_url for keyword_data in drawings_data_list]
        return jsonify(drawings_images_dict)
