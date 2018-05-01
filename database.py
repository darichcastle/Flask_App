from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
import os
from flask_sqlalchemy import SQLAlchemy 
import unicodedata
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from tabledef import *
from sqlalchemy import exc
from sqlalchemy import update
from sqlalchemy import func
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizzes.db'
db = SQLAlchemy(app)
engine = create_engine('sqlite:///tutorial.db', echo=True)

loggedinuser="qwertyuioplkjhgfdsazxcvbnm1234567890"
id_left=0
score=0
ctr=0
lifeline=0

class Scores(db.Model):
	__tablename__ = 'scores'
	
	id=db.Column(db.Integer, primary_key=True, autoincrement=True)
	
	username = db.Column(db.String(200))
	quiz_id = db.Column(db.Integer)
	subcategory = db.Column(db.String(200))
	score_uptilnow = db.Column(db.Integer)
	attempts = db.Column(db.Integer)
	high_score = db.Column(db.Integer)
	question_left = db.Column(db.Integer)
	quizid_left = db.Column(db.Integer)
	subcategory_left = db.Column(db.String(200))
	ctr_left = db.Column(db.Integer)


@app.route('/')
def home():
	global loggedinuser
	if not session.get('logged_in'):
		return render_template('login.html')
	elif(loggedinuser=="admin"):
		return render_template("Admin_index.html")
	else:
		return render_template("Normal_index.html")
		

@app.route('/sign_up', methods=['POST'])
def do_sign_up():
	Session = sessionmaker(bind=engine)
	session = Session()
	USERNAME_NEW = str(request.form['new_username'])
	PASS_NEW = str(request.form['new_pass'])
	STATE=0
	IDLEFT=0
	FIRST=str(request.form['first'])
	LAST=str(request.form['last'])
	Session = sessionmaker(bind=engine)
	s = Session()
	obj = s.query(User).filter_by(username=USERNAME_NEW).first()
	if obj is None:
		user = User(USERNAME_NEW,PASS_NEW,STATE,IDLEFT,FIRST,LAST)
		session.add(user)
		session.commit()
		return render_template("signed_up.html")
	else:
		return render_template("username_exists.html")


@app.route('/login', methods=['POST'])
def do_admin_login():
 
	global loggedinuser
	global score
	global ctr
	POST_USERNAME = str(request.form['username'])
	POST_PASSWORD = str(request.form['password'])
	
	Session = sessionmaker(bind=engine)
	s = Session()
	query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]) )
	result = query.first()
	
	if result:
		session['logged_in'] = True
		loggedinuser=POST_USERNAME
	else:
		return render_template("wrong_password.html")
	
	obj = s.query(User).filter_by(username=loggedinuser).first()
	if(obj.staterestore==1):
		obj2=Scores.query.filter_by(id=obj.idleft).first()
		a=obj2.quizid_left
		b=obj2.subcategory_left
		c=obj2.question_left

		score=obj2.score_uptilnow
		ctr=obj2.ctr_left
		return render_template("continuepage.html", a=a,b=b,c=c)
	
	elif(POST_USERNAME=="admin"):
		return render_template("Admin_index.html")
	return home()


@app.route("/logout")
def logout():
	session['logged_in'] = False
	return home()


subids_music=[]
subids_sports=[]
subids_cinema=[]


class Quizzes(db.Model):
	__tablename__ = 'quizzes'
	
	id=db.Column(db.Integer, primary_key=True, autoincrement=True)
	
	quiz_id = db.Column(db.Integer)
	category = db.Column(db.String(200))
	sub_id = db.Column(db.Integer)
	subcategory = db.Column(db.String(200))

	question = db.Column(db.String(200))
	opt1=db.Column(db.String(200))
	opt2=db.Column(db.String(200))
	opt3=db.Column(db.String(200))
	opt4=db.Column(db.String(200))

	typeofquestion=db.Column(db.Integer)

	answer=db.Column(db.Integer)


