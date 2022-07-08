from flask import Flask, redirect
from mainmain import api
from models import TRACKER, db
from flask import url_for
import os
from flask import render_template,request
from models import USER,TRACKER,TRACKER_LOGS,INTERMEDIATE,INTERMEDIATE_TRACKER
import matplotlib.pyplot as plt

from datetime import datetime
import humanize

app=Flask(__name__)

current_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///"+os.path.join(current_dir,"project.sqlite3")
api.init_app(app)
db.init_app(app)

############################################################################################################################

@app.route("/",methods=["GET","POST"])
def index():
    if request.method == "GET":
        return render_template('login.html')
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        got_it = USER.query.filter_by(user_name=username).first()
        print(got_it)
        message=''
        if got_it==None:
            message="Username does not exits!! Please Sign Up."
            return render_template('signup.html',message=message)
        else:
            if got_it.user_password == password:
                user_id=got_it.user_id
                return redirect(url_for('dashboard', userid=user_id))
            else:
                message="Wrong password. Please login with correct details."
                return render_template('login.html',message=message)
        
@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        new_user = USER(user_name=username,user_email=email,user_password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/")

@app.route("/dashboard/<int:userid>",methods=["GET","POST"])
def dashboard(userid):
    trackers=[]

    user = USER.query.filter_by(user_id=userid).first()
    inter = INTERMEDIATE.query.filter_by(user_id=userid).all()
    for i in inter:
        tracker=TRACKER.query.filter_by(id=i.tracker_id).first()
        trackers.append(tracker)

    timestamp=[]
    for i in trackers:
        inter_log = INTERMEDIATE_TRACKER.query.filter_by(tracker_id=i.id).all()
        print(inter_log)
        if len(inter_log)==0:
            timestamp.append("No logs")
        else:
            tracker_log = TRACKER_LOGS.query.filter_by(tracker_log_id=inter_log[-1].tracker_log_id).first()
            timestamp.append(tracker_log.timestamp)
    
    length= len(trackers)

    return render_template("dashboard.html",trackers=trackers,userid=userid,username=user.user_name,timestamp=timestamp,length=length)

#########################################################################################################################################

L=[]
@app.route("/add_tracker/<int:userid>",methods=["GET","POST"])
def add_trackers(userid):
    if request.method == "GET":
        return render_template('add_tracker.html',userid=userid)
    elif request.method == "POST":
        tracker_name = request.form.get("trackername")
        tracker_description = request.form.get("trackerdescription")
        tracker_type = request.form.get("trackertype")
        settings = request.form.get("settings")
        new_tracker = TRACKER(tracker_name=tracker_name,tracker_description=tracker_description,tracker_type=tracker_type,settings=settings)
        db.session.add(new_tracker)
        db.session.commit()
       
        new_intermediate = INTERMEDIATE(user_id=userid,tracker_id=new_tracker.id)
        db.session.add(new_intermediate)
        db.session.commit()
        return redirect(url_for('dashboard', userid=userid))

@app.route("/details/<trackerid>/<userid>",methods=["GET","POST"])
def details_tracker(trackerid,userid):
    tracker_logs_list=[]
    values=[]
    timestamps=[]
    user = USER.query.filter_by(user_id=userid).first()
    tracker = TRACKER.query.filter_by(id=trackerid).first()
    intermediate_logs = INTERMEDIATE_TRACKER.query.filter_by(tracker_id=trackerid).all()
    for i in intermediate_logs:
        tracker_logs = TRACKER_LOGS.query.filter_by(tracker_log_id=i.tracker_log_id).first()
        tracker_logs_list.append(tracker_logs)
    for j in tracker_logs_list:
        values.append(j.values)
        timestamps.append(j.timestamp)
    bar = plt.figure()
    plt.bar(timestamps,values,color = 'orange',width = 0.25)
    plt.ylabel('Values')
    plt.xlabel('Timestamp')
    bar.savefig('static/bargraph.png')
    plot = plt.figure()
    plt.plot(timestamps,values)
    plt.ylabel('Values')
    plt.xlabel('Timestamp')
    plot.savefig('static/plot.png')
    return render_template("tracker_details.html",tracker=tracker,tracker_logs_list=tracker_logs_list,user=user)

@app.route("/edit/<int:trackerid>",methods=["GET","POST"])
def edit_tracker(trackerid):
    inter = INTERMEDIATE.query.filter_by(tracker_id=trackerid).all()
    tracker = TRACKER.query.filter_by(id=trackerid).first()
    if request.method == "GET":
        return render_template("edit_tracker.html",tracker=tracker,trackerid=trackerid)
    elif request.method == "POST":
        tracker_name = request.form.get("trackername")
        tracker_description = request.form.get("trackerdescription")
        settings = request.form.get("settings")
        tracker.tracker_name = tracker_name
        db.session.commit()
        tracker.tracker_description = tracker_description
        db.session.commit()
        tracker.settings = settings
        db.session.commit()
        return redirect(url_for('dashboard', userid=inter[0].user_id))

@app.route("/delete/<int:trackerid>",methods=["GET","POST"])
def delete_tracker(trackerid):
    inter = INTERMEDIATE.query.filter_by(tracker_id=trackerid).all()
    for i in inter:
        db.session.delete(i)
        db.session.commit()
    tracker = TRACKER.query.filter_by(id=trackerid).first()


    intermediate_logs = INTERMEDIATE_TRACKER.query.filter_by(tracker_id=trackerid).all()
    
    if len(intermediate_logs)!=0:
        for i in intermediate_logs:
            logs= TRACKER_LOGS.query.filter_by(tracker_log_id=i.tracker_log_id).all()
            if len(logs)!=0:
                for j in logs:
                    db.session.delete(j)
                    db.session.commit()
            db.session.delete(i)
            db.session.commit()

    db.session.delete(tracker)
    db.session.commit()
    return redirect(url_for('dashboard', userid=inter[0].user_id))

################################################################################################################################


@app.route("/log/<int:trackerid>",methods=["GET","POST"])
def add_log(trackerid):
    tracker = TRACKER.query.filter_by(id=trackerid).first()
    inter = INTERMEDIATE.query.filter_by(tracker_id=trackerid).all()
    L=tracker.settings.split(",")
    if request.method == "GET":
        return render_template("add_log.html",tracker=tracker,trackerid=trackerid,L=L)
    elif request.method == "POST":
        value = request.form.get("value")
        note = request.form.get("note")
        time_duration = request.form.get("time_duration")
        timestamp = str(datetime.now())

        new_tracker_log = TRACKER_LOGS(values=value,note=note,time_duration=time_duration,timestamp=timestamp)
        db.session.add(new_tracker_log)
        db.session.commit()
        new_intermediate_log = INTERMEDIATE_TRACKER(tracker_log_id=new_tracker_log.tracker_log_id,tracker_id=trackerid)
        db.session.add(new_intermediate_log)
        db.session.commit()
        return redirect(url_for('dashboard', userid=inter[0].user_id))


@app.route("/editlog/<int:tracker_log_id>",methods=["GET","POST"])
def edit_log(tracker_log_id):
    tracker_log = TRACKER_LOGS.query.filter_by(tracker_log_id=tracker_log_id).first()
    inter_log = INTERMEDIATE_TRACKER.query.filter_by(tracker_log_id=tracker_log_id).first()
    inter = INTERMEDIATE.query.filter_by(tracker_id=inter_log.tracker_id).first()
    tracker = TRACKER.query.filter_by(id=inter_log.tracker_id).first()
    L=tracker.settings.split(",")
    if request.method == "GET":
        return render_template("edit_log.html",tracker_log=tracker_log,tracker_log_id=tracker_log_id,L=L,tracker=tracker)
    elif request.method == "POST":
        value = request.form.get("value")
        note = request.form.get("note")
        time_duration = request.form.get("time_duration")
        timestamp = request.form.get("timestamp")
        tracker_log.values = value
        db.session.commit()
        tracker_log.note = note
        db.session.commit()
        tracker_log.time_duration = time_duration
        db.session.commit()
        tracker_log.timestamp = str(datetime.now())
        db.session.commit()
        return redirect(url_for('details_tracker', trackerid=inter_log.tracker_id,userid=inter.user_id))

@app.route("/deletelog/<int:tracker_log_id>",methods=["GET","POST"])
def delete_log(tracker_log_id):
    tracker_log = TRACKER_LOGS.query.filter_by(tracker_log_id=tracker_log_id).first()
    inter_log = INTERMEDIATE_TRACKER.query.filter_by(tracker_log_id=tracker_log_id).all()
    inter = INTERMEDIATE.query.filter_by(tracker_id=inter_log[0].tracker_id).first()
    for i in inter_log:
        db.session.delete(i)
        db.session.commit()
    db.session.delete(tracker_log)
    db.session.commit()
    return redirect(url_for('details_tracker', trackerid=inter_log[0].tracker_id,userid=inter.user_id))

#######################################################################################################################################################################################

@app.route("/logout/<int:user_id>",methods=["GET","POST"])
def logout(user_id):
    message = "Successfully logged out"
    return render_template('login.html',message=message)


############## validations ################
############## api ###################



if __name__=="__main__":
    app.debug=True
    app.run() 