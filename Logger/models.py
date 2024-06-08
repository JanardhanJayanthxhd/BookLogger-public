from Logger import db, login_manager
from flask_login import UserMixin
from sqlalchemy.orm import relationship


@login_manager.user_loader
def user_loader(user):
    return Users.query.filter_by(id=user).first()


class Users(UserMixin, db.Model):
    __tablename__ = 'UserTable'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    api_key = db.Column(db.String(33), nullable=False)
    # Relationship attribute - one to many
    books = relationship("Books", back_populates="owner")

    @staticmethod
    def check_existing_key(key):
        """checks if api key already exists : 0(1) if the db works based on indexing"""
        return Users.query.filter_by(api_key=key).first() is not None

    def __repr__(self):
        return f'user - {self.username}'


class Books(db.Model):
    __tablename__ = 'BookTable'

    book_id = db.Column(db.Integer(), primary_key=True)
    book_title = db.Column(db.String(200), nullable=False)
    book_author = db.Column(db.String(200), nullable=False)
    book_rating = db.Column(db.Integer(), nullable=False)
    # foreign key
    owner_id = db.Column(db.Integer(), db.ForeignKey(Users.id))
    # Inverse the relationship(many to one) created in Users table
    owner = relationship("Users", back_populates="books")

    def to_dict(self, book_id=None) -> dict:
        dictionary = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return dictionary

    def __repr__(self):
        return f'book - {self.book_title}'

# # to create database
# db.create_all()
