import requests as req
import json
contracts_to_check = ['0x5af2ba86ed7df13ee2b7557a7e6db163e04c5238980c6e9fdeb4bcc040a48bb', '0x4f857652d367b49d2a7de4c8486743f84d53544bc258bfa4de649a24d88b942', '0x3991cf84dea67dda6456876c710f8afd021df235100324618df8ba0fcceb66e']



def get_event_ids_for_contract(contract_address):
	r = req.get('https://goerli.voyager.online/api/events?contract=%s&p=1' % contract_address)
	result = r.json()
	last_page = result["lastPage"]
	print("%s pages to go through" % last_page)
	event_ids = []
	for i in range(0, last_page):
		r = req.get('https://goerli.voyager.online/api/events?contract=%s&p=%s' % (contract_address, i))
		result = r.json()
		for item in result["items"]:
			event_ids.append(item["id"])
	return event_ids

def get_event(event_id):
	r = req.get('https://goerli.voyager.online/api/event/%s' % event_id)
	return r.json()
	
print("Retrieving all event ids")
event_ids = []
for contract in contracts_to_check:
	contract_event_ids = get_event_ids_for_contract(contract)
	for event_id in contract_event_ids:
		event_ids.append(event_id)
with open("all_event_ids.json", 'w') as fileTarget:
    json.dump(event_ids, fileTarget)
fileTarget.close()
print("Retrieving all %s events" % len(event_ids))
all_events = []
counter = 0
for event_id in event_ids:
	print("Event %s / %s" % (counter, len(event_ids)))
	all_events.append(get_event(event_id))
	counter += 1
with open("all_events.json", 'w') as fileTarget:
    json.dump(all_events, fileTarget)
fileTarget.close()

