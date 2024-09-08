from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select
import secrets


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config.update(SECRET_KEY=secrets.token_hex(16))
db.init_app(app)
unknown_error_message = "An unknown error occurred"


class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    month_and_year = db.Column(db.DateTime)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    relation_to_category_tab = db.relationship("Category", foreign_keys=category_id)

    def __repr__(self):
        return "<Expense %r>" % self.quantity


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return "<Category %r>" % self.name


@app.route("/", methods=["POST", "GET"])
def index():

    stmt = (
        select(
            Expenses.quantity,
            Category.name,
            Expenses.month_and_year,
            Expenses.id,
            Expenses.category_id,
        )
        .select_from(Category)
        .join(Expenses, Category.id == Expenses.category_id)
    )
    results = db.session.execute(stmt)
    expenses = []
    period = "total"

    for quantity_results, category_results, month_and_year_results, id_results, category_id_results in results:
        expenses.append(
            dict(
                quantity=quantity_results,
                category_name=category_results,
                month_and_year=str(month_and_year_results)[:-12].replace("-", "/"),
                id=id_results,
                category_id=category_id_results,
            )
        )

    months = list(set([element["month_and_year"] for element in expenses]))
    months.sort(reverse=True)

    categories = Category.query.all()
    categories_by_id = {category.id: category.name for category in categories}

    if request.method == "POST":
        period = request.form["change_val"]

    return render_template(
        "index.html",
        expenses=expenses,
        period=period,
        months=months,
        categories=categories_by_id,
    )


@app.route("/add_expense", methods=["POST", "GET"])
def add_expense():
    categories = Category.query.all()

    if request.method == "POST":

        input_category = request.form["category"]
        ready_category_id = (
            Category.query.filter(Category.name == input_category).all()
        )[0].id

        input_quantity = request.form["quantity"]
        ready_quantity = int(float(input_quantity) * 100)

        input_month = request.form["month_and_year"]
        if input_month:
            ready_month = datetime.strptime(input_month, "%Y-%m")
        else:
            input_month = request.form["month"].zfill(2)
            input_year = request.form["year"]
            month_and_year_str = input_year+'-'+input_month
            ready_month = datetime.strptime(month_and_year_str, "%Y-%m")

        new_position = Expenses(
            quantity=ready_quantity,
            month_and_year=ready_month,
            category_id=ready_category_id,
        )
        try:
            db.session.add(new_position)
            db.session.commit()
            return redirect("/")
        except:
            flash(unknown_error_message)

    else:
        return render_template("index.html", categories=categories)


@app.route("/edit", methods=["POST", "GET"])
def edit():

    stmt = (
        select(Expenses.quantity, Category.name, Expenses.month_and_year, Expenses.id)
        .select_from(Category)
        .join(Expenses, Category.id == Expenses.category_id)
    )
    results = db.session.execute(stmt)
    expenses = []
    for arr_quantity, arr_name, arr_month_and_year, arr_index in results:
        expenses.append(
            dict(
                quantity=arr_quantity,
                category_name=arr_name,
                month_and_year=arr_month_and_year.strftime("%Y/%m"),
                id=arr_index,
            )
        )

    return render_template("edit.html", expenses=expenses)


@app.route("/delete_entry/<int:id>")
def delete_entry(id):
    entry_to_delete = Expenses.query.get_or_404(id)
    try:
        db.session.delete(entry_to_delete)
        db.session.commit()
        return redirect("/edit")
    except:
        flash(unknown_error_message)


@app.route("/edit_categories", methods=["POST", "GET"])
def edit_categories():

    if request.method == "POST":
        category_content = request.form["content"]

        category_in_table = Category.query.filter(Category.name == category_content).all()
        if not category_in_table:

            new_category = Category(name=category_content)
            try:
                db.session.add(new_category)
                db.session.commit()
                return redirect("/")
            except:
                flash(unknown_error_message)

        else:
            flash("There already exists a category like this")

    return redirect("/")


@app.route("/delete_category/<int:id>")
def delete_category(id):
    category_to_delete = Category.query.get_or_404(id)
    the_val = id
    categories_in_use = Expenses.query.filter_by(category_id=the_val).all()
    if not categories_in_use:
        try:
            db.session.delete(category_to_delete)
            db.session.commit()
            return redirect("/")
        except:
            flash(unknown_error_message)
    else:
        flash("You cannot delete non-empty category!")
    return redirect("/")


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)