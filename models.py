from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class USER(db.Model):
    __tablename__="user"
    user_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    user_name = db.Column(db.String,nullable=False)
    user_email = db.Column(db.String,unique=True)
    user_password = db.Column(db.String,nullable=False,unique=True)
    #tracker_log=db.relationship("TRACKER_LOGS",secondary="tracker")

class TRACKER(db.Model):
    __tablename__="tracker"
    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    tracker_name = db.Column(db.String,nullable=False)
    tracker_description = db.Column(db.String)
    tracker_type = db.Column(db.String)
    settings = db.Column(db.String)


class TRACKER_LOGS(db.Model):
    __tablename__="tracker_logs"
    tracker_log_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    values = db.Column(db.String,nullable=False)
    time_duration = db.Column(db.String)
    timestamp = db.Column(db.String)
    note = db.Column(db.String)
    #user=db.relationship("USER",secondary="tracker")

class INTERMEDIATE(db.Model):
    __tablename__="intermediate"
    intermediate_id = db.Column(db.Integer,autoincrement=True,primary_key=True,nullable=False)
    user_id = db.Column(db.String,db.ForeignKey("user.user_id"),primary_key=True)
    tracker_id = db.Column(db.String,db.ForeignKey("tracker.id"),primary_key=True)

class INTERMEDIATE_TRACKER(db.Model):
    __tablename__="intermediate_tracker"
    intermediate_tracker_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    tracker_log_id = db.Column(db.String,db.ForeignKey("tracker_logs.tracker_log_id"),primary_key=True)
    tracker_id = db.Column(db.String,db.ForeignKey("tracker.id"),primary_key=True)
