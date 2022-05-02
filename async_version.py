from multiprocessing import cpu_count
from requests import get
import json
import concurrent.futures as cf
from datetime import datetime
import asyncio  # Gives us async/await
import aiohttp

contracts_to_check = ['0x5af2ba86ed7df13ee2b7557a7e6db163e04c5238980c6e9fdeb4bcc040a48bb',
                      '0x4f857652d367b49d2a7de4c8486743f84d53544bc258bfa4de649a24d88b942',
                      '0x3991cf84dea67dda6456876c710f8afd021df235100324618df8ba0fcceb66e']

BASE_URL = "https://goerli.voyager.online/api/"
PAGE_SIZE = 50
NUM_CORES = cpu_count()


async def get_event_ids_for_contract(session, contract_address):
    print(contract_address)
    async with session.get(f"{BASE_URL}events?contract=%{contract_address}&p=1&ps={PAGE_SIZE}") as resp:
        res = await resp.json()
    last_page = res["lastPage"]
    print(f"{last_page} pages to go through")
    event_ids = []
    for i in range(last_page):
        async with session.get(
                f"{BASE_URL}api/events?contract={contract_address}&p={i}&ps={PAGE_SIZE}") as resp:
            res = await resp.json()
            event_ids.extend([x["id"] for x in res["items"]])

    return event_ids


async def fetch_all(session):
    return await asyncio.gather(*[asyncio.create_task(
        get_event_ids_for_contract(session, contract)) for contract in contracts_to_check])


async def get_event(session, event_id):
    async with session.get(f"{BASE_URL}api/event/{event_id}") as resp:
        res = await resp.json()
    return res


async def main():
    print("Retrieving all event ids")

    start = datetime.now()
    all_events = []
    async with aiohttp.ClientSession() as session:
        all_event_ids = [event_id for event_ids in await fetch_all(session) for event_id in event_ids]

        all_events.extend(await asyncio.gather(*[asyncio.create_task(
            get_event(session, event_id)) for event_id in all_event_ids]))

    print(datetime.now() - start)
    with open("all_event_ids.json", 'w') as fileTarget:
        json.dump(all_event_ids, fileTarget)
    print("Retrieving all %s events" % len(all_event_ids))

    # counter = 0
    # for event_id in event_ids:
    #     print("Event %s / %s" % (counter, len(event_ids)))
    #     all_events.append(get_event(event_id))
    #     counter += 1
    with open("all_events.json", 'w') as fileTarget:
        json.dump(all_events, fileTarget)


asyncio.run(main())
