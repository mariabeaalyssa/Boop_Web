from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, PasswordField, BooleanField, RadioField, SelectField, SelectMultipleField, SubmitField, MultipleFileField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, InputRequired, Length, Email, NumberRange, EqualTo, ValidationError
from app.services import Auth, User

class SignupPartOneForm(FlaskForm):
    firstName_input = StringField("First Name", validators=[DataRequired(), Length(min=2, max=50)])
    lastName_input = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=50)])
    email_input = StringField("Email", validators=[DataRequired(), Email()])
    username_input = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])

    verify_identification_input = SubmitField("Continue")

    def validate_email_input(self, email_input):
        email_resp = Auth.verify_email(email_input.data)

        if email_resp["status"] == "success":
            raise ValidationError("This email address has already been taken.")

    def validate_username_input(self, username_input):
        username_resp = Auth.verify_username(username_input.data)
        
        if username_resp["status"] == "success":
            raise ValidationError("This username has already been taken.")

class SignupPartTwoForm(FlaskForm):
    contactNo_input = StringField("Contact Number", validators=[DataRequired(), Length(min=2, max=50)])
    password_input = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=50)])
    confirmPassword_input = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password_input", message="Field must be equal to password.")])

    signup_submit_input = SubmitField("Sign up")

class LoginForm(FlaskForm):
    usernameOrEmail_input = StringField("Username or Email Address", validators=[DataRequired()])
    password_input = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=50)])
    remember_input = BooleanField("Remember Password")
    
    login_submit_input = SubmitField("Log in")

class UpdateUserForm(FlaskForm):
    firstName_input = StringField("First Name", validators=[DataRequired(), Length(min=2, max=50)])
    lastName_input = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=50)])
    email_input = StringField("Email", validators=[DataRequired(), Email()])
    username_input = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    contactNo_input = StringField("Contact Number", validators=[DataRequired(), Length(min=2, max=50)])
    user_profPhoto_input = FileField("User Profile Picture", validators=[FileAllowed(["jpg", "png"])])
    user_coverPhoto_input = FileField("User Cover Picture", validators=[FileAllowed(["jpg", "png"])])

    updateUser_submit_input = SubmitField("Update")

    def validate_email_input(self, email_input):
        current_user = User.get_current_user()
        email_resp = Auth.verify_email(email_input.data)

        if email_resp["status"] == "success" and current_user["email"] != email_input.data:
            print("NGANO EMAIL")
            raise ValidationError("This email address has already been taken.")
        else:
            print("EMAIL AKOA NA")

    def validate_username_input(self, username_input):
        current_user = User.get_current_user()
        username_resp = Auth.verify_username(username_input.data)
        
        if username_resp["status"] == "success" and current_user["username"] != username_input.data:
            print("NGANO USERNAME")
            raise ValidationError("This username has already been taken.")

class AddPetForm(FlaskForm):
    petName_input = StringField("Pet Name", validators=[DataRequired(), Length(min=2, max=80)])
    bio_input = StringField("Pet Bio", validators=[Length(min=2, max=200)])
    birthday_input = DateField("Pet Birthday", format="%Y-%m-%d")
    sex_input = RadioField("Sex", coerce=str, choices=[("Male", "Male"), ("Female", "Female")], validators=[InputRequired()])
    specie_input = SelectField("Specie", coerce=str, choices=[], validators=[InputRequired()])
    breed_input = SelectField("Breed", coerce=str, choices=[], validators=[InputRequired()])
    pet_profPic_input = FileField("Pet Profile Picture", validators=[FileAllowed(["jpg", "png"])])
    pet_coverPic_input = FileField("Pet Cover Picture", validators=[FileAllowed(["jpg", "png"])])

    addPet_submit_input = SubmitField("Add pet")

class UpdatePetForm(FlaskForm):
    petName_input = StringField("Pet Name", validators=[DataRequired(), Length(min=2, max=80)])
    bio_input = StringField("Pet Bio", validators=[Length(min=2, max=200)])
    birthday_input = DateField("Pet Birthday", format="%Y-%m-%d")
    sex_input = RadioField("Sex", coerce=str, choices=[("Male", "Male"), ("Female", "Female")], validators=[InputRequired()])
    specie_input = SelectField("Specie", coerce=str, choices=[], validators=[InputRequired()])
    breed_input = SelectField("Breed", coerce=str, choices=[], validators=[InputRequired()])
    pet_profPic_input = FileField("Pet Profile Picture", validators=[FileAllowed(["jpg", "png"])])

    updatePet_submit_input = SubmitField("Update pet")

class ShareContentForm(FlaskForm):
    shareContent_input = StringField("Story Content", validators=[DataRequired(), Length(min=1, max=150)])
    shareGallery_input = MultipleFileField("Story Gallery", validators=[FileAllowed(["jpg", "png"])])

    shareContent_submit_input = SubmitField("Post story")

class CommentPostForm(FlaskForm):
    commentPost_input = StringField("Comment..", validators=[DataRequired(), Length(min=1, max=150)])

    commentPost_submit_input = SubmitField("Comment Post")

class DealPetForm(FlaskForm):
    pricePet_input = StringField("Price", validators=[DataRequired(), Length(min=1, max=150)])

    dealPet_submit_input = SubmitField("Submit")