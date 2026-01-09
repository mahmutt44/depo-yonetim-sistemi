from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional


class StockMovementForm(FlaskForm):
    product_id = SelectField("Ürün", coerce=int, validators=[DataRequired()])
    warehouse_id = SelectField("Depo", coerce=int, validators=[DataRequired()])
    shelf_id = SelectField("Raf (opsiyonel)", coerce=int, validators=[Optional()])

    movement_type = SelectField(
        "Hareket Tipi",
        choices=[("IN", "Giriş"), ("OUT", "Çıkış"), ("ADJUST", "Düzeltme")],
        validators=[DataRequired()],
    )

    quantity = FloatField("Miktar", validators=[DataRequired()])

    reference_type = SelectField(
        "Referans",
        choices=[
            ("purchase", "Satın Alma"),
            ("sale", "Satış"),
            ("transfer", "Transfer"),
            ("adjustment", "Düzeltme"),
        ],
        validators=[DataRequired()],
    )

    reason = StringField("Sebep (ADJUST için zorunlu)", validators=[Optional()])
    note = TextAreaField("Açıklama", validators=[Optional()])
    submit = SubmitField("Kaydet")
