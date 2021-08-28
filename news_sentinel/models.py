from news_sentinel import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# classes for db - will separate them later
class User(db.Model, UserMixin):
    # columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # relationships
    votes = db.relationship('Vote', backref='voter', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


    def __repr__(self):
        return f"User('{self.id}, {self.username}' , '{self.email}')"


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, unique=True, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    image = db.Column(db.Text)
    date = db.Column(db.String(20), nullable=False)
    pred = db.Column(db.Integer, nullable=False)
    # relationships
    news_votes = db.relationship('Vote', backref='news_name', lazy=True)

    def __repr__(self):
        return f"User('{self.title}' , '{self.author}', '{self.image}' , '{self.date}', '{self.pred}')"


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vote = db.Column(db.Integer, nullable=False)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('news_id', 'user_id', name='_news_user_uc'),)

    def __repr__(self):
        return f"Vote('{self.vote}' , '{self.news_id}', '{self.user_id}')"