class Subcategories(db.Model):
	__tablename__ = 'subcateg'
	
	id=db.Column(db.Integer, primary_key=True, autoincrement=True)
	
	quiz_id2 = db.Column(db.Integer)
	subcategory2 = db.Column(db.String(200))

try:
	flag1= Subcategories.query.filter_by(quiz_id2=1).all()
	for i in flag1:
		subids_sports.append(unicodedata.normalize('NFKD', i.subcategory2).encode('ascii','ignore'))

except exc.OperationalError:
	pass

try:
	flag2= Subcategories.query.filter_by(quiz_id2=2).all()

	for i in flag2:
		subids_music.append(unicodedata.normalize('NFKD', i.subcategory2).encode('ascii','ignore'))

except exc.OperationalError:
	pass

try:
	flag3= Subcategories.query.filter_by(quiz_id2=3).all()

	for i in flag3:
		subids_cinema.append(unicodedata.normalize('NFKD', i.subcategory2).encode('ascii','ignore'))

except exc.OperationalError:
	pass	


@app.route('/welcome')
def index():
	global loggedinuser
	if(loggedinuser=="qwertyuioplkjhgfdsazxcvbnm1234567890"):
		return logout()
	
	elif(loggedinuser=="admin"):
		return render_template('Admin_index.html')
	else:
		return render_template('Normal_index.html')


@app.route('/addrec', methods=['POST'])
def add():
	
	todo=Quizzes( quiz_id=request.form['qid'], category=request.form['category'], sub_id=request.form['sid'], subcategory=request.form['subcategory'], question=request.form['nm'], 
		opt1=request.form['op1'], opt2=request.form['op2'], opt3=request.form['op3'], opt4=request.form['op4'], typeofquestion=request.form['typeofquestion'], 
		answer=request.form['ans'])

	db.session.add(todo)
	db.session.commit()

	global subids_music
	global subids_sports
	global subids_cinema

	conditions=request.form['isitnew']
	if(int(conditions)==1):
		todo2=Subcategories(quiz_id2=request.form['qid'], subcategory2=request.form['subcategory'])
		db.session.add(todo2)
		db.session.commit()
		flag1= Subcategories.query.filter_by(quiz_id2=1).all()
		flag2= Subcategories.query.filter_by(quiz_id2=2).all()
		flag3= Subcategories.query.filter_by(quiz_id2=3).all()


		for i in flag1:
			if i.subcategory2 not in subids_sports:
				subids_sports.append(i.subcategory2)

		for i in flag2:
			if i.subcategory2 not in subids_music:
				subids_music.append(i.subcategory2)

		for i in flag3:
			if i.subcategory2 not in subids_cinema:
				subids_cinema.append(i.subcategory2)

	return render_template("question_added.html")


@app.route('/deleterec', methods=['POST'])
def Deleted():
	
	x=request.form['inp']
	Quizzes.query.filter_by(id=x).delete()
	db.session.commit()

	return redirect(url_for('index'))


