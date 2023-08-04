from flask import jsonify, request
from konlpy.tag import Kkma

from controller import bp
from models.keyword_image import KeywordImage


@bp.route('/api/konlpy', methods=['POST'])
def get_keyword():
    keyword_images = []
    json_data = request.json
    contents = json_data.get('contents')
    diary_keyword = decode(contents)  # tasks.decode.delay(contents)

    while True:
        # if not diary_keyword.ready():
        #     time.sleep(5)
        #     print("    delay...    ")
        #     continue
        # else:
        for word in diary_keyword:
            keyword_data_list = KeywordImage.query.filter_by(keyword=word).limit(10).all()
            if keyword_data_list:
                keyword_images.extend([keyword_data.image_url for keyword_data in keyword_data_list])

        return jsonify(image_urls=keyword_images)


def decode(contents):
    analyzer = Kkma()
    nouns = analyzer.nouns(contents)
    return nouns
