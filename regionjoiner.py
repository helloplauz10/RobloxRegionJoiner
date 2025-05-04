# https://devforum.roblox.com/t/get-jobidgamejoinattemptid-of-a-game-using-the-api/2312602/3
import requests
import sys
import json
import webbrowser
import time

placeId = int(sys.argv[1])

with open("ServerList.json") as file:
    serverList = json.load(file)
    print(f"Using NotValra's Server List. Loaded {len(serverList)} IPs (might need an update next 2026 because of new mexico server)")

with open("txt.eikooc"[::-1]) as cookie:
    roblosecurity = cookie.read().rstrip()

#print("Attempt to fetch  csrf token")
#csrf = requests.post("https://auth.roblox.com/v1/authentication-ticket", headers = {"Cookie": ".ROBLOSECURITY=" + roblosecurity}).headers["x-csrf-token"]

print("Attempt to fetch game instances")

nextCursor = ""
while True:
    gameInstancesReq = requests.get(f"https://games.roblox.com/v1/games/{placeId}/servers/Public?sortOrder=0&excludeFullGames=true&limit=100&cursor={nextCursor}", headers = {"User-Agent": "Roblox/WinInet"})
    gameInstancesReqJson = gameInstancesReq.json()
    if gameInstancesReq.status_code != 200:
        print(f"Rate limited maybe? sleeping for a minute. (status code {gameInstancesReq.status_code})")
        time.sleep(60)
        continue
    if "--ignore_insufficient" in sys.argv:
        gameInstances = gameInstancesReqJson["data"]
    else:
        gameInstances = [i for i in gameInstancesReqJson["data"] if i["maxPlayers"] - 2 >= i["playing"]]
    if "--ignore_insufficient" in sys.argv or len(gameInstances) >= 5:
        print(f"Found {len(gameInstances)} instances. (some may be unjoinable if it went full that quick)")
        break
    nextCursor = gameInstancesReqJson["nextPageCursor"]
    print("Attempt to fetch again.. Insufficient instances. (needs 5+ servers that has 2 players less)")

instances = []
for instance in gameInstances:
    #print(f"Getting info on {jobId}")
    jobId = instance["id"]
    gameJoinReq = requests.post("https://gamejoin.roblox.com/v1/join-game-instance",
                            cookies = {".ROBLOSECURITY": roblosecurity, "path": "/", "domain": ".roblox.com"},
                            json = {"placeId": placeId, "isTeleport": False, "gameId": jobId, "gameJoinAttemptId": jobId},
                            headers = {"Referer": f"https://roblox.com/games/{placeId}", "Origin": "https://roblox.com", "User-Agent": "Roblox/WinInet"}
                            )
    if not gameJoinReq.json()["queuePosition"]:
        udmux = gameJoinReq.json()["joinScript"]["UdmuxEndpoints"][0]["Address"]
        meow = udmux.split(".")
        meow[-1:] = "0"
        location = serverList[".".join(meow)]
        if "region" in location:
            location = f"{location['city']}, {location['region']['name']}, {location['country']['name']}"
        else:
            location = f"{location['city']}, {location['country']['name']}"
        instances.append(instance)
        print(f"{len(instances)}. Located at {location}. Playing: {instance['playing']}/{instance['maxPlayers']}")
    #else:
    #   print(f"Skipping {jobId}")
choice = instances[int(input("Pick: "))]
print(f"Joining {choice['id']}")
webbrowser.open(f"roblox://experiences/start?placeId={placeId}&gameInstanceId={choice['id']}")
