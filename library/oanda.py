


#Load Standard Packages
import pandas as pd
import json
from datetime import timezone, datetime
#Load OANDA Packges
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.accounts as accounts



# Retrieves the latest datetime for the selected contract
def OANDA_Connection_Latest(contract, timeframe, client):
    params = {"count": 1, "granularity": timeframe}
    r = instruments.InstrumentsCandles(instrument=contract, params=params)
    client.request(r)
    r.response['candles'][0]['mid']
    r.response['candles'][0]['time']
    r.response['candles'][0]['volume']
    dat = []
    for oo in r.response['candles']:
        dat.append([oo['time']])
        df = pd.DataFrame(dat)
        df.columns = ['time']
        #Convert To Float
        df["time"] = pd.to_datetime(df["time"], unit='ns')
        latest_datetime = int((df['time'].iloc[0]).replace(tzinfo=timezone.utc).timestamp())
    return latest_datetime


# Batch download of the selected contract's data.
def OANDA_Connection(contract, timeframe, start_unix, client, num_records=5000):
    params = {"from": start_unix, "count": num_records, "granularity": timeframe}
    r = instruments.InstrumentsCandles(instrument=contract, params=params)
    client.request(r)
    # r.response['candles'][0]['mid']
    # r.response['candles'][0]['time']
    # r.response['candles'][0]['volume']
    dat = []
    for oo in r.response['candles']:
        dat.append([oo['time'], oo['mid']['o'], oo['mid']['h'], oo['mid']['l'], oo['mid']['c'], oo['volume'], oo['complete']])
        df = pd.DataFrame(dat)
        df.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'complete']
        #Convert To Float
        df["time"] = pd.to_datetime(df["time"], unit='ns')
        df["open"] = pd.to_numeric(df["open"], downcast="float")
        df["high"] = pd.to_numeric(df["high"], downcast="float")
        df["low"] = pd.to_numeric(df["low"], downcast="float")
        df["close"] = pd.to_numeric(df["close"], downcast="float")
    return df






######################################################################################################
#[1] dev download data function
######################################################################################################

def getInstrumentsList(api, accountID, type=None):
    '''
    api: oandapyV20.API(access_token=APIKEY,environment="live")
    accountID: string
    type: 'CFD', 'METAL', 'CURRENCY'
    
    Some examples: 
        instruments_cur = getInstrumentsList(type="CURRENCY", api=api, accountID=ACCOUNT_ID)
        instruments_cfd = getInstrumentsList(type="CFD", api=api, accountID=ACCOUNT_ID)
        instruments_metal = getInstrumentsList(type="METAL", api=api, accountID=ACCOUNT_ID)
        instruments_all  = getInstrumentsList(api=api, accountID=ACCOUNT_ID)
    '''
    params={"instruments": None}
    r = oandapyV20.endpoints.accounts.AccountInstruments(accountID=accountID, params = params)

    instruments = []
    try:
        rv = api.request(r)
    except oandapyV20.exceptions.V20Error as err:  
        print("Error:", r.status_code, err)
    else:
        print("The result:")
        res = json.dumps(rv, indent=2)
        result = json.loads(res)
        if type is not None:
            for instrument in result['instruments']:
                if (instrument['type'] == type):
                    instruments.append([instrument['name'], instrument['displayName']])
        else:
            for instrument in result['instruments']:
                instruments.append([instrument['name'], instrument['displayName']])

    return instruments




def DownloadData(contract, timeframe, start_datetime, client, retry_limit=3):
    '''
    Parameters
    ----------
    contract : str
    timeframe : str
        oanda's string input for the candle's granularity. E.g. M5, M30, H1.
    start_datetime : datetime64[ns, UTC]
    client : oandapyV20.oandapyV20.API
        oanda's client object
    retry_limits : int
        defines number of tries for each batch to download data before error is raised
    '''
    start_unix = int(start_datetime.replace(tzinfo=timezone.utc).timestamp())
    latest_unix = OANDA_Connection_Latest(contract=contract, timeframe=timeframe, client=client)
    active_unix = start_unix
    data_list = []

    batch_counter = 0
    while active_unix < latest_unix:
        failure_counter = 0
        success = False
        while failure_counter < retry_limit:
            try:
                df = OANDA_Connection(contract=contract, timeframe=timeframe, start_unix=active_unix, client=client)
            except Exception as error:
                failure_counter += 1
                print('ERROR', error)
                print(f"Warning. Download FAILED! || Batch Counter: {batch_counter} Failed Attempts: {failure_counter}")
                print(f"Will retry: {failure_counter}/{retry_limit}.")
                continue
            else:
                success = True
                batch_counter += 1
                print(f"Download Successful! || Batch Counter: {batch_counter} Failed Attempts: {failure_counter}")
                failure_counter = 999
        
        if not success:
            last_row = df.tail(1)
            active_unix = int((last_row['time'].iloc[0]).replace(tzinfo=timezone.utc).timestamp())
            data_list.append(df)
            exec(f"raise Exception('Data download Failed! Failure occurred in Batch: {batch_counter}')")
        
        last_row = df.tail(1)
        active_unix = int((last_row['time'].iloc[0]).replace(tzinfo=timezone.utc).timestamp())
        data_list.append(df)
        print(f"Data seconds remaining: {latest_unix-active_unix}")
  
    return pd.concat(data_list, axis=0, ignore_index=True).drop_duplicates().query('complete==True').drop(columns='complete')
