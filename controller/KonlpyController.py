from flask import jsonify, request
from konlpy.tag import Kkma

from controller import bp
from models.keyword_image import KeywordImage


@bp.route('/api/konlpy', methods=['POST'])
def get_keyword():
    json_data = request.json
    contents = json_data.get('contents')
    diary_keyword = decode(contents)

    keyword_images_dict = {}
    for word in diary_keyword:
        keyword_data_list = KeywordImage.query.filter_by(keyword=word).limit(10).all()
        if keyword_data_list:
            keyword_images_dict[word] = [keyword_data.image_url for keyword_data in keyword_data_list]

    return jsonify(keyword_images_dict)


def decode(contents):
    analyzer = Kkma()
    nouns = analyzer.nouns(contents)
    return nouns
