from typing import Dict, Any
import json
import click
from flask import Flask, render_template, request, url_for, redirect
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate



from database import db, migrate
import local_tools
import utils_for_start
from models import Tutor, Booking, ClassesRequest
from forms import BookingRequestForm, ClassesRequestForm
from random import sample

DATA_TEACHERS = "static/teachers.json"  # all tutors
DATA_BOOKINGS = "static/bookings.json"  # all bookings
DATA_CLIENT_REQUEST = "static/request.json"  # last request

app = Flask("__name__")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tutors.db'
app.secret_key = 'my-super-secret-phrase-I-dont-tell-this-to-nobody-excluding-my-wife-my-chirdren-my-friens-my-colleagues'
db.init_app(app)
migrate.init_app(app, db)


tutors = local_tools.get_teachers(DATA_TEACHERS)
goals = local_tools.get_goals()


@app.cli.command('first_init')
def create_tables_from_json():
    #TODO: Как это вынести в отдельный файл, который не будет в продакшин?
    db.drop_all()
    db.create_all()
    n_objects= utils_for_start.create_db_from_json(db)
    click.echo(f"Created {n_objects} objects in db" )
    for rec in db.session.query(Tutor).order_by(Tutor.name.desc()).all():
        click.echo(rec)



@app.route('/')
def index(all_selected=False):
    # return "Here is a start page"
    tutors = db.session.query(Tutor).all()
    if all_selected:
        #TODO: не срабатывает!
        selected_tutors = tutors
    else:
        # случайные 6 из списка
        selected_tutors = [tutors[i] for i in sample(range(len(tutors)), k=min(6, len(tutors)))]

    for tutor in selected_tutors:
        # TODO: переделать на уровне модели!
        tutor.goals = json.loads(tutor.goals)
        tutor.free = json.loads(tutor.free)

    return render_template("index.html", goals=goals, tutors=selected_tutors)


@app.route("/goals/<goal>")
def app_goals(goal):
    # "- цели /goals/<goal>/  – здесь будет цель <goal>"
    if not goal or goal not in goals:
        goal = "travel"
    # selected_tutors = [tutor for tutor in tutors if goal in tutor["goals"]]
    selected_tutors = db.session.query(Tutor).filter(Tutor.goals.contains(goal)).order_by(Tutor.price).all()
    for tutor in selected_tutors:
        # TODO: переделать на уровне модели!
        tutor.goals = json.loads(tutor.goals)
        tutor.free = json.loads(tutor.free)

    return render_template("goal.html", goal=goal, goals=goals, tutors=selected_tutors)


@app.route("/profiles")
def tutor_profile_0():
    return tutor_profile(0)


@app.route("/profiles/<int:tutor_id>")
def tutor_profile(tutor_id):
    # return " - профиля учителя /profiles/<id учителя>/ – здесь будет преподаватель <id учителя>"
    tutor=db.session.query(Tutor).get_or_404(tutor_id, description='Преподаватель с таким ID не найден')
    #TODO: переделать на уровне модели!
    tutor.goals = json.loads(tutor.goals)
    tutor.free = json.loads(tutor.free)

    time_table = dict()
    time_table["days_of_week"] = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    time_table["time_slots"] = ["8:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]
    time_table["name_of_days"] = local_tools.get_rus_name_day_of_week('all')
    time_table["open_days"] = {day: any(list(tutor.free[day].values())) for day in time_table["days_of_week"]}
    return render_template("profile.html", tutor=tutor, goals=goals, time_table=time_table)


@app.route("/request")
def form_request_all():
    # TODO: как обойти этот редирект?
    return form_request('')


@app.route("/request/<goal>")
def form_request(goal):
    # return "- заявки на подбор /request/ – здесь будет заявка на подбор"
    if not goal:
        goal = "travel"

    form = ClassesRequestForm()
    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for("form_request_done"))

    return render_template("request.html", form=form, primary_goal=goal, goals=goals)


@app.route("/request_done", methods=["GET", "POST"])
def form_request_done():
    # "- принятой заявки на подбор /request_done/ – заявка на подбор отправлена"
    classes_request = ClassesRequest(
        client_goal = request.form.get("client_goal"),
        client_time = request.form.get("client_time"),
        client_name = request.form.get("client_name"),
        client_phone = request.form.get("client_phone")
    )

    db.session.add(classes_request)
    db.session.commit()

    return render_template("request_done.html", goals=goals, cli_req=classes_request)


@app.route("/booking/<int:tutor_id>/<day_of_week>/<time_slot>", methods=["GET", "POST"])
# @app.route("/booking", methods=["GET","POST"])
def form_tutor_booking(tutor_id, day_of_week, time_slot):
    # "- формы бронирования /booking/<id учителя>/ – здесь будет форма бронирования <id учителя>"
    tutor = db.session.query(Tutor).get_or_404(tutor_id)
    #TODO: переделать на уровне модели!
    tutor.goals = json.loads(tutor.goals)
    tutor.free = json.loads(tutor.free)
    slot_info: Dict[str, Any] = {
        "day_of_week": day_of_week, "day_rus_name": local_tools.get_rus_name_day_of_week(day_of_week), \
        "time_slot": time_slot
    }
    booking = Booking(
        day_of_week=day_of_week,
        time_slot=time_slot,
        tutor_id = tutor.id
    )

    form = BookingRequestForm()
    if request.method == 'POST' and form.validate_on_submit():
        form.populate_object(booking)
        booking.save()
        # db.session.add(booking)
        # db.session.commit()
        return render_template("/booking_done")
    return render_template("booking.html", form=form, tutor=tutor, slot_info=slot_info)


@app.route("/booking_done", methods=["GET", "POST"])
def form_tutor_booking_done():
    # "- принятой заявки на подбор /booking_done/   – заявка отправлена"
    booking = Booking(
        day_of_week=request.form.get('day_of_week'),
        time_slot=request.form.get('time_slot'),
        tutor_id = request.form.get('tutor_id'),
        client_name = request.form.get("client_name"),
        client_phone = request.form.get("client_phone")
    )

    slot_info = {"day_of_week": request.form.get("day_of_week"), \
                 "day_rus_name": local_tools.get_rus_name_day_of_week(request.form.get("day_of_week")), \
                 "time_slot": request.form.get("time_slot")}
    # убрать время у препода
    tutor = db.session.query(Tutor).get(booking.tutor_id)
    # TODO: переделать на уровне модели!
    tutor.free = json.loads(tutor.free)
    tutor.free[booking.day_of_week][booking.time_slot] = False
    tutor.free = json.dumps(tutor.free)

    db.session.add_all([booking, tutor])
    db.session.commit()

    return render_template("booking_done.html", booking=booking, slot_info=slot_info)


if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=5000, debug=True)
    app.run(debug=False)