@app.route('/questionpage/<int:quizidhaha>/<subway>/')
@app.route('/questionpage/<int:quizidhaha>/<subway>/<int:QuestionNumber>')
def Sports(QuestionNumber = None, quizidhaha = None, subway=None):
	
	global loggedinuser
	if(loggedinuser=="qwertyuioplkjhgfdsazxcvbnm1234567890"):
		return logout()
	global score
	global ctr
	
	global id_left
	global lifeline
	if QuestionNumber is None:
		exist = Scores.query.filter_by(username=loggedinuser).filter_by(quiz_id=quizidhaha).filter_by(subcategory=subway).first()
		if exist is None:
			obj5 = Scores(username=loggedinuser, quiz_id=quizidhaha, subcategory=subway, score_uptilnow=0, attempts=0, high_score=0, question_left=0, quizid_left=0, subcategory_left="aplpe", ctr_left=0)
			db.session.add(obj5)
			db.session.commit()
		
		return render_template('startquiz.html', quizidhaha=quizidhaha, subway=subway)
	
	else:
		if(QuestionNumber!=1):
			x=request.args.getlist('op', None)
			print(type(x)) 
			print x 
			obj2= Quizzes.query.filter_by(id=ctr).first()
			
			if x:
				if(int(obj2.answer) <= 4):
					if(int(obj2.answer)==int(x[0])):
						if(lifeline==1):
							score+=0.5
						else:
							score+=1
				else:#4C2
					if(len(x)==2):
						if(int(obj2.answer)==5):
							if(int(x[0]) == 1 and int(x[1]) == 2):
								score+=1
						elif(int(obj2.answer) == 6):
							if(int(x[0]) == 1 and int(x[1]) == 3):
								score+=1
						elif(int(obj2.answer) == 7):
							if(int(x[0]) == 1 and int(x[1]) == 4):
								score+=1
						elif(int(obj2.answer) == 8):
							if(int(x[0]) == 2 and int(x[1]) == 3):
								score+=1
						elif(int(obj2.answer) == 9):
							if(int(x[0]) == 2 and int(x[1]) == 4):
								score+=1
						elif(int(obj2.answer) == 10):
							if(int(x[0]) == 3 and int(x[1]) == 4):
								score+=1

		idx=0
		
		obj = Quizzes.query.filter_by(quiz_id=quizidhaha).filter_by(subcategory=subway).all()
		
		object1 = Scores.query.filter_by(username=loggedinuser).filter_by(quiz_id=quizidhaha).filter_by(subcategory=subway).first()
		object1.score_uptilnow=score
		object1.question_left=QuestionNumber
		object1.quizid_left = quizidhaha
		object1.subcategory_left = subway
		object1.ctr_left = ctr
		id_left=object1.id

		db.session.commit()
		
		if (QuestionNumber>len(obj)):
			print score
			temp=score
			object1.score_uptilnow=0
			if(temp > object1.high_score):
				object1.high_score=temp
			object1.attempts += 1
			object1.question_left=0
			id_left=object1.id

			db.session.commit()
			Session = sessionmaker(bind=engine)
			s = Session()
			object2 = s.query(User).filter_by(username=loggedinuser).first()
			object2.staterestore=0

			s.commit()


			score=0
			ctr=0
			lifeline=0
			haha=Scores.query.filter_by(subcategory=subway).filter(Scores.username != "admin").order_by(desc(Scores.high_score))
			for i in haha:
				print i.username
				print i.high_score 
			
			return render_template('scorepage.html', score=temp, subway=subway)
		lifeline=0
		for i in obj:
			idx+=1
			if(idx==QuestionNumber):
				ctr=i.id
				question=unicodedata.normalize('NFKD', i.question).encode('ascii','ignore')
				if(int(i.typeofquestion)==1):
					return render_template('sportsquestions.html', QuestionNumber=QuestionNumber, Question=i, subway=subway, quizidhaha=quizidhaha, question=question)
				else:
					return render_template('mamcq_new.html', QuestionNumber=QuestionNumber, Question=i, subway=subway, quizidhaha=quizidhaha, question=question)


