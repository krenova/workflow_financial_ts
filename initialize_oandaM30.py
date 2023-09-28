
######################################################################################################
import json

import library.encryptPW as encr
import library.oanda as oanda
import oandapyV20

from datetime import datetime

import pandas as pd

from pymongo import MongoClient
######################################################################################################


encr.pw_encryption()


# Oanda connection
pw_dir = json.load(open("./config/config.json"))['directory']['pw']
ACCOUNT_ID = encr.pw_decrypt("oandaAccntID")
APIKEY = encr.pw_decrypt("oanda")
API = oandapyV20.API(access_token=APIKEY ,environment="live")


# Mongodb connection
client_db = MongoClient("mongodb://localhost:27017")



# Pull list of instruments
instruments_all  = oanda.getInstrumentsList(api=API, accountID=ACCOUNT_ID)
instruments_currency  = oanda.getInstrumentsList(api=API, accountID=ACCOUNT_ID, type='CURRENCY')



# Extraction Parameters
start_datetime = datetime(2017, 1, 1)
timeframe = "M30"



# If no 30min collection, create collection
if not any([x=="oandaM30" for x in client_db.financial_ts.list_collection_names()]):

    client_db.financial_ts.create_collection(
        'oandaM30',
        timeseries={
            'timeField':'time',
            'metaField': 'contract',
            'granularity': 'minutes'
        }
    )



# Extract data from oanda and push into mongoDB
for i in range(0,len(instruments_currency)):

    contract = instruments_currency[i][0]
    
    print(f"\n==============================================================")
    print(f"   Current contract: {contract}; Current iteration: {i+1} of {len(instruments_currency)}")
    print(f"==============================================================\n")

    # Download Data
    df = oanda.DownloadData(contract=contract,timeframe=timeframe, start_datetime=start_datetime, client=API)

    # Insert data into collection
    try:
        client_db.financial_ts.oandaM30.insert_many(
            df.\
                assign(
                    contract = contract
                ).\
                to_dict(orient='records')
        )
    except Exception as error:
        print('ERROR', error)
        print(f"Insertation into mongoDB failed.")
    else:
        continue




results = client_db.financial_ts.oandaM30.aggregate([
    { "$group": { "_id": "$contract", "contracts": { "$addToSet": "$contract" } } },
    { "$unwind": "$contracts" },
    { "$replaceRoot": { "newRoot": { "contract": "$contracts" } } }
])


pd.DataFrame(list(results))



results = client_db.financial_ts.oandaM30.aggregate([
    { "$group": { "_id": "$contract", "count": { "$sum": 1 } } },
    { "$project": { "_id": 0 ,"contract": "$_id", "count": 1} }
])


pd.DataFrame(list(results))