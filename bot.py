
import requests
import config
import slackclient
import time
import re
import os
import datetime
import dateutil.parser
import random
from sutime import SUTime

MONTREAL = ('45.4981', '-73.5596')

url = 'https://api.darksky.net/forecast/%s/%s,%s' % (config.DARK_SKY_KEY, MONTREAL[0], MONTREAL[1])

bot = slackclient.SlackClient(config.SLACK_BOT_TOKEN)
bot_id = config.SLACK_BOT_ID

jar_files = os.path.join(os.path.dirname(__file__), 'jars')
sutime = SUTime(jars=jar_files)


def validates_message(event):
    try:
        if event['type'] == 'message' and event['user'] != bot_id and re.match(r'.*charlie.*weather.*', event['text'].lower()):
            return True
        elif event['type'] == 'message' and event['user'] != bot_id and re.match(r'.*charlie bit me.*', event['text'].lower()):
            charlie_bit_me(event['channel'])
        elif event['type'] == 'message' and event['user'] != bot_id and re.match(r'.*(hi|hello|hey|yo|heya|sup).*charlie.*', event['text'].lower()):
            hi(event['channel'])
    except:
        pass


def handle_message(message, channel):

    now = datetime.datetime.now()
    now_iso = now.isoformat(timespec='seconds')
    times = sutime.parse(message.lower(), reference_date=now_iso)

    if times:
        time_type = times[0]['type']
        if time_type == 'TIME' or time_type == 'DATE':
            if times[0]['value'] == 'PRESENT_REF':
                message = get_weather(now_iso)
            elif len(times[0]['value']) == 10:
                message = get_weather(times[0]['value'] + 'T' + now.strftime('%H:%M:%S'))
            else:
                message = get_weather(times[0]['value'])
        elif time_type == 'DURATION':
            new_time = now
            for t in times:
                duration = compute_duration(now, t['value'])
                if duration:
                    new_time = new_time + duration
            if duration and new_time != now:
                message = get_weather(new_time.isoformat(timespec='seconds'))
            else:
                message = "Bad time request!"
        else:
            message= "Bad request!"
    else:
        message = "When?"

    send_message(message=message, channel=channel)


def compute_duration(now, duration):
    types_of_durations = {'S': 'seconds', 'M': 'minutes', 'H': 'hours', 'D': 'days'}
    if duration[1] == 'T':
        attr = {types_of_durations[duration[-1]]: int(re.search(r'\d+', duration).group(0))}
        return datetime.timedelta(**attr)
    elif duration[-1] == 'D':
        attr = {types_of_durations[duration[-1]]: int(re.search(r'\d+', duration).group(0))}
        return datetime.timedelta(**attr)
    elif duration[-1] == 'W':
        attr = {types_of_durations['D']: 7 * int(re.search(r'\d+', duration).group(0))}
        return datetime.timedelta(**attr)
    elif duration[-1] == 'M':
        attr = {types_of_durations['D']: 30 * int(re.search(r'\d+', duration).group(0))}
        return datetime.timedelta(**attr)
    elif duration[-1] == 'Y':
        attr = {types_of_durations['D']: 365 * int(re.search(r'\d+', duration).group(0))}
        return datetime.timedelta(**attr)
    else:
        return None


def get_weather(date_time):
    new_url = url + ',%s?units=ca&exclude=%s,%s,%s,%s' % (date_time, 'minutely', 'hourly', 'alerts', 'flags')
    response = requests.get(new_url)
    forecast = response.json()
    date_time_object = dateutil.parser.parse(date_time)

    query_params = (
            date_time_object.strftime('%b %d, %Y %H:%M'),
            forecast['currently']['summary'],
            forecast['currently']['apparentTemperature'],
            date_time_object.strftime('%b %d, %Y'),
            forecast['daily']['data'][0]['summary'],
            forecast['daily']['data'][0]['apparentTemperatureMax'],
            forecast['daily']['data'][0]['apparentTemperatureMin']
        )

    return '*%s*: %s\nFeels like _%s_ °C\n\n*%s*: %s\nFeels like _%s_ °C (High) and _%s_ °C (Low)' % query_params


def charlie_bit_me(channel):
    bot.api_call('chat.postMessage', channel=channel, text=':cry:', as_user=True)


def hi(channel):
    greetings = ['Hi!', 'Hello!', 'Hey!', 'Yo!']
    bot.api_call('chat.postMessage', channel=channel, text=random.choice(greetings), as_user=True)


def send_message(message, channel):
    bot.api_call('chat.postMessage', channel=channel, text=message, as_user=True)


def run():
    if bot.rtm_connect(with_team_state=False):
        print('Connected')
        while True:
            for event in bot.rtm_read():
                print(event)
                if validates_message(event):
                    handle_message(message=event.get('text'), channel=event.get('channel'))
            time.sleep(1)
    else:
        print('Connection Failed')

if __name__=='__main__':
    run()
