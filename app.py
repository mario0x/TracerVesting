from flask import Flask, render_template, request
from web3 import Web3
from datetime import datetime
from pycoingecko import CoinGeckoAPI
from utils import *

app = Flask(__name__)
cg = CoinGeckoAPI()

@app.route("/", methods=['GET', 'POST'])
def index():

	rpcURL = 'https://mainnet.infura.io/v3/a0458173591d445880be6f8dfbb78a67'

	# Connect to an eth node in order to interact with ethereum
	w3 = Web3(Web3.HTTPProvider(rpcURL))

	# Get TCR price
	cg_output = cg.get_token_price(id='ethereum', vs_currencies='usd', contract_addresses='0x9c4a4204b79dd291d6b6571c5be8bbcd0622f050')
	tracer_price = cg_output['0x9c4a4204b79dd291d6b6571c5be8bbcd0622f050']['usd']


	if request.method ==  "POST":
		if list(request.form.keys())[1] == 'submitBtn':
			# vestingContract = request.form['contract']
			ethaddy = request.form['ethaddy']
			# schedule = request.form['schedule']

			# find users vesting
			type = NO_VESTING
			# TODO check for multiple vesting schedules on the same contract
			# TODO check for multiple types of vesting schedules for the same user
			for vesting_type in list(vesting_contracts.keys()):
				(address, name, abi) = vesting_contracts[vesting_type]
				contract = w3.eth.contract(Web3.toChecksumAddress(address), abi=abi)

				# We can seperate the contract info into two seperate types
				# simple [total available, amount claimed]
				# and complex [totalAmount, claimedAmount, startTime, cliffTime, endTime, isFixed, cliffClaimed | asset]

				# initial 100 vesting doesnt require schedule id function is getVesting(address)
				# returns [total available, claimed]
				if vesting_type == INITIAL_100:
					vesting_data = contract.functions.getVesting(ethaddy).call()

				# mycelium vesting requires schedule id but does not have a number of schedules function is getVesting(address, id)
				# returns [total available, claimed]
				elif vesting_type == MYCELIUM_VESTING:
					vesting_data = contract.functions.getVesting(ethaddy, 0).call()

				# Governor vesting has a number of schedules and requires a schedule id function is schedules(address, id)
				# return [totalAmount, claimedAmount, startTime, cliffTime, endTime, isFixed, cliffClaimed]

				# Mycelium employee vesting has a number of schedules and requires a schedule id function is schedules(address, id)
				# return [totalAmount, claimedAmount, startTime, cliffTime, endTime, isFixed, cliffClaimed]

				# Standard vesting has a number of schedules. Function is schedules(address, id)
				# return [totalAmount, claimedAmount, startTime, cliffTime, endTime, isFixed, asset]
				elif vesting_type == GOVERNOR_VESTING or vesting_type == MYCELIUM_EMPLOYEE_VESTING or vesting_type == STANDARD_VESTING:
					vesting_data = contract.functions.schedules(ethaddy, 0).call()

				if vesting_data[0] != 0:
					print("Found {0} vesting schedule".format(name))
					print(vesting_data)
					type = vesting_type
					break

				
			vesting_class = getVestingClass(type)
			if vesting_class == COMPLEX_VESTING:
				total_amount = vesting_data[0] / 1000000000000000000
				claimed_amount = round(vesting_data[1] / 1000000000000000000, 2)
				start_time = datetime.utcfromtimestamp(vesting_data[2]).strftime('%Y-%m-%d')
				cliff_time = datetime.utcfromtimestamp(vesting_data[3]).strftime('%Y-%m-%d')
				end_time = datetime.utcfromtimestamp(vesting_data[4]).strftime('%Y-%m-%d')
				cliff_claimed = vesting_data[5]
				print("Found complex vesting")
				return render_template("dashboard.html", total_amount=total_amount, claimed_amount=claimed_amount, start_time=start_time, cliff_time=cliff_time, end_time=end_time, cliff_claimed=cliff_claimed, tracer_price=tracer_price, complex_vesting=True)
			elif vesting_class == SIMPLE_VESTING:
				total_amount = vesting_data[0] / 1000000000000000000
				claimed_amount = round(vesting_data[1] / 1000000000000000000, 2)
				print("Found simple vesting")
				return render_template("dashboard.html", total_amount=total_amount, claimed_amount=claimed_amount, tracer_price=tracer_price)
			else:
				print("Found no vesting")
				return render_template("front.html", no_vesting=True)

	return render_template("front.html")

if __name__ == '__main__':
    app.run(debug=False)