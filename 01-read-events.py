import json
from logging import exception
from requests import get
import sqlite3
from pprint import pprint
import math 

con = sqlite3.connect('tutorials_events.db')
cur = con.cursor()
contracts_to_check = ["0x5af2ba86ed7df13ee2b7557a7e6db163e04c5238980c6e9fdeb4bcc040a48bb",
                      "0x4f857652d367b49d2a7de4c8486743f84d53544bc258bfa4de649a24d88b942", "0x3991cf84dea67dda6456876c710f8afd021df235100324618df8ba0fcceb66e"]
BASE_URL = "https://goerli.voyager.online/api"
PAGE_SIZE = 50

def create_tables():
    cur.execute( "CREATE TABLE IF NOT EXISTS players ( id integer primary key autoincrement unique , account text not null , from_address text ,blockHash text ,transactionHash text not null ,status text ,keys text,rank integer)" )
    cur.execute( " CREATE TABLE IF NOT EXISTS exercises ( id integer primary key autoincrement unique , starknet_id text not null unique, account text not null , workshop text not null ,exercise text, from_address text, blockHash text , transactionHash text not null ,keys text)" )
    cur.execute( " CREATE TABLE IF NOT EXISTS event_ids ( id integer primary key autoincrement unique , contract_address text not null , starknet_id text not null unique, processed integer)" )

def insert_into_players(args):
    cur.executemany("""INSERT INTO players
	(
				account,
				from_address,
				blockHash,
				transactionHash,
				keys,
				rank
			) VALUES
			(
				:account,
				:from_address,
				:blockHash,
				:transactionHash,
				:keys,
				:rank
			)
	""", args)
    con.commit()


def insert_into_exercises(args):
    cur.executemany("""INSERT INTO exercises
	(
                account,
                starknet_id,
                workshop,
                exercise,
                from_address,
                blockHash,
                transactionHash,
                keys
			) VALUES
			(
                :account,
                :starknet_id,
                :workshop,
                :exercise,
                :from_address,
                :blockHash,
                :transactionHash,
                :keys
            )
	""", args)
    con.commit()

def insert_into_event_ids(args):
    cur.executemany("""INSERT INTO event_ids
    (
                contract_address,
                starknet_id,
                processed
            ) VALUES
            (
                :contract_address,
                :starknet_id,
                :processed
            )
    """, args)
    con.commit()


def count_events_in_sql_per_contracts(contract_address):
    result = cur.execute(f"SELECT count(distinct starknet_id) from event_ids where contract_address = '{contract_address}'")
    return result.fetchone()[0]

def count_unprocessed_events():
    result = cur.execute(f"SELECT count(distinct starknet_id) from event_ids where processed != 1")
    return result.fetchone()[0]

def get_events_already_in_sql(starknet_ids_list):
    list_as_string = ""
    for starknet_id in starknet_ids_list:
        list_as_string += f"'{starknet_id}',"
    list_as_string = list_as_string[:-1]
    result = cur.execute(f"SELECT starknet_id from event_ids where starknet_id in ({list_as_string})")
    return [element[0] for element in result.fetchall()]

def get_non_processed_events_in_sql():
    result = cur.execute(f"SELECT starknet_id from event_ids where processed != 1 LIMIT {PAGE_SIZE} ")
    return [element[0] for element in result.fetchall()]

def update_events_processed(starknet_ids_list):
    list_as_string = ""
    for starknet_id in starknet_ids_list:
        list_as_string += f"'{starknet_id}',"
    list_as_string = list_as_string[:-1]
    result = cur.execute(f"UPDATE event_ids set processed = 1 where starknet_id in ({list_as_string})")
    con.commit()

def update_event_ids_for_contract(contract_address):
    existing_events = count_events_in_sql_per_contracts(contract_address)
    print(f"{existing_events} events already stored")
    print(f"{BASE_URL}/events?contract={contract_address}&p=1&ps={PAGE_SIZE}")
    last_page = get(
        f"{BASE_URL}/events?contract={contract_address}&p=1&ps={PAGE_SIZE}").json()["lastPage"]
    print(len(get(
        f"{BASE_URL}/events?contract={contract_address}&p=1&ps={PAGE_SIZE}").json()["items"]))
    print(f"{last_page} pages in total")
    starting_page = math.floor(existing_events/PAGE_SIZE)
    print(f"Starting at page {starting_page}")
    for i in range(starting_page, last_page +1):
        page_event_ids = [item["id"] for item in get(
        f"{BASE_URL}/events?contract={contract_address}&p={i}&ps={PAGE_SIZE}").json()["items"]]
        already_recorded_events = get_events_already_in_sql(page_event_ids)
        for id in already_recorded_events:
            page_event_ids.remove(id)

        events_ids_formatted = [{"starknet_id": event, "contract_address": contract_address, "processed": 0} for event in page_event_ids]

        # print(len(event_ids))
        # print(events_ids_formatted)
        insert_into_event_ids(events_ids_formatted)

def get_event(event_id):
    return get(f"{BASE_URL}/event/{event_id}").json()

### Main function
def run():
    print("Retrieving all event ids")
    for contract in contracts_to_check:
        update_event_ids_for_contract(contract)
    unprocessed_events_number = count_unprocessed_events()
    while(unprocessed_events_number != 0):
        event_ids = get_non_processed_events_in_sql()
        print(f"Retrieving {len(event_ids)} non processed events, {unprocessed_events_number} remaining")
        player_events = []
        exercise_events = []
        for counter, event_id in enumerate(event_ids):
            print(f"Event {counter} / {len(event_ids)}, {event_id}")
            event = get_event(event_id)
            if not set({"data", "keys", "from_address", "id", "blockHash", "transactionHash"}).issubset(set(event.keys())):
                print("continuing")
                print(event)
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
                event["starknet_id"] = event_id
                exercise_events.append(event)
            else:
                event["account"] = data[0]
                event["rank"] = data[1]
                player_events.append(event)
        print("saving exercises")
        insert_into_exercises(exercise_events)
        print("saving players")
        insert_into_players(player_events)
        update_events_processed(event_ids)
        unprocessed_events_number = count_unprocessed_events()

if __name__ == '__main__':
    create_tables()
#    update_event_ids_for_contract(contracts_to_check[0])
    run()

