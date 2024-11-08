from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///source.db'
db = SQLAlchemy(app)

class ThinkTank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry_name = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.Date, default=datetime.today())

    def __repr__(self):
        return '<Name %r>' % self.entry_name
    
@app.route('/', methods=['GET'])
def index():
    entries = ThinkTank.query.order_by(ThinkTank.entry_name).all()
    return render_template('index.html', entries=entries)

@app.route('/display/<int:identity>', methods=['GET'])
def display(identity):
    entry = ThinkTank.query.get_or_404(identity)
    return render_template('display.html', entry=entry)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form['name']
        content = request.form['content']
        new_entry = ThinkTank(entry_name=name, content=content)

        try:
            db.session.add(new_entry)
            db.session.commit()
            return redirect('/')
        except SQLAlchemyError as e:
            db.session.rollback()
            err_msg = str(e.__dict__['orig'])
            return f'Error: {err_msg}'
    else:
        return render_template('create.html')

@app.route('/edit/<int:identity>', methods=['GET', 'POST'])
def edit(identity):
    entry = ThinkTank.query.get_or_404(identity)
    if request.method == 'POST':
        entry.content = request.form['content']
        entry.date_created = datetime.today()

        try:
            db.session.commit()
            return redirect('/')
        except SQLAlchemyError as e:
            db.session.rollback()
            err_msg = str(e.__dict__['orig'])
            return f'Error: {err_msg}'
    else:
        return render_template('edit.html', entry=entry)
    
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_name = request.form['q']
        entries_by_name = ThinkTank.query.filter_by(entry_name=search_name).all()
        return render_template('index.html', entries=entries_by_name)
    else:
        return redirect('/')



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)