from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from flask_wtf import Form, FlaskForm
from wtforms import StringField, IntegerField, ValidationError, FieldList, FormField, SubmitField
from wtforms.validators import InputRequired

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)


# Define the Role data-model
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    # Define the relationship to Student via StudentCourses
    students = db.relationship('Student', secondary='student_courses')

    def __str__(self):

        students = "["
        for stud in self.students:
            students = students + stud.name + ','
        students = students + "]"
        string_object = str(self.id) + "|" + str(self.name) +"|" + students
        return string_object

# Define the UserRoles association table
class StudentCourses(db.Model):
    __tablename__ = 'student_courses'
    id = db.Column(db.Integer(), primary_key=True)
    course_id = db.Column(db.Integer(), db.ForeignKey('courses.id', ondelete='CASCADE'))
    student_id = db.Column(db.Integer(), db.ForeignKey('student.id', ondelete='CASCADE'))

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), )
    email = db.Column(db.String(50), unique=True)
    age = db.Column(db.Integer())
    student_nick_names = db.relationship("StudentNickName", backref='student', cascade='all')

    # Define the relationship to Course via StudentCourses
    courses = db.relationship('Course', secondary='student_courses')

    def __str__(self):

        nick_names = "["
        for nick in self.student_nick_names:
            nick_names = nick_names + nick.nick_name + ','
        nick_names = nick_names + "]"
        courses = "["
        for course in self.courses:
            courses = courses + course.name + ','
        courses = courses + "]"
        string_object = str(self.id) + "|" + str(self.name) +"|" + str(self.email) + "|" + str(self.age) + "|" + nick_names + "|" + courses
        return string_object

# Define the UserRoles association table
class StudentNickName(db.Model):
    __tablename__ = 'student_nick_name'
    id = db.Column(db.Integer(), primary_key=True)
    nick_name = db.Column(db.String(50))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'))

    def __str__(self):
        string_object = nick_name
        return string_object

#Forms Section

class StudentNickNameForm(Form):
    id = IntegerField('id')
    nick_name = StringField('nick_name', validators=[InputRequired()])
    class Meta:
        # No need for csrf token in this child form
        csrf = False

def email_at_check(form, field):
    if '@' not in field.data:
        raise ValidationError('Email must contain an @')
def email_unique(form, field):
    stud = Student.query.filter(Student.email == field.data).first()
    print('zzzzzz',stud)
    if stud is not None:
        raise ValidationError('Not a unique email address')

class StudentForm(Form):
    id = IntegerField('id')
    name = StringField('name', validators=[InputRequired()])
    email = StringField('email', validators=[InputRequired(), email_at_check, email_unique])
    age = IntegerField('age', validators=[InputRequired()])
    # student_nick_names = StringField('student_nick_names', validators=[InputRequired()])
    student_nick_names = FieldList(FormField(StudentNickNameForm), label='Nicknames', min_entries=1)
    add_nickname = SubmitField(label='Add More Nicknames')

    submit = SubmitField()


# https://stackoverflow.com/questions/49066046/append-entry-to-fieldlist-with-flask-wtforms-using-ajax
class ChildForm(FlaskForm):

    name = StringField(label='Name child')
    age = IntegerField(label='Age child')

    class Meta:
        # No need for csrf token in this child form
        csrf = False

class ParentForm(FlaskForm):

    name = StringField(label='Name parent')
    children = FieldList(FormField(ChildForm), label='Children')
    add_child = SubmitField(label='Add child')

    submit = SubmitField()


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

@app.route('/add_students', methods={'GET','POST'})
def add_students():
    form = StudentForm()
    if form.validate_on_submit():
        print("dddddddd", form.name, form.email, form.age)
        studObj = Student(name=form.name.data, email=form.email.data, age=form.age.data)
        # studObj.name = form.name
        # studObj.email = form.email
        # studObj.age = 44
        db.session.add(studObj)
        db.session.commit()
        return 'Form Successfully Submitted!'
    return render_template('addStudent.html', form=form)

    # joe = Student(name='Joe',email="joe@weber.edu",age=21)
    # db.session.add(joe)
    # db.session.commit()
    #
    # mary = Student(name='Mary', email="mary@weber.edu", age=22)
    # nickname_1 = StudentNickName(nick_name="Maria")
    # mary.student_nick_names.append(nickname_1)
    # db.session.add(mary)
    # db.session.commit()
    #
    #
    # message = "Student named Joe and Mary added to DB)"
    # return render_template('index.html', message=message)

