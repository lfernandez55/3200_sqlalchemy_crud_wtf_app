from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from flask_wtf import FlaskForm #Form is deprecated, use FlaskForm instead
from wtforms import StringField, IntegerField, ValidationError, FieldList, FormField, SubmitField, HiddenField, SelectMultipleField, widgets
from wtforms.validators import InputRequired

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)


# Model Section
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

class StudentNickName(db.Model):
    __tablename__ = 'student_nick_name'
    id = db.Column(db.Integer(), primary_key=True)
    nick_name = db.Column(db.String(50))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'))

    def __str__(self):
        string_object = self.nick_name
        return string_object

# Forms Section

class StudentNickNameForm(FlaskForm):
    id = IntegerField('id')
    nick_name = StringField('nick_name')
    class Meta:
        # No need for csrf token in this child form
        csrf = False

#these are custom validations that are called in the StudentForm
def email_at_check(form, field):
    if '@' not in field.data:
        raise ValidationError('Email must contain an @')
def email_unique(form, field):
    stud = Student.query.filter(Student.email == field.data).first()
    if stud is not None:
        if str(stud.id) != str(form.id.data):
            raise ValidationError('Not a unique email address')

class StudentForm(FlaskForm):
    id = HiddenField('id')
    name = StringField('name', validators=[InputRequired()])
    email = StringField('email', validators=[InputRequired(), email_at_check, email_unique])
    age = IntegerField('age', validators=[InputRequired()])
    student_nick_names = FieldList(FormField(StudentNickNameForm), label='Nicknames', min_entries=1)
    add_nickname = SubmitField(label='Add Nicknames')
    remove_nickname = SubmitField(label='Remove Last Nickname Entry')
    courses = SelectMultipleField('Enrollments', choices=[]) #we populate choices later

    submit = SubmitField()


class StudentEnrollmentForm(FlaskForm):
    id = HiddenField('id')
    name = HiddenField('name')
    email = HiddenField('email')
    age = HiddenField('age')
    courses = SelectMultipleField(label='Enrollments', coerce=int)
    submit = SubmitField()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)

# Routes section  (all routes that use WTForms are at top of this section)
@app.route('/add_students', methods={'GET','POST'})
def add_students():
    form = StudentForm()
    # the following field is not used in the form.  it has to be deleted
    # otherwise a validation error will be thrown see
    # https://wtforms.readthedocs.io/en/2.1/specific_problems.html#removing-fields-per-instance
    del form.student_nick_names
    if form.validate_on_submit():
        studObj = Student(name=form.name.data, email=form.email.data, age=form.age.data)
        db.session.add(studObj)
        db.session.commit()
        flash('Student Added!!')
        return redirect(url_for('home_page'))
    return render_template('addStudent.html', form=form)

@app.route('/add_students_with_nn_option', methods={'GET','POST'})
def add_students_with_nn_option():
    form = StudentForm()

    if form.add_nickname.data:
        form.student_nick_names.append_entry()
        return render_template('add_stud_w_nn.html', form=form)
    if form.remove_nickname.data:
        form.student_nick_names.pop_entry()
        return render_template('add_stud_w_nn.html', form=form)
    if form.validate_on_submit():
        studObj = Student(name=form.name.data, email=form.email.data, age=form.age.data)
        for nickname in form.student_nick_names.data:
            nicknameObj = StudentNickName(nick_name=nickname['nick_name'])
            studObj.student_nick_names.append(nicknameObj)
        db.session.add(studObj)
        db.session.commit()
        flash('Student Added!!')
        return redirect(url_for('home_page'))
    return render_template('add_stud_w_nn.html', form=form)

@app.route('/update_student', methods=['GET', 'POST'])
def update_student():
    studObj = Student.query.filter(Student.id == 1).first()
    form = StudentForm(id=studObj.id, name=studObj.name, email=studObj.email, age=studObj.age, student_nick_names=studObj.student_nick_names)
    if form.add_nickname.data:
        form.student_nick_names.append_entry()
        return render_template('update_student.html', form=form)
    if form.remove_nickname.data:
        form.student_nick_names.pop_entry()
        return render_template('update_student.html', form=form)
    if form.validate_on_submit():
        studObj.name=form.name.data
        studObj.email=form.email.data
        studObj.age=form.age.data
        # Begin code for *updating* studObj.student_nick_names (rather than appending to it)
        # There should be a way to update the existing children objects rather than deleting and readding them
        # But in the below we delete and re-add.  Otherwise updated children simply append to existing children list
        for i in range(len(studObj.student_nick_names)):
            db.session.delete(studObj.student_nick_names[i])
        for nickname in form.student_nick_names.data:
            nicknameObj = StudentNickName(nick_name=nickname['nick_name'])
            studObj.student_nick_names.append(nicknameObj)
        # End code for *updating*....
        db.session.add(studObj)
        db.session.commit()
        flash('Student Updated!!')
        return redirect(url_for('home_page'))
    return render_template('update_student.html', form=form)

@app.route('/enroll_students', methods=['GET', 'POST'])
def enroll_students():
    studObj = Student.query.filter(Student.id == 1).first()

    # form.courses needs to be populated with the student's current enrollments
    stud_current_enrollments = []
    for course in studObj.courses:
         stud_current_enrollments.append(str(course.id))

    form = StudentEnrollmentForm(id=studObj.id, name=studObj.name, email=studObj.email, age=studObj.age, courses=stud_current_enrollments)

    # form.courses.choices needs to be populated with the entire list of courses that the student can choose from
    coursesCollection = Course.query.all()
    courses_list = []
    for course in coursesCollection:
        courses_list.append(course.name)
    course_choices = list(enumerate(courses_list,start=1))
    form.courses.choices = course_choices

    if form.validate_on_submit():

        studObj.courses = []
        for course_id in form.courses.data:
            courseObj = Course.query.filter(Course.id == course_id).first()
            studObj.courses.append(courseObj)
        db.session.add(studObj)
        db.session.commit()
        flash('Students Enrollments Updated!!')
        return redirect(url_for('home_page'))
    return render_template('enroll_students.html', form=form)

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


@app.route('/select_students')
def select_students():
    students = Student.query.all()
    query_results = ""
    for stud in students:
        query_results = query_results + str(stud) + "<br>"

    message = "Query Results: <br>" + query_results
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

@app.route('/show_student_enrollments')
def show_student_enrollments():
    studObj = Student.query.filter(Student.id == 1).first()
    courses = ""
    for course in studObj.courses:
        courses = courses + str(course.name) +  ","
    message = "The student with id 1 is enrolled in:<br> " + courses
    return render_template('index.html', message=message)