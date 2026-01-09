from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class WarehouseForm(FlaskForm):
    name = StringField("Depo Adı", validators=[DataRequired(), Length(max=200)])
    address = TextAreaField("Adres", validators=[Optional()])
    is_active = BooleanField("Aktif", default=True)
    submit = SubmitField("Kaydet")


class ShelfForm(FlaskForm):
    code = StringField("Kod", validators=[DataRequired(), Length(max=50)])
    description = TextAreaField("Açıklama", validators=[Optional()])
    submit = SubmitField("Kaydet")
