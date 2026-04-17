from flask import Flask, render_template, url_for, request, redirect, flash, session
import random

app = Flask(__name__)
app.secret_key = "Aa88bfo3bjxdd"  # Ключ

# Список
phones = [
    {"firm": f, "name": n, "price": p, "cameras": c} for f, n, p, c in [
        ("Samsung", "Galaxy S26 Ultra", 70299, 4),
        ("Apple", "iPhone 17 Pro Max", 69999, 3),
        ("Xiaomi", "Redmi Note 14", 7499, 3),
        ("Apple", "iPhone 17 Pro", 63999, 3),
        ("Xiaomi", "Redmi Note 15", 8999, 3),
        ("Apple", "iPhone 17", 46799, 2),
        ("Samsung", "Galaxy S26 Plus", 54249, 3),
        ("Apple", "iPhone Air", 48999, 1),
        ("Samsung", "Galaxy S25 FE", 32799, 3),
        ("Apple", "iPhone 16", 39299, 2),
    ]
]


# Головна сторінка
@app.route("/")
def index():
    return render_template("phones.html", phones=phones)


# Пошук
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":  # Процес пошуку
        mode = request.form.get("mode")
        firm = request.form.get("firm")
        price = request.form.get("price")
        result = []

        if mode == "firm":  # Тільки одна фірма
            if not firm:
                flash("Введіть фірму", "danger")
                return redirect("/search")
            result = [phone for phone in phones if phone["firm"].lower() == firm.lower()]

        elif mode == "price":  # Менше або дорівнює ціні
            if not price:
                flash("Введіть ціну", "danger")
                return redirect("/search")
            try:
                price = int(price)
            except:
                flash("Ціна має бути числом", "danger")  # Перевірки
                return redirect("/search")
            if price <= 0:
                flash("Ціна має бути більше 0", "danger")  # Перевірки
                return redirect("/search")
            result = [phone for phone in phones if phone["price"] <= int(price)]

        elif mode == "cheap_cameras":  # Найдешевший з максимумом камер
            max_c = max(phone["cameras"] for phone in phones)
            result = [min([phone for phone in phones if phone["cameras"] == max_c], key=lambda x:x["price"])]

        if not result:  # Немає даних
            flash("Немає даних", "warning")
            return redirect("/no_data")

        flash("Успішно!", "success")
        return render_template("phones.html", phones=result)

    return render_template("search.html")  # Сторінка пошуку


# Додавання даних
@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "POST":  # Процесс додавання
        firm = request.form.get("firm")
        name = request.form.get("name")
        price = request.form.get("price")
        cameras = request.form.get("cameras")

        if not firm or not name or not price or not cameras:  # Перевірка полів
            flash("Заповніть всі поля", "danger")
            return redirect("/add")

        try:
            price = int(price)
            cameras = int(cameras)
        except:
            flash("Ціна і камери мають бути числами", "danger")  # Перевірки
            return redirect("/add")
        if price <= 0:
            flash("Ціна має бути більше 0", "danger")  # Перевірки
            return redirect("/add")
        if cameras < 1 or cameras > 10:
            flash("Кількість камер має бути від 1 до 10", "danger")  # Перевірки
            return redirect("/add")

        phones.append({
            "firm": firm,
            "name": name,
            "price": int(price),
            "cameras": int(cameras)
        })

        flash("Телефон додано!", "success")
        return redirect("/")

    return render_template("add.html")  # Сторінка додавання даних


# Сторінка гри
@app.route("/game", methods=["GET", "POST"])
def game():

    options = ["Камінь", "Ножиці", "Вогонь", "Змія", "Людина", "Дерево", "Вовк", "Губка", "Папір", "Повітря", "Вода", "Дракон", "Диявол", "Запальничка", "Пістолет"]

    # Ініціалізація
    if "round" not in session:
        session["round"] = 1
        session["user_score"] = 0
        session["comp_score"] = 0
        session["last_result"] = None
        session["last_comp"] = None

    # Хід
    if request.method == "POST":

        if session["round"] > 15:
            return redirect(url_for("game"))

        user_choice = request.form.get("choice")
        comp_choice = random.choice(options)

        idx_user = options.index(user_choice)
        idx_comp = options.index(comp_choice)

        n = len(options)
        half = n // 2

        if user_choice == comp_choice:
            result = "Нічия"
        elif (idx_comp - idx_user) % n <= half:
            result = "Ви виграли"
            session["user_score"] += 1
        else:
            result = "Ви програли"
            session["comp_score"] += 1

        session["last_result"] = result
        session["last_comp"] = comp_choice

        session["round"] += 1

        return redirect(url_for("game"))

    final = None

    if session["round"] > 15:
        if session["user_score"] > session["comp_score"]:
            final = "Ви виграли"
        elif session["user_score"] < session["comp_score"]:
            final = "Комп’ютер виграв"
        else:
            final = "Нічия"

    return render_template(
        "game.html",
        options=options,
        round=session.get("round"),
        user_score=session.get("user_score"),
        comp_score=session.get("comp_score"),
        result=session.get("last_result"),
        comp=session.get("last_comp"),
        final=final
    )


# Для нової гри
@app.route("/reset_game")
def reset_game():
    session.clear()
    return redirect("/game")


# Сторінка "Немає даних"
@app.route("/no_data")
def no_data():
    return render_template("no_data.html"), 200


# Обробка помилки 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
