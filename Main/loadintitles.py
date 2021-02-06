##API Key
#http://www.omdbapi.com/?i=ttIDHere

import requests
import json
import random  
import urllib
from queue_class import *
from titles_class import * 

#Based on IMDb's top 250 and top rated TV shows
imdbIDs = ['0805647', '0468569', '0167260', '0120737', '0133093', '0245429', '0110357', '0088763', '4154796',
           '4633694', '7286456', '8503618', '4154756', '2380307', '2096673', '0993846', '2024544', '1454029',
           '1201607', '0435761', '0892769', '0405159', '0266697', '0137523', '6751668', '1049413', '0910970'
           , '0395169', '0347149', '0266543', '0253474', '0317248', '0198781', '0211915', '0109830',
           '0110912','0108052','0097576','8579674','1950186','8613070','6966692', '1392190','2267998','0986264','0457430',
           '0434409','0096283','0088247','0086190','0083658','0080678', '4786824','8134470','0460681',
           '7569576','11794642','0413573','1190634','0944947','5171438','2442560','1520211','1844624','0386676',
           '10048342','8111088','0903747','0108778','0364845','4574334']

def setUpQueue(amount):
    #The value of the drop down menu is passed into the function to define the maxsize of the queue
    global imdbIDs, Movie, TVShow
    amount = int(amount)
    title_queue = TitlePriorityQueue(amount)

    track= 0

    while track < amount:
        chosen_title = random.choice(imdbIDs)
        imdbIDs.remove(chosen_title)

        
        #scraps the data of the imdb
        currentTitle = requests.get("http://www.omdbapi.com/?i=tt" + chosen_title + "&apikey=8598b952")

        #Titles the user will rate
        currentTitle = currentTitle.text
        currentTitle = json.loads(currentTitle)
        currentTitle['Genre'] = currentTitle['Genre'].split(", ")

        #The title data is instaniated into an object based on if it is a movie or tv show (this has already been categorised by the API)

        if currentTitle['Type'] == "movie":

            titleobject = Movie(currentTitle['Poster'], currentTitle['Title'], currentTitle['Genre'])

        elif currentTitle['Type'] == "series":
            titleobject = TVShow(currentTitle['Poster'], currentTitle['Title'], currentTitle['Genre'])
            

        title_queue.enqueue(titleobject)

        track += 1

    #the title queue object is passed back into the ratings window interface
    print(title_queue)
    return title_queue


    

    

