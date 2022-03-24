import json


with open("all_events.json") as fileTarget:
	retrievedElements = json.load(fileTarget)
	fileTarget.close()
all_players = {}

for element in retrievedElements:
	# print(element)
	if (not 'keys' in element) or (not 'data' in element):
		continue
	if not '755441373043073014148610978030610359041553112847603033567051378564483684855' in element['keys']:
		continue
	player_address = str(element['data'][0])
	workshop_number = int(element['data'][1])
	exercice_number = int(element['data'][2])
	if not player_address in all_players:
		all_players[player_address] = {}
		all_players[player_address]["workshops"] = {}
	if not workshop_number in all_players[player_address]["workshops"]:
		all_players[player_address]["workshops"][workshop_number] = []
	if not exercice_number in all_players[player_address]["workshops"][workshop_number]:
		all_players[player_address]["workshops"][workshop_number].append(exercice_number)

# Counting players, workshops and exercices
all_workshops = {}
all_workshop_counts = {}
all_exercice_counts = {}
workshops_thresholds = [0, 2, 1, 1, 0]
print("######## Player numbers")
print("%s unique addresses" % len(all_players))
for player in all_players:
	total_exercices_done = 0
	for workshop in all_players[player]["workshops"]:
		if not workshop in all_workshops:
			all_workshops[workshop] = {}
			all_workshops[workshop]["total_players"] = 0
			all_workshops[workshop]["total_players_over_threshold"] = 0
			all_workshops[workshop]["exercices_player_counter"] = {}
		if not len(all_players[player]["workshops"]) in all_workshop_counts:
			all_workshop_counts[len(all_players[player]["workshops"])] = {}
			all_workshop_counts[len(all_players[player]["workshops"])]["total_players"] = 0
		all_workshops[workshop]["total_players"]+=1
		all_workshop_counts[len(all_players[player]["workshops"])]["total_players"]+=1
		total_exercices_done += len(all_players[player]["workshops"][workshop])
		if len(all_players[player]["workshops"][workshop]) > workshops_thresholds[workshop]:
			all_workshops[workshop]["total_players_over_threshold"]+=1
		for exercice in all_players[player]["workshops"][workshop]:
			if not exercice in all_workshops[workshop]["exercices_player_counter"]:
				all_workshops[workshop]["exercices_player_counter"][exercice] = 0
			all_workshops[workshop]["exercices_player_counter"][exercice] +=1
	if not total_exercices_done in all_exercice_counts:
		all_exercice_counts[total_exercices_done] = {}
		all_exercice_counts[total_exercices_done]["total_players"] = 0
	all_exercice_counts[total_exercices_done]["total_players"]+=1
for workshop in all_workshops:
	print("%s players for workshop %s, %s over threshold" % (all_workshops[workshop]["total_players"] , workshop, all_workshops[workshop]["total_players_over_threshold"] ))
print("######## Workshops per player")
for workshop_count in all_workshop_counts:
	print("%s players did %s workshops" % (all_workshop_counts[workshop_count]["total_players"] , workshop_count))
print("######## Exercices per players")
for exercice_count in all_exercice_counts:
	print("%s players did %s exercices" % (all_exercice_counts[exercice_count]["total_players"] , exercice_count))

print("######## Workshop exercices progression")
for workshop in all_workshops:
	for exercice in all_workshops[workshop]["exercices_player_counter"]:
		print("%s players on exercice %s on workshop %s" % (all_workshops[workshop]["exercices_player_counter"][exercice], exercice, workshop))


