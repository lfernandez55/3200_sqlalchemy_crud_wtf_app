# 3200_sqlalchemy_crud_app
This is an app that demos how to use WTforms to manage info in tables with one to many, and many to many relationships.  There are four forms in this app:

A WTform that creates a student record in a single Student table
A WTform that creates a student record in a Student table and in a StudentNickname (child) table
A WTform that updates a student record in a Student table and in a StudentNickname (child) table
A WTform that creates/updates the course enrollments of a student.  The Student and Course tables have a many to many relationship.

WTForms documentation can be found in the following locations:
https://wtforms.readthedocs.io/en/2.1/index.html (Version 2.1)*
https://wtforms.readthedocs.io/en/stable/index.html (Version 2.2.1)
https://wtforms.readthedocs.io/en/stable/crash_course.html (Version 2.2.1 Crash Course)
*This documents a slightly older version.  But the doc is clearer.

To run this app do the usual:
python -m venv venv
venv\scripts\activate.bat
pip install -r requirements.txt
