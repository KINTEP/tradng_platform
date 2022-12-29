from flask import Flask, render_template, request, jsonify
import time
import random
import datetime
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import requests
from helpers import get_market_data
from data_center import get_close_price
import time




app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = '119AH192781'


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "db.sqlite")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class Trades(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	user = db.Column(db.Integer)
	asset = db.Column(db.String(100))
	entry_price = db.Column(db.Float)
	date =  db.Column(db.DateTime, default=datetime.datetime.now)
	order_type =  db.Column(db.String(100))
	size =  db.Column(db.Float)
	stop_loss =  db.Column(db.Float)
	take_profit =  db.Column(db.Float)
	net_profit =  db.Column(db.Float)
	close_price =  db.Column(db.Float)
	status = db.Column(db.Boolean, default = False)

	def __repr__(self):
		return f"{self.asset} {self.entry_price}"

class Users(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.Integer, unique = True)
	balance = db.Column(db.Float)
	deposit = db.Column(db.Float)
	equity = db.Column(db.Float)


	def __repr__(self):
		return f"{self.id} {self.name}"



def create_all_candles():
	open = round(100*random.random(),2)
	closes = [open*random.choice([1.01,1.001, 1.02,1.002, 1.03,1.003,]), open*random.choice([0.99, 0.98, 0.97,0.912, 0.82, 0.88])] 
	close = random.choice(closes)
	high = random.choice([1.01, 1.02, 1.03])*close
	if close >= open:
		high = random.choice([1.01, 1.02, 1.03])*close
		low = random.choice([0.99, 0.98, 0.97])*open
	if close < open:
		low = random.choice([0.99, 0.98, 0.97])*close
		high = random.choice([1.01, 1.02, 1.03])*open
	data = {
		"time": f"{str(datetime.datetime.now().year)}-{str(datetime.datetime.now().month)}-{str(datetime.datetime.now().day)}",
		"open": round(open, 2),
		"high": round(high, 2),
		"low": round(low, 2),
		"close": round(close, 2)	
	}
	return data





profits = [100,200,300,-200,-100,10,30,-300,-245]
i = 0
@app.route("/")
def home():
	balance = 1000000
	return render_template('home.html', balance=balance)

@app.route("/get_prices")
def get_prices():
	#for i in range(100000):
	res = [{"price":round(100*random.random(),2), "size": round(random.random(), 5)} for i in range(9)]
	return res

#print(list(range(-100, 100)))

count = 0

def increase():
    global count
    count += 1
    return (count)




@app.route("/get_ohlc/<symb>")
def get_ohlc(symb):
	#data = get_market_data()
	data = get_close_price(symb)
	return data


@app.route("/all_get_ohlc")
def all_get_ohlc():
	data = [create_all_candles() for i in range(200)]
	return data


@app.route("/get_history")
def get_history():
	res = [{"price":round(25000*random.random(),2), "amount": round(random.random(), 5), "time":f"{str(datetime.datetime.now().time().hour)}:{str(datetime.datetime.now().time().minute)}:{str(datetime.datetime.now().time().second)}"} for i in range(20)]
	return res


@app.route("/chart_data")
def chart_data():
	initial_price = 30000
	res = {"price": int(random.random()*30000)}
	return res


@app.route("/open_trade", methods = ['POST', 'GET'])
def open_trade():
	standard_lot = 1000
	if request.method == "GET":
		user = request.args.get('user')
		asset = request.args.get('asset')
		size = float(request.args.get('size'))
		stop_loss = float(request.args.get('stop_loss'))
		take_profit = float(request.args.get('take_profit'))
		order_type = request.args.get('order_type')
		entry_price = float(requests.get(f"http://127.0.0.1:5000/get_ohlc/{asset}").json()['close'])
		status = True
		if order_type != "sell":
			stop_loss = entry_price - stop_loss
			take_profit = entry_price + take_profit
		else:
			stop_loss = entry_price + stop_loss
			take_profit = entry_price - take_profit
		rate = size/standard_lot
		net_profit = float(-1*rate)
		trade = Trades(user=user, asset=asset, entry_price=entry_price, order_type=order_type, size=size, stop_loss=stop_loss, take_profit=take_profit, status=status, net_profit=net_profit)
		db.session.add(trade)
		db.session.commit()

		query = Trades.query.all()
		idx = query[-1].id
		return {"status": "success", "id": idx, "price": entry_price, "loss": stop_loss, "profit": take_profit}, 200

@app.route("/get_profit/<int:id>")
def get_profit(id):
	trade = Trades.query.get(id)
	asset = trade.asset
	profit = trade.net_profit
	return {"profit": profit}


@app.route("/close_trade")
def close_trade():
	idx = request.args.get("id")
	trade = Trades.query.get(idx)
	asset = trade.asset
	trade.status = False
	trade.close_price =  requests.get(f"http://127.0.0.1:5000/get_ohlc/{asset}").json()['close']
	user = Users.query.get(trade.user)
	user.balance = user.balance + trade.net_profit
	db.session.commit()
	return [idx]


@app.route("/update_trades")
def update_trades():
	trades = Trades.query.filter_by(status=True).all()
	original_equity = Users.query.get(1)
	standard_lot = 1000
	for trd in trades:
		asset = trd.asset
		current_price = requests.get(f"http://127.0.0.1:5000/get_ohlc/{asset}").json()['close']
		if trd.order_type == "buy":
			if (current_price >= trd.take_profit) or (current_price <= trd.stop_loss):
				trd.status = False
				trd.close_price = current_price
		if trd.order_type == "sell":
			if (current_price <= trd.take_profit) or (current_price >= trd.stop_loss):
				trd.status = False
				trd.close_price = current_price
		#profit = current_price.get('close') - trd.entry_price
		if trd.order_type != "sell":
			profit = current_price - trd.entry_price
		else:
			profit = trd.entry_price - current_price
		rate = trd.size/standard_lot
		if profit >= 0:
			profit=profit
		else:
			profit = 1.01*profit
		trd.net_profit = round(rate*profit, 2)
		user = Users.query.get(trd.user)
		user.equity  = original_equity.equity + trd.net_profit
	db.session.commit()
	all_trades = Trades.query.filter_by(status=True).all()
	all_trades = [i.__dict__ for i in trades]
	all_trades1 = []
	for dat in all_trades:
		dat.pop("_sa_instance_state")
		all_trades1.append(dat)
	return all_trades1


@app.route("/all_open_trades")
def all_open_trades():
	all_trades = Trades.query.filter_by(status=True).all()
	all_trades = [i.__dict__ for i in all_trades]
	all_trades1 = []
	for dat in all_trades:
		dat.pop("_sa_instance_state")
		all_trades1.append(dat)
	return all_trades1


@app.route("/user_accont_summary")
def user_accont_summary():
	user = Users.query.get(1)
	balance = user.balance
	equity = user.equity
	deposit = user.deposit
	trade = Trades.query.filter_by(status=False)
	real_profit = sum([i.net_profit for i in trade])
	data = {
		"balance": deposit + real_profit,
		"equity": equity,
		"deposit": deposit,
		"real_profit": real_profit
	}
	return data



@app.route("/cancel_all")
def cancel_all():
	status = request.args.get("status")
	if status == str(1):
		trades = Trades.query.filter_by(status=True)
		for trd in trades:
			trd.status = False
		db.session.commit()
		return {"data": "success"}
	return {"data": "failed"}

@app.route("/trade_history")
def trade_history():
	trades = Trades.query.filter_by(status=False)
	all_trades = [i.__dict__ for i in trades]
	all_trades1 = []
	for dat in all_trades:
		dat.pop("_sa_instance_state")
		all_trades1.append(dat)
	return all_trades1


@app.route("/reset_stop_loss")
def reset_stop_loss():
	trade_id = request.args.get('id')
	#price = request.args.get('price')
	trade = Trades.query.get(int(trade_id))
	entry = trade.entry_price
	trade.stop_loss = float(entry)
	db.session.commit()
	return {"data": entry}





#[30000,29000,28100,31000]

"""
@socket.on('message')
def handlemsg(msg):
	global i
	if i < len(profits):
		socket.send(profits[i])
		i += 1



"""
with app.app_context():
	db.drop_all()
	db.create_all()
	
	user = Users(name="Newton Isaac Kumi", balance=1000, equity=1000, deposit=1000)
	db.session.add(user)
	db.session.commit()


if __name__ == '__main__':

	app.run(debug=True)
	#socket.run(app)