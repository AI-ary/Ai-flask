from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_restx import Api

from config import databaseConfig

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

    # API Swagger
    api = Api(
        app,
        version='v2',
        title="Aiary Project's AI API Server",
        description="AI API Server Swagger",
        doc="/swagger",
        contact="Aiary",
        license="MIT",
    )

    # Controller
    from controller import DalleController, KonlpyController
    api.add_namespace(DalleController.Dalle, "/ai_api/dalle")
    api.add_namespace(KonlpyController.Konlpy, "/ai_api/konlpy")

    return app
