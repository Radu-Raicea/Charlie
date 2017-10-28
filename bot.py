
import requests
import config
import slackclient
import time
import re

MONTREAL = ('45.4981', '-73.5596')

url = 'https://api.darksky.net/forecast/%s/%s,%s?units=ca' % (config.DARK_SKY_KEY, MONTREAL[0], MONTREAL[1])

bot = slackclient.SlackClient(config.SLACK_BOT_TOKEN)
bot_id = config.SLACK_BOT_ID


def validates_message(event):
    if event['type'] == 'message' and event['user'] != bot_id and re.match(r'.*charlie.*weather.*', event['text'].lower()):
        return True
    elif event['type'] == 'message' and event['user'] != bot_id and re.match(r'.*charlie bit me.*', event['text'].lower()):
        charlie_bit_me(event['channel'])


def handle_message(message, channel):

    message = message.lower()

    if re.match(r'.*(today|day).*', message):
        message = today_weather()
    elif re.match(r'.*(hour).*', message):
        message = next_hour_weather()
    else:
        message = current_weather()
        
    send_message(message=message, channel=channel)


def current_weather():
    new_url = url + '&exclude=%s,%s,%s,%s,%s' % ('minutely', 'hourly', 'daily', 'alerts', 'flags')
    response = requests.get(new_url)
    forecast = response.json()
    return '[{"color": "#36a64f", "title": "Current Weather", "text": "%s\nFeels like %s"}]' % (forecast['currently']['summary'], forecast['currently']['apparentTemperature'])


def next_hour_weather():
    new_url = url + '&exclude=%s,%s,%s,%s,%s' % ('currently', 'minutely', 'daily', 'alerts', 'flags')
    response = requests.get(new_url)
    forecast = response.json()
    return '[{"color": "#36a64f", "title": "Weather in the Next Hour", "text": "%s\nFeels like %s"}]' % (forecast['hourly']['data'][0]['summary'], forecast['hourly']['data'][0]['apparentTemperature'])


def today_weather():
    new_url = url + '&exclude=%s,%s,%s,%s,%s' % ('currently', 'minutely', 'hourly', 'alerts', 'flags')
    response = requests.get(new_url)
    forecast = response.json()
    return '[{"color": "#36a64f", "title": "Today\'s Weather", "text": "%s\nFeels like %s (High) and %s (Low)"}]' % (forecast['daily']['data'][0]['summary'], forecast['daily']['data'][0]['apparentTemperatureMax'], forecast['daily']['data'][0]['apparentTemperatureMin'])


def charlie_bit_me(channel):
    bot.api_call('chat.postMessage', channel=channel, text=':cry:', as_user=True)


def send_message(message, channel):
    bot.api_call('chat.postMessage', channel=channel, attachments=message, as_user=True)


def run():
    if bot.rtm_connect(with_team_state=False):
        print('Connected')
        while True:
            for event in bot.rtm_read():
                if validates_message(event):
                    handle_message(message=event.get('text'), channel=event.get('channel'))
            time.sleep(1)
    else:
        print('Connection Failed')

if __name__=='__main__':
    run()
