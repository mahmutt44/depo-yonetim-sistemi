from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class CustomerForm(FlaskForm):
    name = StringField("Müşteri Adı", validators=[DataRequired(), Length(max=200)])
    phone = StringField("Telefon", validators=[Optional(), Length(max=50)])
    email = StringField("E-posta", validators=[Optional(), Length(max=200)])
    address = TextAreaField("Adres", validators=[Optional()])
    is_active = BooleanField("Aktif", default=True)
    submit = SubmitField("Kaydet")
