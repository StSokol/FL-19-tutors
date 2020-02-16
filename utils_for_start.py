import os
import json
from models import Tutor

DATA_TUTORS = 'first_start_data/teachers.json'


def create_db_from_json(db):
    if not os.path.isfile(DATA_TUTORS):
        print(f'File "{DATA_TUTORS}" not found')
        return 0

    with open(DATA_TUTORS) as f:
        contents = json.loads(f.read())

    for tutor in contents:
        db.session.add(Tutor(
            name=tutor['name'],
            about=tutor['about'],
            rating=tutor['rating'],
            picture=tutor['picture'],
            price=tutor['price'],
            goals=json.dumps(tutor['goals']),
            free=json.dumps(tutor['free']),
        ))
    try:
        db.session.commit()
    except:
        db.session.rollback()

    return len(contents)
