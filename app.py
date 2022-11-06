from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "exercise.db")
app.config["SECRET_KEY"] = "dev"

db = SQLAlchemy(app)
ma = Marshmallow(app)


@app.cli.command("db_create")
def db_create():
    db.create_all()
    print("Database created.")


@app.cli.command("db_drop")
def db_drop():
    db.drop_all()
    print("Database dropped.")


@app.route("/")
def index():
    return jsonify(message="Welcome to the Exercise Tracker API.")


class User(db.Model):
    __tablename__ = "users"
    _id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)


class Exercise(db.Model):
    __tablename__ = "exercises"
    _id = Column(Integer, primary_key=True)
    description = Column(String)
    duration = Column(Integer)
    date = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users._id"))


class UserSchema(ma.Schema):
    class Meta:
        fields = ("_id", "username")
        load_instance = True


class ExerciseSchema(ma.Schema):
    class Meta:
        fields = ("_id", "description", "duration", "date", "user_id")
        load_instance = True


user_schema = UserSchema()
users_schema = UserSchema(many=True)

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

if __name__ == "__main__":
    app.run(debug=True)
