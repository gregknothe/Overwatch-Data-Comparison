import requests
import pandas as pd
import datetime as dt
import cv2
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import urllib
import datetime
import os

def timeToMinutes(time):
    t = time.split(":")
    minutes = 0
    if len(t) == 3:
        minutes += float(t[0]) * 60
        minutes += float(t[1])
        minutes += float(t[2]) / 60
    if len(t) == 2:
        minutes += float(t[0])
        minutes += float(t[1]) / 60
    if len(t) == 1:
        minutes += float(t[0]) / 60
    return round(minutes,2)


def per10Calculation(value, timeMinutes):
    print str(value) + " " + str(timeMinutes)
    if value == 0:
        return 0
    else:
        return round(float(value) / (float(timeMinutes)/10),2)


def userData(userName="Asome#1762", region="us", platform="pc"):
    userName = userName.replace("#", "-")
    url = "https://ow-api.com/v1/stats/"+platform+"/"+region+"/"+userName+"/complete"
    print url
    jsonFile = requests.get(url)
    data = jsonFile.json()
    return data


def heroListCreator(data):
    heroList = data["competitiveStats"]["careerStats"].keys()
    actualHeroList = []
    for hero in heroList:
        timePlayed = data["competitiveStats"]["careerStats"][hero]["game"]["timePlayed"]
        timePlayedMinutes = timeToMinutes(timePlayed)
        if timePlayedMinutes > 5:
            actualHeroList.append(hero)
        else:
            pass
    actualHeroList.remove("allHeroes")
    return actualHeroList


def heroData(data):
    heroList = heroListCreator(data)
    timePlayed,damageTotal,winPercentage,healingTotal,elimsTotal,weaponAccuracy,deathsTotal = [],[],[],[],[],[],[]
    damagePer10,elimsPer10,healingPer10,deathsPer10,timeInMinutes = [],[],[],[],[]
    for hero in heroList:
        print hero
        timeMinutes = timeToMinutes(data["competitiveStats"]["careerStats"][hero]["game"]["timePlayed"])
        timeInMinutes.append(timeMinutes)
        timePlayed.append(data["competitiveStats"]["careerStats"][hero]["game"]["timePlayed"])
        damageTotal.append(int(data["competitiveStats"]["careerStats"][hero]["combat"]["heroDamageDone"]))
        elimsTotal.append(int(data["competitiveStats"]["careerStats"][hero]["combat"]["eliminations"]))
        try:
            deathsTotal.append(int(data["competitiveStats"]["careerStats"][hero]["combat"]["deaths"]))
            deathsPer10.append(per10Calculation(int(data["competitiveStats"]["careerStats"][hero]["combat"]["deaths"]), timeMinutes))
        except Exception as e:
            deathsTotal.append(0)
            deathsPer10.append(0)
        try:
            weaponAccuracy.append(int(data["competitiveStats"]["careerStats"][hero]["combat"]["weaponAccuracy"].replace("%","")))
        except Exception as e:
            weaponAccuracy.append(0)
        try:
            winPercentage.append(int(data["competitiveStats"]["careerStats"][hero]["game"]["winPercentage"].replace("%","")))
        except Exception as e:
            winPercentage.append(0)
        try:
            healingTotal.append(int(data["competitiveStats"]["careerStats"][hero]["assists"]["healingDone"]))
            healingPer10.append(per10Calculation(int(data["competitiveStats"]["careerStats"][hero]["assists"]["healingDone"]),timeMinutes))
        except Exception as e:
            healingTotal.append(0)
            healingPer10.append(0)

        damagePer10.append(per10Calculation(int(data["competitiveStats"]["careerStats"][hero]["combat"]["heroDamageDone"]),timeMinutes))
        elimsPer10.append(per10Calculation(int(data["competitiveStats"]["careerStats"][hero]["combat"]["eliminations"]),timeMinutes))
    dataFrame = pd.DataFrame({"hero": heroList, "timePlayed": timePlayed, "damageTotal": damageTotal,
                              "winPercentage": winPercentage, "healingTotal": healingTotal, "elimsTotal": elimsTotal,
                              "weaponAccuracy": weaponAccuracy, "deathsTotal": deathsTotal, "healingPer10": healingPer10,
                              "damagePer10": damagePer10, "elimsPer10": elimsPer10, "deathsPer10": deathsPer10,
                              "timeMinutes": timeInMinutes})
    dataFrame = dataFrame[["hero", "timePlayed", "timeMinutes", "winPercentage", "damageTotal", "damagePer10", "healingTotal",
                           "healingPer10", "elimsTotal", "elimsPer10", "deathsTotal", "deathsPer10", "weaponAccuracy"]]
    return dataFrame


