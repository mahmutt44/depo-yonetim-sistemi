from flask_wtf import FlaskForm
from wtforms import BooleanField, FloatField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Optional


class CategoryForm(FlaskForm):
    name = StringField("Kategori Adı", validators=[DataRequired()])
    submit = SubmitField("Kaydet")


class ProductForm(FlaskForm):
    name = StringField("Ürün Adı", validators=[DataRequired()])
    sku = StringField("SKU", validators=[DataRequired()])
    barcode = StringField("Barkod", validators=[Optional()])

    category_id = SelectField("Kategori", coerce=int, validators=[Optional()])
    unit_id = SelectField("Birim", coerce=int, validators=[DataRequired()])
    min_stock_level = FloatField("Minimum Stok", validators=[NumberRange(min=0)], default=0)
    description = TextAreaField("Açıklama", validators=[Optional()])
    is_active = BooleanField("Aktif", default=True)

    submit = SubmitField("Kaydet")
