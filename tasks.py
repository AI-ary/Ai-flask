# from celery import Celery
# from konlpy.tag import Kkma
#
# # app = Celery('config',  backend='rpc://', broker='amqp://gdiary:gdiary123@gdiary_host/gdiary_host', include=['text.views'])
# celery = Celery('tasks', backend='rpc://', broker='pyamqp://guest@gd_rabbitmq//', include=["tasks"])
#
#
# @celery.task
# def decode(contents):
#     analyzer = Kkma()
#     nouns = analyzer.nouns(contents)
#     return nouns
