from flask import current_app
import requests
from datetime import datetime, timedelta

def get_latest_rate(from_cur, to_cur):
    headers = {"accept": "application/json"}
    exrate_url = "{}/fetch-one?api_key={}&from={}&to={}".format(current_app.config['FAST_FOREX_API_URL'], current_app.config['FAST_FOREX_API_KEY'], from_cur, to_cur)
    response = requests.get(exrate_url, headers=headers)
    return response

def get_rsi_value(from_cur, to_cur, duration):
    end_date = datetime.now()
    if duration.endswith('d'):   
        start_date = end_date - timedelta(days=int(duration[:-1]))
    elif duration.endswith('m'):   
        start_date = end_date - relativedelta(months=int(duration[:-1]))
    elif duration.endswith('y'):    
        start_date = end_date - relativedelta(years=int(duration[:-1]))
    start_date = start_date - timedelta(days=14)

    headers = {"accept": "application/json"}
    time_series_url = "{}/time-series?api_key={}&from={}&to={}&start={}&end={}".format(current_app.config['FAST_FOREX_API_URL'], current_app.config['FAST_FOREX_API_KEY'], from_cur, to_cur, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    response=None
    # If currency for current date is not updated, thus need to use the previous date as latest currency
    while not response or 'future' in response.text:
        response = requests.get(time_series_url, headers=headers)

        if response.status_code == 200:
            json_obj = response.json()  
            results= json_obj['results']
            dates =  list(list(results.values())[0].keys())
            exchange_rates = list(list(results.values())[0].values())
            # print("Dates:", list(dates))
            # print("Exchange Rates:", list(exchange_rates))

            changes = []
            for i in range(1, len(exchange_rates)):
                if exchange_rates[i] - exchange_rates[i - 1] != 0:
                    change = (exchange_rates[i] - exchange_rates[i - 1])/exchange_rates[i-1] * 100
                else:
                    change = 0
                changes.append(change)
            # print("Changes:", list(changes))

            rsi_values = []
            for i in range(14, len(changes)+1):
                gain = 0
                loss = 0
                for j in range(i-14, i):
                    if  changes[j] > 0:
                        gain += changes[j]
                    else:
                        loss -= changes[j]
                average_gain = gain / 14
                average_loss = loss / 14
                relative_strength = average_gain/average_loss
                rsi = 100-(100/(1+relative_strength))
                # print('Avg gain for '+ str(i) + ': ' + str(average_gain))
                # print('Avg loss for '+ str(i) + ': ' + str(average_loss))
                # print('RS for '+ str(i)  + ': ' + str(relative_strength))
                # print('RSI for '+ str(i)  + ': ' + str(rsi))
                rsi_values.append(rsi)
            changes = round(rsi_values[-1] - rsi_values[0] / rsi_values[0] * 100,4)
            dates = dates[14:]
            rounded_rsi_values = [round(rsi, 1) for rsi in rsi_values]
            return changes, dates, rounded_rsi_values
        
        else:
            if 'future' in response.text:
                end_date = end_date - timedelta(days=1)
                print(f"Error: {response.status_code} - {response.text}")