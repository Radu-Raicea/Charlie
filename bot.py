
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
    if event['type'] == 'message' and event['user'] != bot_id and re.match(r'.*weather.*', event['text'].lower()):
        return True


def handle_message(message, user, channel):
    response = requests.get(url)
    forecast = response.json()
    message = '*Current Weather*\n%s\nFeels like %s' % (forecast['currently']['summary'], forecast['currently']['apparentTemperature'])
    send_message(message=message, channel=channel)


def send_message(message, channel):
    bot.api_call('chat.postMessage', channel=channel, text=message, as_user=True)


def run():
    if bot.rtm_connect(with_team_state=False):
        print('Connected')
        while True:
            for event in bot.rtm_read():
                if validates_message(event):
                    handle_message(message=event.get('text'), user=event.get('user'), channel=event.get('channel'))
            time.sleep(1)
    else:
        print('Connection Failed')

if __name__=='__main__':
    run()
