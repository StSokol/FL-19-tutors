from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, RadioField
from wtforms.validators import ValidationError, DataRequired

class BookingRequestForm(FlaskForm):
    client_name = StringField('Вас зовут:', validators=[DataRequired()])
    client_phone = StringField('Ваш телефон', validators=[DataRequired()])

class ClassesRequestForm(FlaskForm):
    client_goal = RadioField('Какая цель занятий?', choices=[
        ('travel', 'Для путешествий'),
        ('study', 'Для школы'),
        ('work', 'Для работы'),
        ('relocate', 'Для переезда'),
    ],default='travel')
    client_time = RadioField('Сколько времени есть?',
        choices=[
            ('1-2', '1-2 часа в неделю'),
            ('3-5', '3-5 часа в неделю'),
            ('5-7', '5-7 часа в неделю'),
            ('7-10', '7-10 часа в неделю')
        ], default='3-5')
    client_name = StringField('Вас зовут:', validators=[DataRequired()])
    client_phone = StringField('Ваш телефон', validators=[DataRequired()])
