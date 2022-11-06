from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from flask_marshmallow import Marshmallow
import os
import datetime

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


@app.route("/api/users", methods=["GET"])
def users():
    users_list = User.query.all()
    result = users_schema.dump(users_list)
    return jsonify(result)


@app.route("/api/users", methods=["POST"])
def create_user():
    username = request.form["username"]
    user = User.query.filter_by(username=username).first()

    if not username:
        return jsonify(message="Username is required.")
    else:
        if user:
            return jsonify(message="The username " + user.username + " is already registered."), 409
        else:
            try:
                new_user = User(username=username)
                db.session.add(new_user)
                db.session.commit()
            except:
                return jsonify(message="Something went wrong.")
            else:
                return {
                  "username": new_user.username,
                  "_id": new_user._id
                }
            

@app.route("/api/users/<int:_id>/exercises", methods=["POST"])
def add_exercise(_id: int):
    description = request.form["description"]
    duration = request.form["duration"]
    dateinput = request.form["date"]
    
    if dateinput:
        date = datetime.datetime.strptime(dateinput, "%Y-%m-%d")
    else:
        date = datetime.datetime.now()
    
    user = User.query.filter_by(_id=_id).first()

    new_exercise = Exercise(description=description, duration=duration, date=date, user_id=user._id)

    db.session.add(new_exercise)
    db.session.commit()

    return {
        "username": user.username,
        "description": new_exercise.description,
        "duration": new_exercise.duration,
        "date": new_exercise.date.strftime("%a %b %d %Y"),
        "_id": _id
    }


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
