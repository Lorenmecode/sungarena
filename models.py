from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()


class user(db.Model):
    __tablename__="users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at=db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        
        return f"User {self.username}>"


       