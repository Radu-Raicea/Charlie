
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
bot_id = None

jar_files = os.path.join(os.path.dirname(__file__), 'jars')
sutime = SUTime(jars=jar_files)

greetings = ['Hi!', 'Hello!', 'Hey!', 'Yo!']


def validate_message(event):
    """Verifies that the Slack even is a message that is supported by the bot.

    Args:
        event (Event object): Slack event object

    """
    try:
        if event['type'] == 'message' and event['user'] != bot_id and re.match(r'.*charlie.*weather.*', event['text'].lower()):
            handle_weather_message(message=event['text'], channel=event['channel'])
        elif event['type'] == 'message' and event['user'] != bot_id and re.match(r'.*charlie bit me.*', event['text'].lower()):
            send_message(message=':cry:', channel=event['channel'])
        elif event['type'] == 'message' and event['user'] != bot_id and re.match(r'.*(hi|hello|hey|yo|heya|sup).*charlie.*', event['text'].lower()):
            send_message(message=random.choice(greetings), channel=event['channel'])
    except Exception as e:
        print(e)


def handle_weather_message(message, channel):
    """Parses temporal entity and creates correct weather message.

    Args:
        message (str): Message string containing possible temporal entity
        channel (str): Slack channel string

    """
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
                try:
                    duration = compute_duration(t['value'])
                except ValueError:
                    pass
                else:
                    new_time = new_time + duration
            if new_time != now:
                message = get_weather(new_time.isoformat(timespec='seconds'))
            else:
                message = "Bad request (time duration was 0)."

        else:
            message= "Bad request (time type not recognized)."
    else:
        message = "When?"

    send_message(message=message, channel=channel)


def compute_duration(duration):
    """Returns datetime.timedelta of SUTime duration string.

    SUTime gives durations in the following formats:
    PT4S -> 4 seconds
    PT4M -> 4 minutes
    PT4H -> 4 hours
    P4D -> 4 days
    P4W -> 4 weeks
    P4M -> 4 months
    P4Y -> 4 years

    Args:
        duration (str): SUTime duration string (look above)
    
    Returns:
        datetime.timedelta object: If duration string is valid

    Raises:
        ValueError: If the duration string is invalid

    """
    types_of_durations = {'S': 'seconds', 'M': 'minutes', 'H': 'hours', 'D': 'days'}

    if duration[1] == 'T' or duration[-1] == 'D':
        attr = {types_of_durations[duration[-1]]: extract_number(duration)}
    elif duration[-1] == 'W':
        attr = {types_of_durations['D']: 7 * extract_number(duration)}
    elif duration[-1] == 'M':
        attr = {types_of_durations['D']: 30 * extract_number(duration)}
    elif duration[-1] == 'Y':
        attr = {types_of_durations['D']: 365 * extract_number(duration)}
    else:
        raise ValueError

    return datetime.timedelta(**attr)


def extract_number(string):
    """Extracts all digits from a string.

    Args:
        string (str): A string containing digits

    Returns:
        int: Integer representation of the digits in the string

    """
    return int(re.search(r'\d+', string).group(0))


def get_weather(date_time):
    """Returns a string with the weather at a specific time.

    Args:
        date_time (str): String containing a datetime in ISO 8601 format (2017-10-29T16:12:55)

    Returns:
        str: String with weather (formatted for Slack)

    """
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


def send_message(message, channel):
    """Sends message to a Slack channel.

    Args:
        message (str): Message string
        channel (str): Slack channel string
    
    """
    bot.api_call('chat.postMessage', channel=channel, text=message, as_user=True)


def run():
    """Control loop listening to new messages."""
    if bot.rtm_connect(with_team_state=False):
        print('Connected')

        # Obtains the bot ID
        users = bot.api_call('users.list').get('members')
        for user in users:
            if 'name' in user and user.get('name') == 'charlie':
                global bot_id
                bot_id = user.get('id')

        while True:
            for event in bot.rtm_read():
                validate_message(event)
            time.sleep(1)
    else:
        print('Connection Failed')

if __name__=='__main__':
    run()
