from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Никнейм', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    username = StringField('Никннейм', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class ChatForm(FlaskForm):
    name = StringField('Название статьи', validators=[DataRequired(), Length(max=50)])
    article = TextAreaField('Содержимое', validators=[DataRequired(), Length(min=1, max=10000)])
    submit = SubmitField('Выпустить статью')

class MessageForm(FlaskForm):
    content = TextAreaField('Введите сообщение', validators=[DataRequired(), Length(min=1, max=5000)])
    submit = SubmitField('Отправить коментарий')

class DeleteChatForm(FlaskForm):
    chat_id = StringField('ID статьи', validators=[DataRequired()])
    check = BooleanField('Подтвердите что вы хотите удалить статью', validators=[DataRequired()])
    submit = SubmitField('Удалить')

class BanUser(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('BAN!')

class Pre(FlaskForm):
    check = BooleanField('Нажмите если хотите чтоб статья вышла')
    submit = SubmitField('Отправить')