@app.route('/questionpage/<int:quizidhaha>/<subway>/<int:QuestionNumber>/50-50')
def lifeline(QuestionNumber = None, quizidhaha = None, subway=None):
	if(loggedinuser=="qwertyuioplkjhgfdsazxcvbnm1234567890"):
		return logout()
	global ctr
	global lifeline
	lifeline=1
	obj= Quizzes.query.filter_by(id=ctr).first()
	answer=int(obj.answer)

	question=unicodedata.normalize('NFKD', obj.question).encode('ascii','ignore')

	if(answer==1):
		option1=unicodedata.normalize('NFKD', obj.opt1).encode('ascii','ignore')
		name1=1
		option2=unicodedata.normalize('NFKD', obj.opt3).encode('ascii','ignore')
		name2=3
	elif(answer==2):
		option1=unicodedata.normalize('NFKD', obj.opt1).encode('ascii','ignore')
		name1=1
		option2=unicodedata.normalize('NFKD', obj.opt2).encode('ascii','ignore')
		name2=2
	elif(answer==3):
		option1=unicodedata.normalize('NFKD', obj.opt2).encode('ascii','ignore')
		name1=2
		option2=unicodedata.normalize('NFKD', obj.opt3).encode('ascii','ignore')
		name2=3
	else:
		option1=unicodedata.normalize('NFKD', obj.opt2).encode('ascii','ignore')
		name1=2
		option2=unicodedata.normalize('NFKD', obj.opt4).encode('ascii','ignore')
		name2=4
	

	return render_template('50-50.html', QuestionNumber=QuestionNumber, Question=obj, subway=subway, quizidhaha=quizidhaha, option1=option1, option2=option2, question=question, name1=name1, name2=name2)


@app.route('/addquestion')
def addy():
	if(loggedinuser=="qwertyuioplkjhgfdsazxcvbnm1234567890"):
		return logout()
	return render_template('addquestion.html')


@app.route('/youraccount')
def account():
	if(loggedinuser=="qwertyuioplkjhgfdsazxcvbnm1234567890"):
		return logout()
	object1 = Scores.query.filter_by(username=loggedinuser).all()
	
	Session = sessionmaker(bind=engine)
	s = Session()
	nameobj = s.query(User).filter_by(username=loggedinuser).first()
	listofusers=s.query(User).all()
	for i in listofusers:
		finalscore=0
		scoresofuser = Scores.query.filter_by(username=i.username).all()
		for j in scoresofuser:
			finalscore+=j.high_score
		print i.username
		print finalscore

	totalscores = db.session.query(db.func.sum(Scores.high_score).label('average')).scalar()
	print totalscores
	return render_template('youraccount.html', object1=object1, nameobj=nameobj)



@app.route('/deletequestion')
def deletey():
	if(loggedinuser=="qwertyuioplkjhgfdsazxcvbnm1234567890"):
		return logout()
	return render_template('deletequestion.html')


@app.route('/subcategorypagesports')
def subc1():
	if(loggedinuser=="qwertyuioplkjhgfdsazxcvbnm1234567890"):
		return logout()
	global subids_sports
	# for i in subids_sports:
	# 	print type(i);

	return render_template('subcategorypage.html', subcategories=subids_sports, quizidhaha=1)


@app.route('/subcategorypagemusic')
def subc2():
	if(loggedinuser=="qwertyuioplkjhgfdsazxcvbnm1234567890"):
		return logout()
	global subids_music
	# for i in subids_music:
	# 	print type(i);
	return render_template('subcategorypage.html', subcategories=subids_music, quizidhaha=2)


@app.route('/subcategorypagecinema')
def subc3():
	if(loggedinuser=="qwertyuioplkjhgfdsazxcvbnm1234567890"):
		return logout()
	global subids_cinema
	return render_template('subcategorypage.html', subcategories=subids_cinema, quizidhaha=3)


@app.route('/showall')
def display():
	if(loggedinuser=="qwertyuioplkjhgfdsazxcvbnm1234567890"):
		return logout()
	obj = Quizzes.query.all()
	return render_template('showall.html', questions=obj)


@app.route('/logoutinmiddle')
def logoutinmiddle():
	if(loggedinuser=="qwertyuioplkjhgfdsazxcvbnm1234567890"):
		return logout()
	Session = sessionmaker(bind=engine)
	s = Session()
	obj = s.query(User).filter_by(username=loggedinuser).first()
	# print obj.staterestore
	obj.staterestore=1
	# print obj.staterestore
	obj.idleft=id_left
	s.commit()
	return logout()


