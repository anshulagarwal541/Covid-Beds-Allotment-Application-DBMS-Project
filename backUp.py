from flask import Flask, render_template, request, redirect, url_for, session
# To return a html page whenever route is called
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, Integer, String, func
from datetime import datetime

app = Flask(__name__)
app.secret_key = "#nmit123"


app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:rachit12@localhost/dbmsproject"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Creating tables
hospitalRows = [
    {"hid": "hbang1", "hname": "Bangalore Unix Hospital",
        "address": "56 late street, Bangalore"},
    {"hid": "hmadh2", "hname": "Madhya Pradesh Cancer Hospital",
        "address": "1 Saint George street, Madhya Pradesh - 200263"},
    {"hid": "hup3", "hname": "Lucknow Central Hospital",
        "address": "63 lal bahadur marg, George Town, Lucknow"},
    {"hid": "hmum4", "hname": "Tata Memorial Hospital",
        "address": "5th atreet of shastri marg, mumbai"},
    {"hid": "hguj5", "hname": "Gujarat Central Hospital",
        "address": "71st chorah jesus marg, gujarat"},
    {"hid": "hbang6", "hname": "Shusrusa Hospital",
        "address": "9th bahadur street near GHS, Bangalore, Karnataka"},
    {"hid": "hup7", "hname": "Central Railway Hospital",
        "address": "29th lane of ravi narayan road lane, Allahabad, Uttar Pradesh"},
    {"hid": "hup8", "hname": "Army Central Hospital",
        "address": "12th lane of gandhi road, Allahabad, Uttar Pradesh"},
]

bedRows = [
    {"hid": "hbang1", "totalBeds": 289, "bedsAvailable": 289, "costperbed": 1837},
    {"hid": "hmadh2", "totalBeds": 549, "bedsAvailable": 549, "costperbed": 3832},
    {"hid": "hup3", "totalBeds": 162, "bedsAvailable": 162, "costperbed": 2634},
    {"hid": "hmum4", "totalBeds": 534, "bedsAvailable": 534, "costperbed": 6583},
    {"hid": "hguj5", "totalBeds": 1035, "bedsAvailable": 1035, "costperbed": 6453},
    {"hid": "hbang6", "totalBeds": 856, "bedsAvailable": 856, "costperbed": 4342},
    {"hid": "hup7", "totalBeds": 766, "bedsAvailable": 766, "costperbed": 837},
    {"hid": "hup8", "totalBeds": 946, "bedsAvailable": 946, "costperbed": 637}
]


class Home(db.Model):
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    uid = db.Column(db.String(20), nullable=False,
                    primary_key=True, index=True)
   # What things need
    costs = db.relationship('Costs', backref='home_costs', lazy=True)

    def __repr__(self) -> str:
        return f"{self.username} - {self.password} - {self.uid}"


# @event.listens_for(Home, 'after_insert')
# def after_home_insert(mapper, connection, target):
#     target.uid = str(target.sno)
#     # Commit the changes after generating the uid


class Hospitals(db.Model):
    hid = db.Column(db.String(20), primary_key=True,
                    index=True, nullable=False)
    hname = db.Column(db.String(50), nullable=False)
    haddress = db.Column(db.String(100), nullable=False)

    # Add a relationship to the Beds table
    beds = db.relationship('Beds', backref='hospital', lazy=True)
    costs = db.relationship('Costs', backref='hospital', lazy=True)
    # What things need

    def __repr__(self) -> str:
        return f"{self.hid} - {self.hname} - {self.haddress}"


