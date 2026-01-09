from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class UnitForm(FlaskForm):
    name = StringField("Birim Adı", validators=[DataRequired(), Length(max=50)])
    short_code = StringField("Kısa Kod", validators=[DataRequired(), Length(max=20)])
    is_active = BooleanField("Aktif", default=True)
    submit = SubmitField("Kaydet")
