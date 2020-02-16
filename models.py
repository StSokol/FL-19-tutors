from database import db


class Tutor(db.Model):
    __tablename__ = 'tutors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    about = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    goals = db.Column(db.String, nullable=False)
    free = db.Column(db.String, nullable=False)
    bookings = db.relationship('Booking', back_populates='tutor')

    def __repr__(self):
        return "<Tutor(id='%s', name='%s')>" % (self.id, self.name)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.String(3), nullable=False)
    time_slot = db.Column(db.String(10), nullable=False)
    client_name = db.Column(db.String, nullable=False)
    client_phone = db.Column(db.String, nullable=False)
    tutor = db.relationship('Tutor', back_populates="bookings")
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutors.id'))

    def __repr__(self):
        return "<Booking(id='%s', tutor='%s', day_of_week='%s', time_slot='%s')>" % (self.id, self.tutor, self.day_of_week, self.time_slot)


class ClassesRequest(db.Model):
    __tablename__ = 'classes_request'
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String, nullable=False)
    client_phone = db.Column(db.String, nullable=False)
    client_goal = db.Column(db.String, nullable=False)
    client_time = db.Column(db.String, nullable=False)

    def __repr__(self):
        return "<ClassesRequest(id='%s', client='%s', goal='%s')>" % (self.id, self.client_name, self.client_goal)