@app.route('/add_students_with_nn_option', methods={'GET','POST'})
def add_students_with_nn_option():
    form = StudentForm()

    if form.add_nickname.data:
        form.student_nick_names.append_entry()
        return render_template('add_stud_w_nn.html', form=form)
    if form.validate_on_submit():
        print("dddddddd", form.name, form.email, form.age, form.student_nick_names.data)
        studObj = Student(name=form.name.data, email=form.email.data, age=form.age.data)
        for nickname in form.student_nick_names.data:
            print('XXXXXXXXXXXXXXXXXXXX:', nickname['nick_name'], type(nickname['nick_name']))
            nicknameObj = StudentNickName(nick_name=nickname['nick_name'])
            # mary.student_nick_names.append(nickname_1)
            studObj.student_nick_names.append(nicknameObj)
        # studObj.name = form.name
        # studObj.email = form.email
        # studObj.age = 44
        db.session.add(studObj)
        db.session.commit()
        flash('Student Added!!')
        # return 'Form Successfully Submitted!'
        return redirect(url_for('home_page'))
    return render_template('add_stud_w_nn.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = ParentForm()

    if form.add_child.data:
        form.children.append_entry()
        return render_template('register.html', form=form)

    if form.validate_on_submit():
        return "Yabba dabba do!!!!"

    return render_template('register.html', form=form)

@app.route('/add_nicknames_to_student')
def add_nicknames_to_student():
    joe = Student.query.filter(Student.email == 'joe@weber.edu').first()
    print(joe.name)
    nickname_1 = StudentNickName(nick_name="Jojo")
    nickname_2 = StudentNickName(nick_name="Joey")
    joe.student_nick_names.append(nickname_1)
    joe.student_nick_names.append(nickname_2)
    db.session.add(joe)
    db.session.commit()
    message = "Two nicknames added to Joe"
    return render_template('index.html', message=message)

@app.route('/update_student')
def update_student():
    joe = Student.query.filter(Student.email == 'joe@weber.edu').first()
    joe.name = 'Joseph'
    db.session.add(joe)
    db.session.commit()
    message = "Student Updated"
    return render_template('index.html', message=message)


@app.route('/select_student')
def select_student():
    joe = Student.query.filter(Student.email == 'joe@weber.edu').first()
    message = "Query Results:<br> " + str(joe)
    return render_template('index.html', message=message)

@app.route('/select_students')
def select_students():
    students = Student.query.all()
    query_results = ""
    for stud in students:
        query_results = query_results + str(stud) + "<br>"

    message = "Query Results: <br>" + query_results
    return render_template('index.html', message=message)

@app.route('/delete_student')
def delete_student():
    joe = Student.query.filter(Student.email == 'joe@weber.edu').first()
    db.session.delete(joe)
    db.session.commit()
    message = "Joe deleted from DB"
    return render_template('index.html', message=message)

@app.route('/add_courses')
def add_courses():
    course1 = Course(name="Anthro 1000")
    db.session.add(course1)
    course2 = Course(name="English 1100")
    db.session.add(course2)

    db.session.commit()
    message = "Two courses added to DB"
    return render_template('index.html', message=message)

@app.route('/enroll_students')
def enroll_students():
    anthro = Course.query.filter(Course.name == 'Anthro 1000').first()
    english = Course.query.filter(Course.name == 'English 1100').first()
    joe = Student.query.filter(Student.email == 'joe@weber.edu').first()
    mary = Student.query.filter(Student.email == 'mary@weber.edu').first()
    anthro.students.append(joe)
    english.students.append(joe)
    anthro.students.append(mary)
    db.session.add(anthro)
    db.session.add(english)

    db.session.commit()
    message = "Two courses added to DB"
    return render_template('index.html', message=message)


@app.route('/show_course_enrollments')
def show_course_enrollments():
    anthro = Course.query.filter(Course.name == 'Anthro 1000').first()
    english = Course.query.filter(Course.name == 'English 1100').first()

    message = "Course Enrollments:<br>" + str(anthro) + "<br>" + str(english)
    return render_template('index.html', message=message)

@app.route('/show_student_enrollments')
def show_student_enrollments():
    joe = Student.query.filter(Student.email == 'joe@weber.edu').first()
    if joe is None:
        print('none type object')
    else:
        print('Not none')
    courses = ""
    for course in joe.courses:
        courses = courses + str(course.name) +  ","
    message = "Joe is enrolled in:<br> " + courses
    return render_template('index.html', message=message)