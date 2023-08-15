from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from config import databaseConfig
from config.databaseConfig import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_SCHEMA

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(databaseConfig)

    # CORS
    CORS(app, resources={r'*': {'origins': '*'}})

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)

    # 블루프린트
    from controller import DalleController, KonlpyController
    app.register_blueprint(DalleController.bp, name='dalle')
    app.register_blueprint(KonlpyController.bp, name='konlpy')

    return app
