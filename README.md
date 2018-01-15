# Charlie
Charlie is a Slack bot that gets weather updates. It uses the Dark Sky API (free 1,000 calls per day) for retrieving weather forecasts. It uses the Stanford CoreNLP's Temporal Tagger (SUTime) to process time queries. CoreNLP is developed in Java, so a Python port is used here. NLTK is used for non-temporal NLP. Charlie uses Google's Geocoding API to transform locations into coordinates (free 2,500 calls per day).

## Instructions
Install the packages
```
sudo pip install requests slackclient sutime dateutil geopy nltk
```

Download Java SE (JDK)
```
http://www.oracle.com/technetwork/java/javase/downloads/index.html
```

Download Maven
```
https://maven.apache.org/download.cgi
```

Install Maven using the instructions below
```
https://maven.apache.org/install.html
```

Install all Java dependencies from pom.xml using Maven
```
mvn dependency:copy-dependencies -DoutputDirectory=./jars
```

Make an account on DarkSky and get the API token
```
https://darksky.net
```

Create a Slack bot
```
1. Go to https://my.slack.com/services/new/bot
2. Write "charlie" in the username box
3. Customize your bot account and copy the API Token
```

Log into you Google account and get the Geocoding API key
```
https://developers.google.com/maps/documentation/geocoding/start
```

Create a `config.py` file with the format of `example.config.py` and fill in the API tokens
```
DARK_SKY_KEY = '<put API key here>'
SLACK_BOT_TOKEN = '<put API key here>'
GOOGLE_MAPS_KEY = '<put API key here>'
```

Run Charlie
```
python charlie.py
```

<a href="https://darksky.net"><img src="https://darksky.net/dev/img/attribution/poweredby-oneline.png" width="200"></a>
