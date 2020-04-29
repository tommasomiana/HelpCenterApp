from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.validators import InputRequired, regexp
from flask_wtf.file import FileRequired

class ChatForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    message = TextAreaField('message', validators=[InputRequired()])
    submit = SubmitField('submit')

class ImageForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    image = FileField('Image File', validators=[FileRequired('File was empty!')])
    submit = SubmitField('submit')