@app.route('/userstable')
def utable():
	if(loggedinuser=="qwertyuioplkjhgfdsazxcvbnm1234567890"):
		return logout()

	Session = sessionmaker(bind=engine)
	s = Session()
	listofusers=s.query(User).all()

	# leader_names = []
	# leader_scores = []
	leaderboard = []
	
	for i in listofusers:
		finalscore=0
		scoresofuser = Scores.query.filter_by(username=i.username).all()
		for j in scoresofuser:
			finalscore+=j.high_score
		# leader_names.append(i.username)
		# leader_scores.append(finalscore)
		x=(i.username, finalscore)
		if(i.username!="admin"):
			leaderboard.append(x)
	# totalscores = db.session.query(db.func.sum(Scores.high_score).label('average')).scalar()
	
	for i in leaderboard:
		print i[0]
		print i[1]
	leaderboard.sort(key=lambda x: x[1], reverse=True)
	for i in leaderboard:
		print i[0]
		print i[1]

	return render_template('userstable.html', leaderboard=leaderboard)


@app.route('/leaderboard/<subway>')
def leaderboard(subway=None):
	# haha=Scores.query.filter_by(subcategory=subway).order_by(desc(Scores.high_score))
	if(loggedinuser=="qwertyuioplkjhgfdsazxcvbnm1234567890"):
		return logout()
	haha=Scores.query.filter_by(subcategory=subway).filter(Scores.username != "admin").order_by(desc(Scores.high_score))
	# for i in haha:
	# 	print i.username
	# 	print i.high_score 
	return render_template('leaderboard.html', obj=haha)

@app.route('/piechart/<subway>')
def piechart(subway=None):
	if(loggedinuser=="qwertyuioplkjhgfdsazxcvbnm1234567890"):
		return logout()
	haha=Scores.query.filter_by(subcategory=subway).filter(Scores.username != "admin").order_by(desc(Scores.high_score))
	return render_template("piechart.html", obj=haha)



@app.route('/editprofile', methods=['POST'])
def editprofile():
	global loggedinuser
	Session = sessionmaker(bind=engine)
	s = Session()
	USERNAME_NEW = str(request.form['newname'])
	PASS_NEW = str(request.form['newpass'])

	obj = s.query(User).filter_by(username=USERNAME_NEW).first()
	if obj is None:

		cur_user=s.query(User).filter_by(username=loggedinuser).first()
		print cur_user
		cur_user.username = USERNAME_NEW
		cur_user.password = PASS_NEW
		s.commit()
		obj2=Scores.query.filter_by(username=loggedinuser).all()
		for i in obj2:
			i.username=USERNAME_NEW
		db.session.commit()
		loggedinuser=USERNAME_NEW
		return home()
	else:
		return render_template("username_exists2.html")

@app.route('/renderedit')
def renderedit():
	if(loggedinuser=="qwertyuioplkjhgfdsazxcvbnm1234567890"):
		return logout()
	return render_template('editprofile.html')


@app.route('/nocontinue')
def nocontinue():
	
	global ctr
	global score
	ctr=0
	score=0
	Session = sessionmaker(bind=engine)
	s = Session()
	obj = s.query(User).filter_by(username=loggedinuser).first()
	print obj.staterestore
	obj.staterestore=0
	print obj.staterestore
	s.commit()
	
	obj2=Scores.query.filter_by(id=obj.idleft).first()
	obj2.quizid_left=0
	obj2.question_left=0
	obj2.score_uptilnow=0
	db.session.commit()
	return home()


if __name__ == '__main__':
	db.create_all()
	app.secret_key = os.urandom(12)
	app.run(debug=True)


#@app.route('/addrec',methods = ['POST', 'GET'])
#def addrec():
#   res, msg = model.addUser(request)
#   return render_template("result.html", result=res, message=msg
