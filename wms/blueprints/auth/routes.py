from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from ...extensions import login_manager
from ...models import User
from . import bp
from .forms import LoginForm


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard" if current_user.is_admin else "stock.stock_list"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.check_password(form.password.data) or not user.is_active:
            flash("Kullanıcı adı/şifre hatalı.", "danger")
            return render_template("auth/login.html", form=form)

        login_user(user)
        next_url = request.args.get("next")
        default_url = url_for("admin.dashboard" if user.is_admin else "stock.stock_list")
        return redirect(next_url or default_url)

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
