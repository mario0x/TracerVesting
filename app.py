from flask import Flask, render_template, request
from web3 import Web3
from datetime import datetime
from pycoingecko import CoinGeckoAPI

app = Flask(__name__)
cg = CoinGeckoAPI()

@app.route("/", methods=['GET', 'POST'])
def index():
	abi = [{"inputs":[{"internalType":"address","name":"tcr","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":False,"internalType":"address","name":"claimer","type":"address"}],"name":"Claim","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":True,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"currentTime","type":"uint256"},{"internalType":"uint256","name":"startTime","type":"uint256"},{"internalType":"uint256","name":"endTime","type":"uint256"}],"name":"calcDistribution","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"scheduleId","type":"uint256"}],"name":"cancelVesting","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"scheduleNumber","type":"uint256"}],"name":"claim","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"scheduleId","type":"uint256"}],"name":"getVesting","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"numberOfSchedules","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"schedules","outputs":[{"internalType":"uint256","name":"totalAmount","type":"uint256"},{"internalType":"uint256","name":"claimedAmount","type":"uint256"},{"internalType":"uint256","name":"startTime","type":"uint256"},{"internalType":"uint256","name":"cliffTime","type":"uint256"},{"internalType":"uint256","name":"endTime","type":"uint256"},{"internalType":"bool","name":"isFixed","type":"bool"},{"internalType":"bool","name":"cliffClaimed","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bool","name":"isFixed","type":"bool"},{"internalType":"uint256","name":"cliffWeeks","type":"uint256"},{"internalType":"uint256","name":"vestingWeeks","type":"uint256"}],"name":"setVestingSchedule","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"valueLocked","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}]
	infuraLink = ''

	# Connect to an infura node in order to interact with ethereum
	w3 = Web3(Web3.HTTPProvider(infuraLink))

	# Get TCR price
	cg_output = cg.get_token_price(id='ethereum', vs_currencies='usd', contract_addresses='0x9c4a4204b79dd291d6b6571c5be8bbcd0622f050')
	tracer_price = cg_output['0x9c4a4204b79dd291d6b6571c5be8bbcd0622f050']['usd']

	if request.method ==  "POST":
		if list(request.form.keys())[3] == 'submitBtn':
			vestingContract = request.form['contract']
			ethaddy = request.form['ethaddy']
			schedule = request.form['schedule']
			
			contract = w3.eth.contract(Web3.toChecksumAddress(vestingContract), abi=abi)

			vestingData = contract.functions.schedules(ethaddy, int(schedule)).call()
			
			total_amount = vestingData[0] / 1000000000000000000
			claimed_amount = round(vestingData[1] / 1000000000000000000, 2)
			start_time = datetime.utcfromtimestamp(vestingData[2]).strftime('%Y-%m-%d')
			cliff_time = datetime.utcfromtimestamp(vestingData[3]).strftime('%Y-%m-%d')
			end_time = datetime.utcfromtimestamp(vestingData[4]).strftime('%Y-%m-%d')
			cliff_claimed = vestingData[5]

			return render_template("dashboard.html", total_amount=total_amount, claimed_amount=claimed_amount, start_time=start_time, cliff_time=cliff_time, end_time=end_time, cliff_claimed=cliff_claimed, tracer_price=tracer_price)
	return render_template("front.html")

if __name__ == '__main__':
    app.run(debug=False)