def userDataGeneration(userName="Asome#1762", region="us", platform="pc"):
    data =userData(userName, region, platform)
    df = heroData(data)
    tank, damage, support = 0, 0, 0
    for x in range(len(data["ratings"])):
        if data["ratings"][x]["role"] == "tank":
            tank = data["ratings"][x]["level"]
        if data["ratings"][x]["role"] == "damage":
            damage = data["ratings"][x]["level"]
        if data["ratings"][x]["role"] == "support":
            support = data["ratings"][x]["level"]
    gamesPlayed = data["competitiveStats"]["careerStats"]["allHeroes"]["game"]["gamesPlayed"]
    gamesWon = data["competitiveStats"]["careerStats"]["allHeroes"]["game"]["gamesWon"]
    file_name = userName + "_" + region + "_" + platform + "_" + str(tank) + "_" + str(damage) + "_" + str(support) + \
                "_" + str(gamesPlayed) + "_" + str(gamesWon) + "_" + str(dt.date.today()) + ".csv"
    df.to_csv(file_name)
    return df


def compareUserData(newFile, oldFile):
    newInfo = newFile.split("_")
    oldInfo = oldFile.split("_")

#    if newInfo[0] != oldInfo[0]:
#        print "The two files don't share the same account name."
#        return

    tankDelta = int(newInfo[3]) - int(oldInfo[3])
    damageDelta = int(newInfo[4]) - int(oldInfo[4])
    supportDelta = int(newInfo[5]) - int(oldInfo[5])
    gamePlayedDelta = int(newInfo[6]) - int(oldInfo[6])
    gamesWonDelta = int(newInfo[7].replace(".csv","")) - int(oldInfo[7].replace(".csv",""))


    newData, oldData = pd.read_csv(newFile), pd.read_csv(oldFile)
    newHero, oldHero = [], []
    newLoc, oldLoc = [], []
    timeMinutesDelta, damageTotalDelta, oldDamagePer10 = [], [], []
    healingTotalDelta, oldHealingPer10 = [], []
    elimsTotalDelta, oldElimsPer10 = [], []
    deathsTotalDelta, oldDeathsPer10 = [], []
    for hero in newData["hero"]:
        if hero in oldData["hero"].tolist():
            oldHero.append(hero)
            print "Shared Hero: " + hero
        else:
            newHero.append(hero)
            print "New Hero: " + hero

    for hero in oldHero:
        newLoc.append(newData["hero"].tolist().index(hero))
        oldLoc.append(oldData["hero"].tolist().index(hero))

    for x in range(len(oldHero)):
        timeMinutesDelta.append(round(newData.iat[newLoc[x], 3] - oldData.iat[oldLoc[x], 3], 2))
        damageTotalDelta.append(round(newData.iat[newLoc[x], 5] - oldData.iat[oldLoc[x], 5], 2))
        oldDamagePer10.append(oldData.iat[oldLoc[x], 6])
        healingTotalDelta.append(round(newData.iat[newLoc[x], 7] - oldData.iat[oldLoc[x], 7], 2))
        oldHealingPer10.append(oldData.iat[oldLoc[x], 8])
        elimsTotalDelta.append(round(newData.iat[newLoc[x], 9] - oldData.iat[oldLoc[x], 9], 2))
        oldElimsPer10.append(oldData.iat[oldLoc[x], 10])
        deathsTotalDelta.append(round(newData.iat[newLoc[x], 11] - oldData.iat[oldLoc[x], 11], 2))
        oldDeathsPer10.append(oldData.iat[oldLoc[x], 12])

    for hero in newHero:
        heroLoc = newData["hero"].tolist().index(hero)
        timeMinutesDelta.append(newData.iat[heroLoc, 3])
        damageTotalDelta.append(newData.iat[heroLoc, 5])
        oldDamagePer10.append(0)
        healingTotalDelta.append(newData.iat[heroLoc, 7])
        oldHealingPer10.append(0)
        elimsTotalDelta.append(newData.iat[heroLoc, 9])
        oldElimsPer10.append(0)
        deathsTotalDelta.append(newData.iat[heroLoc, 11])
        oldDeathsPer10.append(0)

    oldHero.extend(newHero)

    #Run new time and damage delta values through calcPer10 function, append to new list, and create dataset.

    print oldHero, timeMinutesDelta, damageTotalDelta
    return 0







