import mysql.connector
import json
import urllib
import requests

import config
import mod
from themeControllers import *
from windows import *
from objectclasses import *

systemdb = mysql.connector.connect(
    host="sql11.freemysqlhosting.net",
    user="sql11399413",
    password="EQ2GCCEILe",
    database="sql11399413"
)

c = systemdb.cursor(buffered=True)

#Based on IMDb's top 250 and top rated TV shows
imdbIDs = ['0805647', '0468569', '0167260', '0120737', '0133093', '0245429', '0110357', '0088763', '4154796',
           '4633694', '7286456', '8503618', '4154756', '2380307', '2096673', '0993846', '2024544', '1454029',
           '1201607', '0435761', '0892769', '0405159', '0266697', '0137523', '6751668', '1049413', '0910970'
           , '0395169', '0347149', '0266543', '0253474', '0317248', '0198781', '0211915', '0109830',
           '0110912','0108052','0097576','8579674','1950186','8613070','6966692', '1392190','2267998','0986264','0457430',
           '0434409','0096283','0088247','0086190','0083658','0080678', '4786824','8134470','0460681',
           '7569576','11794642','0413573','1190634','0944947','5171438','2442560','1520211','1844624','0386676',
           '10048342','8111088','0903747','0108778','0364845','4574334', '12361974', '9140560',  '9208876',  '5109280',
           '0770828',  '2948372', '9620292', '9770150', '6723592', '9698442', '0451279', '5363618', '0094898',
           '2395427', '9784798', '0068646', '12920838', '0448115', '1345836', '10288566', '6802400', '10813940']


def getUser2Id(user2):
    global systemdb
    c = systemdb.cursor(buffered=True)
    c.execute('''SELECT userId FROM users WHERE username='{}';'''.format(user2))
    user2Id = c.fetchall()
    user2Id = user2Id[0][0]


    c.close()

    return user2Id






print(config.system)
#Main Program


ShowLoginScreen()
