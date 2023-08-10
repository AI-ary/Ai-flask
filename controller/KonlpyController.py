from flask import jsonify, request
import time

from controller import bp
from models.keyword_image import KeywordImage
from tasks import decode


@bp.route('/api/konlpy', methods=['POST'])
def get_keyword():
    json_data = request.json
    contents = json_data.get('contents')
    diary_keyword = decode.delay(contents)

    keyword_images_dict = {}
    while True:
        if not diary_keyword.ready():
            time.sleep(5)
            print("    delay...    ")
            continue
        else:
            for word in diary_keyword.get():
                keyword_data_list = KeywordImage.query.filter_by(keyword=word).limit(10).all()
                if keyword_data_list:
                    keyword_images_dict[word] = [keyword_data.image_url for keyword_data in keyword_data_list]

    return jsonify(keyword_images_dict)

