# QuoteBot

Discord bot to play audio samples with commands.

You can easily host your own version of the bot either by cloning this repo or using the [Docker image](https://hub.docker.com/r/jonathangriffe/quotebot).
To get more details on how to host your own QuoteBot, read the hosting section below.

## Features

Drop the samples that you want to use in the ```quotes``` folder. They should be .mp3 files.
The samples beggining by a number will be indexed with that number and you will be able to play them by using the command ```!<number>```.

Note: To play any sample, you must first join a voice chat, the bot will play the sample in your voice chat.

To play any sample, whether indexed or not, you can also use the ```!q <string>```. The bot will play the first sample containing the specified string, if one exists.

You can also add a sample that the bot will play when you first join a voice chat and haven't been active in a while by using the ```!addgreet <sample>```. The sample string should be the name of the sample file, without the ```/quotes/``` or the ```.mp3```.
Running the command again will update the sample to be played. Using ```!rmgreet``` will disable this.

Using ```!list``` will list the sample files.

Using ```!rand``` will play a random sample.

Using ```!stop``` will stop the sample currently played.

There are also two methods of adding samples that are available to any user.

The first is sending a mp3 file with the command ```!add```, which will add the sample. By default, this quote will be indexed, to disable the indexing of this quote, specify False as argument (```!add False```).

The second allows users to add samples from Youtube, by using the command ```!addyt <video_link> <start_timestamp> <end_timestamp>```. The bot will then play the extracted sample. If you want to change the sample, you can run the command again (for example to adjust the timestamps).
To save the sample, use ```!addas <name>```. The name shouldn't include a number, as the bot will automatically index it, unless disabled by adding ```False``` as a second argument.

## Hosting 

To host the bot, create a discord bot, be sure to activate all the intents on the bot screen, add the bot to your server and get the API token.

### Hosting locally

To host the bot without docker, simply clone this repository and install all the requirements, add all the samples you want in the a ```quotes``` folder inside the project files then run ```quotebot.py```:

```
git clone git@github.com:JonathanGriffe/QuoteBot.git
pip install -r requirements.txt
python quotebot.py
```

### Hosting with Docker

To host the bot with Docker, simply run the [jonathangriffe/quotebot](https://hub.docker.com/r/jonathangriffe/quotebot) image, pass your API token as the DISCORD_TOKEN environment variable and mount the folder containing your samples to /quotes:
  
```
docker run -d --name quotebot -e DISCORD_TOKEN=<your_API_token> --mount type=bind,source=<path_to_your_samples_folder>,target=/quotes jonathangriffe/quotebot
```