class Beds(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hid = db.Column(db.String(20), db.ForeignKey(
        'hospitals.hid'), nullable=False)
    totalBeds = db.Column(db.Integer, nullable=False)
    bedsAvailable = db.Column(db.Integer, nullable=False)
    costperbed = db.Column(db.Integer, nullable=False)
    # What things need

    def __repr__(self) -> str:
        return f"{self.hid} - {self.totalBeds} - {self.bedsAvailable} - {self.costperbed}"


class Costs(db.Model):
    invoiceid = db.Column(db.Integer, primary_key=True, index=True)
    uid = db.Column(db.String(20), db.ForeignKey('home.uid'), nullable=False)
    hid = db.Column(db.String(20), db.ForeignKey(
        'hospitals.hid'), nullable=False)
    hname = db.Column(db.String(50), nullable=False)
    bedsselected = db.Column(db.Integer, nullable=False)
    costperbed = db.Column(db.Integer, nullable=False)
    totalcost = db.Column(db.Integer, nullable=False)

    def __repr__(self) -> str:
        return f"{self.invoiceid} - {self.uid} - {self.hid} - {self.bedsselected} - {self.costperbed} - {self.totalcost}"

# Function to drop the tables


def drop_tables():
    with app.app_context():
        db.drop_all()

# Function to create the tables


def create_tables():
    with app.app_context():
        db.create_all()


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        uid = request.form['uid']
        h=Home.query.filter_by(uid=uid).first();
        if h:
            return render_template('uidError.html')
        else:
            session['uid'] = uid
            signup = Home(username=username, password=password, uid=uid)
            db.session.add(signup)
            db.session.commit()
    allSignUps = Home.query.all()
    return render_template('home.html', allSignUps=allSignUps)


@app.route('/hospitals', methods=['GET', 'POST'])
def hospitals():
    hospitals = Hospitals.query.all()
    return render_template('hospitals.html', hospitals=hospitals)


@app.route('/beds', methods=['GET', 'POST'])
def beds():
    if request.method == 'POST':
        hid = request.form['hid']
        hname = request.form['hname']
        h1 = Hospitals.query.filter_by(hid=hid).first()
        h2 = Hospitals.query.filter_by(hname=hname).first()
        if (h1 and h2 and h1.hname==hname):
            totalInfo = Beds.query.all()
            return render_template('beds.html', totalInfo=totalInfo, hid=hid, hname=hname)
        else:
            return render_template('errorHospital.html')
    else:
        totalInfo = Beds.query.all()
        return render_template('beds.html', totalInfo=totalInfo)


@app.route('/cost', methods=['GET', 'POST'])
def cost():
    if request.method=='POST':
        hid = request.form['hid']
        bed = Beds.query.filter_by(hid=hid).first()
        uid = request.form['uid']
        homeObject = Home.query.filter_by(uid=uid).first()
        if homeObject:
            bedsselected = request.form['bedsselected']
            hname = request.form['hname']
            costperbed = bed.costperbed
            if (int(bed.bedsAvailable) < int(bedsselected)):
                return render_template('errorBeds.html')
            else:
                bed.bedsAvailable = str(int(bed.bedsAvailable)-int(bedsselected))
                totalcost = str(int(costperbed)*int(bedsselected))
                date = datetime.today()
                cost = Costs(uid=uid, hid=hid, hname=hname, bedsselected=bedsselected,
                        costperbed=costperbed, totalcost=totalcost)
                db.session.add(cost)
                db.session.commit()
                return render_template('cost.html', uid=uid, hid=hid, bedsselected=bedsselected, costperbed=costperbed, totalcost=totalcost, date=date)
        else:
            return render_template('errorUser.html')
    else:
        return render_template('errorHandle.html')
    
    # try:

    #     print("working")
    #     uid = session.get('uid')
    #
    #     totalcost = func.cast(costperbed, Integer) * func.cast(bedsselected, Integer)
    #     totalcost = func.cast(totalcost, String)
    #     cost = Costs(
    #         uid=uid,
    #         hid=hid,
    #         bedsselected=bedsselected,
    #         costperbed=costperbed,
    #         totalcost=totalcost
    #     )
    #     db.session.add(cost)
    #     db.session.commit()
    #     return render_template('cost.html', uid=uid, hid=hid)
    # except Exception as e:
    #     print("Error:", e)
    #     return "An error occurred. Please try again later."

if __name__ == "__main__":
    with app.app_context():
        drop_tables()
        create_tables()
        for hospitalRow in hospitalRows:
            hospital = Hospitals(
                hid=hospitalRow["hid"], hname=hospitalRow["hname"], haddress=hospitalRow["address"])
            db.session.merge(hospital)
        for bedRow in bedRows:
            bed = Beds(hid=bedRow["hid"], totalBeds=bedRow["totalBeds"],
                       bedsAvailable=bedRow["bedsAvailable"], costperbed=bedRow["costperbed"])
            db.session.add(bed)
        db.session.commit()
        bedRows.clear()
    app.run(debug=True, port=1495)
