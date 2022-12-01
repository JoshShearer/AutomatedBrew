from modules import app, cbpi
from thread import start_new_thread
import logging
import time
import requests

pushover_token = None
pushover_user = None
pushover = None

def pushoverToken():
	global pushover_token
	pushover_token = cbpi.get_config_parameter("pushover_token", None)
	if pushover_token is None:
		print "INIT Pushover Token"
		try:
			cbpi.add_config_parameter("pushover_token", "", "text", "Pushover API Token")
		except:
			cbpi.notify("Pushover Error", "Unable to update database. Update CraftBeerPi and reboot.", type="danger", timeout=None)

def pushoverUser():
	global pushover_user
	pushover_user = cbpi.get_config_parameter("pushover_user", None)
	if pushover_user is None:
		print "INIT Pushover User Key"
		try:
			cbpi.add_config_parameter("pushover_user", "", "text", "Pushover User Key")
		except:
			cbpi.notify("Pushover Error", "Unable to update database. Update CraftBeerPi and reboot.", type="danger", timeout=None)

@cbpi.initalizer(order=9000)
def init(cbpi):
	global pushover
	cbpi.app.logger.info("INITIALIZE Pushover PLUGIN")
	pushoverUser()
	pushoverToken()
	if pushover_token is None or not pushover_token:
		cbpi.notify("Pushover Error", "Check Pushover API Token is set", type="danger", timeout=None)
	elif pushover_user is None or not pushover_user:
		cbpi.notify("Pushover Error", "Check Pushover User Key is set", type="danger", timeout=None)
	else:
		pushover = "OK"

@cbpi.event("MESSAGE", async=True)
def messageEvent(message):
	pushoverData = {}
	pushoverData["token"] = pushover_token
	pushoverData["user"] = pushover_user
	pushoverData["message"] = message["message"]
	pushoverData["title"] = message["headline"]
	requests.post("https://api.pushover.net/1/messages.json", data=pushoverData)
