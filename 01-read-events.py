import json
from logging import exception
from requests import get
import sqlite3
from pprint import pprint

con = sqlite3.connect('tutorials_events.db')
cur = con.cursor()
contracts_to_check = ["0x5af2ba86ed7df13ee2b7557a7e6db163e04c5238980c6e9fdeb4bcc040a48bb",
                      "0x4f857652d367b49d2a7de4c8486743f84d53544bc258bfa4de649a24d88b942", "0x3991cf84dea67dda6456876c710f8afd021df235100324618df8ba0fcceb66e"]
BASE_URL = "https://goerli.voyager.online/api"
PAGE_SIZE = 50


def insert_into_players(args):
    cur.executemany("""INSERT INTO players
	(
				id,
				account,
				from_address,
				blockHash,
				transactionHash,
				status,
				keys,
				rank
			) VALUES
			(
				:id,
				:account,
				:from_address,
				:blockHash,
				:transactionHash,
				:status,
				:keys,
				:rank
			)
	""", args)
    con.commit()


def insert_into_exercises(args):
    cur.executemany("""INSERT INTO exercises
	(
				id,
                account,
                workshop,
                exercise,
                from_address,
                blockHash,
                transactionHash,
                status,
                keys
			) VALUES
			(
				:id,
                :account,
                :workshop,
                :exercise,
                :from_address,
                :blockHash,
                :transactionHash,
                :status,
                :keys
            )
	""", args)
    con.commit()


def get_event_ids_for_contract(contract_address):
    last_page = get(
        f"{BASE_URL}/events?contract={contract_address}&p=1").json()["lastPage"]

    print(f"{last_page} pages to go through")
    event_ids = [item["id"] for i in range(last_page) for item in get(
        f"{BASE_URL}/events?contract={contract_address}&p={i}&ps={PAGE_SIZE}").json()["items"]]
    return event_ids


def get_event(event_id):
    return get(f"{BASE_URL}/event/{event_id}").json()


print("Retrieving all event ids")
event_ids = list(set([
    event_id for contract in contracts_to_check for event_id in get_event_ids_for_contract(contract)]))
with open("all_event_ids.json", "w") as fileTarget:
    json.dump(event_ids, fileTarget)
print(f"Retrieving all {len(event_ids)} events")
player_events = []
exercise_events = []
for counter, event_id in enumerate(event_ids):
    print(f"Event {counter} / {len(event_ids)}, {event_id}")
    event = get_event(event_id)
    if not set(event.keys()) == set({"data", "keys", "from_address", "id", "blockHash", "transactionHash", "status"}):
        continue
    try:
        event["keys"] = event["keys"].pop()
    except Exception as e:
        print(e, event_id)
        continue
    data = event.pop("data")
    if len(data) > 2:
        event["account"] = data[0]
        event["workshop"] = data[1]
        event["exercise"] = data[2]
        exercise_events.append(event)
    else:
        event["account"] = data[0]
        event["rank"] = data[1]
        player_events.append(event)
print("saving exercises")
insert_into_exercises(exercise_events)
print("saving players")
insert_into_players(player_events)
