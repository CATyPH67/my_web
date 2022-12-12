from app_config import app, db
from models import *
# from forms import CategoryForm, NewsForm
from datetime import datetime

from flask import request, render_template, redirect, url_for, flash

from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from sqlalchemy import desc, func

# flask-login

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        if request.form['cmd'] == 'Войти':
            u = db.session.query(User). \
                filter(User.login == request.form['login']). \
                filter(User.password == request.form['password']). \
                one_or_none()
            if u is None:
                flash("Неверное имя пользователя или пароль")
            else:
                login_user(u)
                return redirect(url_for('index'))

    return render_template('login.html')


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter(User.user_id == int(user_id)).one_or_none()


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form['nickname']) > 4 and len(request.form['login']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            if db.session.query(User).filter(User.login == request.form['login']).count() == 0:
                u = User(login=request.form['login'], password=request.form['psw'], nickname=request.form['nickname'])
                db.session.add(u)
                db.session.commit()
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")

    return render_template("register.html")


@app.route('/')
def index():
    return render_template(
        'index.html'
    )


@app.route('/note/<int:id>', methods=["POST", "GET"])
def note(id):
    note = db.session.query(Note).filter(Note.note_id == id).one_or_none()
    if note is None:
        return 'Not Found', 404

    user = note.user
    types = note.type
    genres = note.genre

    if request.method == "POST":
        if request.form['delete'] == 'Удалить запись':
            for type in types:
                note.type.remove(type)

            for genre in genres:
                note.genre.remove(genre)

            db.session.delete(note)
            db.session.commit()

            return redirect(url_for('user_note_search', page_num=1))

    return render_template(
        "note.html",
        note=note,
        user=user,
        genres=genres,
        types=types,
        id=str(id)
    )


@app.route('/user_note_search/<int:page_num>')
@login_required
def user_note_search(page_num):
    user_notes_search = db.session.query(Note).filter(current_user.user_id == Note.user_id).\
        paginate(per_page=5, page=page_num, error_out=True)
    return render_template('user_note_search.html', notes=user_notes_search)


@app.route('/create_note', methods=['GET', 'POST'])
@login_required
def create_note():
    types = db.session.query(Type).all()
    genres = db.session.query(Genre).all()
    if request.method == "POST":
        user_id = current_user.user_id
        name = request.form['name']
        open = False if request.form.get('private') else True
        date = datetime.now()
        score = request.form['score']
        text = request.form['text']

        note = Note(user_id=user_id, name=name, open=open, date=date, score=score, text=text)
        db.session.add(note)

        selected_types = request.form.getlist('types')
        for type_id in selected_types:
            type = db.session.query(Type).filter(Type.type_id == type_id).one_or_none()
            note.type.append(type)

        selected_genres = request.form.getlist('genres')
        for genre_id in selected_genres:
            genre = db.session.query(Genre).filter(Genre.genre_id == genre_id).one_or_none()
            note.genre.append(genre)

        db.session.commit()
        flash("Успешно создана", "success")
        return redirect(url_for('note', id=note.note_id))

    return render_template("create_note.html", types=types, genres=genres)


@app.route('/edit_note/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_note(id):
    note = db.session.query(Note).filter(Note.note_id == id).one_or_none()
    if note is None:
        return 'Not Found', 404

    cur_types = note.type
    cur_genres = note.genre

    types = db.session.query(Type).all()
    genres = db.session.query(Genre).all()

    add_types = [type for type in types if type not in cur_types]
    add_genres = [genre for genre in genres if genre not in cur_genres]

    if request.method == "POST":
        note.name = request.form['name']
        note.open = False if request.form.get('private') else True
        note.date = datetime.now()
        note.score = request.form['score']
        note.text = request.form['text']

        del_types = request.form.getlist('del_types')
        for type_id in del_types:
            type = db.session.query(Type).filter(Type.type_id == type_id).one_or_none()
            note.type.remove(type)

        del_genres = request.form.getlist('del_genres')
        for genre_id in del_genres:
            genre = db.session.query(Genre).filter(Genre.genre_id == genre_id).one_or_none()
            note.genre.remove(genre)

        add_types = request.form.getlist('add_types')
        for type_id in add_types:
            type = db.session.query(Type).filter(Type.type_id == type_id).one_or_none()
            note.type.append(type)

        add_genres = request.form.getlist('add_genres')
        for genre_id in add_genres:
            genre = db.session.query(Genre).filter(Genre.genre_id == genre_id).one_or_none()
            note.genre.append(genre)

        db.session.commit()
        flash("Успешно отредактирована", "success")
        return redirect(url_for('note', id=id))

    return render_template(
        "edit_note.html",
        note=note,
        del_types=cur_types,
        add_types=add_types,
        del_genres=cur_genres,
        add_genres=add_genres,
        id=id
    )


@app.route('/note_search/<int:page_num>')
@app.route('/note_search/<int:page_num>/<sort_key>')
def note_search(page_num, sort_key='name'):
    if current_user and current_user.is_authenticated:
        notes_search = db.session.query(Note).filter(Note.open == bool(True), current_user.user_id != Note.user_id).\
            order_by().paginate(per_page=5, page=page_num, error_out=True)
    else:
        notes_search = db.session.query(Note).filter(Note.open == bool(True)).paginate(per_page=5, page=page_num, error_out=True)
    return render_template('note_search.html', notes=notes_search)


if __name__ == '__main__':
    # Create scheme if not exists
    db.create_all()
    # if db.session.query(User).count() == 0:
    #     u = User(user_login='admin', user_name='admin', user_password='admin')
    #     db.session.add(u)
    #     db.session.commit()
    # SHOW SQL LOG
    # app.config['SQLALCHEMY_ECHO'] = True
    app.run(debug=True)
