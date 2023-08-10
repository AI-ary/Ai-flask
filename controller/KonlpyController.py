from flask import jsonify, request

from controller import bp
from models.keyword_image import KeywordImage
from tasks import celery


@bp.route('/api/konlpy', methods=['POST'])
def generate_keyword():
    json_data = request.json
    contents = json_data.get('contents')
    task = celery.send_task('konlpy_ai', kwargs={'contents': contents})
    task_id = task.id
    return {"task_id": task_id}


@bp.route('/api/konlpy/task', methods=['POST'])
def get_task_status():
    json_data = request.json
    task_id = json_data.get("task_id")
    status = celery.AsyncResult(task_id, app=celery)
    return {"status": str(status.state)}


@bp.route('/api/konlpy/result', methods=['POST'])
def get_task_result():
    json_data = request.json
    task_id = json_data.get("task_id")
    diary_keyword = celery.AsyncResult(task_id).result

    keyword_images_dict = {}
    for word in diary_keyword:
        keyword_data_list = KeywordImage.query.filter_by(keyword=word).limit(10).all()
        if keyword_data_list:
            keyword_images_dict[word] = [keyword_data.image_url for keyword_data in keyword_data_list]
    return jsonify(keyword_images_dict)


