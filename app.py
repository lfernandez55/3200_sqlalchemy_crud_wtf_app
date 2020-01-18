from flask import Flask, render_template
#, render_template_string, render_template, redirect, url_for, request,
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)


# Define the Role data-model
class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    age = db.Column(db.Integer())
    student_nick_names = db.relationship("StudentNickName", backref='student')

    def __repr__(self):
        string_object = self.name  + "end_of_object"
        return string_object

# Define the UserRoles association table
class StudentNickName(db.Model):
    __tablename__ = 'student_nick_name'
    id = db.Column(db.Integer(), primary_key=True)
    nick_name = db.Column(db.String(50), unique=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)


@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/create_all')
def create_all():
    db.create_all()
    message = "DB Created! (A SQLite DB File Should Appear In Your Project Folder.  " \
              "Also, if changes are made to the model, running this again should " \
              "add these changes to the db.)"
    return render_template('index.html', message=message)

@app.route('/drop_all')
def drop_all():
    db.drop_all()
    message = "DB Dropped!!)"
    return render_template('index.html', message=message)

@app.route('/add_student')
def add_student():
    joe = Student(name='Joe',age=21)
    # nickname_1 = StudentNickName(nick_name="Jo Jo")
    # nickname_2 = StudentNickName(nick_name="Joey")
    # joe.student_nick_names.append(nickname_1)
    # joe.student_nick_names.append(nickname_2)
    db.session.add(joe)
    db.session.commit()

    message = "Student named Joe added to DB)"
    return render_template('index.html', message=message)

@app.route('/add_nicknames_to_student')
def add_nicknames_to_student():
    joe = Student.query.filter(Student.name == 'Joe').first()
    print(joe.name)
    nickname_1 = StudentNickName(nick_name="Jo Jo")
    nickname_2 = StudentNickName(nick_name="Joey")
    joe.student_nick_names.append(nickname_1)
    joe.student_nick_names.append(nickname_2)
    db.session.add(joe)
    db.session.commit()
    message = "Two nicknames added to Joe"
    return render_template('index.html', message=message)

@app.route('/update_student')
def update_student():
    joe = Student.query.filter(Student.name == 'Joe').first()
    #TODO:  update student here
    message = "TODO UPDATE STUDENT"
    return render_template('index.html', message=message)


@app.route('/select_student')
def select_student():
    joe = Student.query.filter(Student.name == 'Joe').first()
    query_results = ""
    query_results = query_results + joe.name + " AKA: "
    for nicknames in joe.student_nick_names:
        query_results = query_results + " " + nicknames.nick_name
    message = "Query Results: " + query_results
    return render_template('index.html', message=message)