from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional


class PurchaseForm(FlaskForm):
    supplier_id = SelectField("Tedarikçi", coerce=int, validators=[DataRequired()])
    warehouse_id = SelectField("Depo", coerce=int, validators=[DataRequired()])
    shelf_id = SelectField("Raf (opsiyonel)", coerce=int, validators=[Optional()])
    note = TextAreaField("Açıklama", validators=[Optional()])
    submit = SubmitField("Kaydet")


class PurchaseItemForm(FlaskForm):
    product_id = SelectField("Ürün", coerce=int, validators=[DataRequired()])
    quantity = FloatField("Miktar", validators=[DataRequired()])
    submit = SubmitField("Ekle")
