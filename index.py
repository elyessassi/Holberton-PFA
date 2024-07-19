from flask import Flask, render_template, request, flash, redirect, url_for
import requests
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import UserMixin, login_user, logout_user, current_user, LoginManager, login_required
from werkzeug.security import generate_password_hash, check_password_hash
#creating sqlalchemy and db name
db = SQLAlchemy()
DB_NAME = "DBASE.db"

# inisialisig app

app = Flask(__name__)
app.secret_key = "feehfiajjef ,uh agfauhefae"
app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'
db = SQLAlchemy(app)

# function that creates a database
def create_db(app):
    if not path.exists(DB_NAME):
        with app.app_context():
            db.create_all()
        print("database created")

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
# user class
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    favorites = db.relationship('Favorite')
# favorite class
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    release_date = db.Column(db.TEXT)
    movie_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIxMTFmYWQ1NzY3ODAyZjIzZmEwZjBlMTdkNTVhZjc4NSIsIm5iZiI6MTcyMDY0OTUwMC4xMDE1NzYsInN1YiI6IjY2ODQ5NDRmMzMzZjVmM2RhYTMyZmUwMCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.MeORYLjuJhfx4bmiVIGI_VLXlXBEm5Hr3q4Txo8le9s"
}

response = requests.get(url, headers=headers)
list = response.json().get("results")

# main route that has trending movies
@app.route("/", methods=["GET", "POST"])
def main():
    return render_template("home.html", data=list, user=current_user)
#movie page route
@app.route("/movie_page/<id>", methods=["GET", "POST"])
def movie_page(id):
    mp_headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIxMTFmYWQ1NzY3ODAyZjIzZmEwZjBlMTdkNTVhZjc4NSIsIm5iZiI6MTcyMDY0OTUwMC4xMDE1NzYsInN1YiI6IjY2ODQ5NDRmMzMzZjVmM2RhYTMyZmUwMCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.MeORYLjuJhfx4bmiVIGI_VLXlXBEm5Hr3q4Txo8le9s"
}
    res = requests.get(f"https://api.themoviedb.org/3/movie/{id}", headers=mp_headers)
    data = res.json()
    res_rec = requests.get(f"https://api.themoviedb.org/3/movie/{id}/recommendations", headers=mp_headers)
    rec_data = res_rec.json().get("results")
    if request.method == "POST":
        test = Favorite.query.filter_by(movie_id=id).first()
        if test:
            flash("movie already exists in your favorites list", category="error")
        else:
            add_favorite = Favorite(title=data.get("original_title"), release_date=data.get("release_date") ,movie_id=data.get("id"), user_id=current_user.id)
            db.session.add(add_favorite)
            db.session.commit()
            flash("movie was added successfully to the favorites list", category="success")
    return render_template("movie_page.html", data=data, rec_data=rec_data, user=current_user)
# login page route
@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form["login_email"]
        password = request.form["login_password"]
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("logged in successfully", category="success")
                login_user(user, remember=True)
                return redirect("/")
            else:
                flash("wrong password, try again", category="error")
        else:
            flash("wrong email, try again!!", category="error")
            
    return render_template("login_page.html", user=current_user)
#sign-up page route
@app.route("/Sign-up", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        email = request.form["sign_in_email"]
        password1 = request.form["sign_in_password1"]
        password2 = request.form["sign_in_password2"]
        user = User.query.filter_by(email=email).first()
        if user:
            flash("email already exists", category="error")
        if len(email) < 9:
            flash("email must be greater than 8 characters", category="error")
        elif len(password1) < 5:
            flash("password must be greater than 4 characters", category="error")
        elif password1 != password2:
            flash("the two passwords must be identical", category="error")
        else:
            new_user = User(email=email, password=generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            flash("the account was created successfully", category="success")
            login_user(new_user, remember=True)
            return redirect("/")  
    return render_template("signup_page.html", user=current_user)
#search page route
@app.route("/Search", methods=["GET", "POST"])
def search():
    headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIxMTFmYWQ1NzY3ODAyZjIzZmEwZjBlMTdkNTVhZjc4NSIsIm5iZiI6MTcyMDY0OTUwMC4xMDE1NzYsInN1YiI6IjY2ODQ5NDRmMzMzZjVmM2RhYTMyZmUwMCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.MeORYLjuJhfx4bmiVIGI_VLXlXBEm5Hr3q4Txo8le9s"
}
    title = request.form['search_input']
    res = requests.get(f"https://api.themoviedb.org/3/search/movie?query={title}", headers=headers)
    print(res)
    data = res.json().get("results")
    if len(data) != 0:
        return render_template("search.html", data=data, title=title, user=current_user)
    else:
        return render_template("notfound.html", user=current_user)
#logout page route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")
#favorites page route
@app.route("/favorites", methods=["GET", "POST"])
@login_required
def favorites_func():
    user_favorites = Favorite.query.filter_by(user_id=current_user.id)
    return render_template("favorites.html", user=current_user, user_favorites=user_favorites)
#delete function
@app.route("/delete/<id>", methods=["GET", "POST"])
def delete_func(id):
    test = Favorite.query.filter_by(movie_id=id).first()
    db.session.delete(test)
    db.session.commit()
    flash("movie deleted successfully", category="success")
    return (redirect(url_for("favorites_func")))

if __name__ == "__main__":
    create_db(app)
    app.run(debug=True) 
    