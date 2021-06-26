import configparser
import sys
import discord
import redis

token = ""
redis_host = ""
redis_port = 6379
redis_pass = ""
proxylist = []

client = discord.Client()


def checkconfig():
    try:
        file = open("config.ini")
        file.close()
    except IOError:
        print("Config file doesn't exist yet, making one...")
        config = configparser.ConfigParser()
        config['bot'] = {'token': ''}
        config['redis'] = {'host': '', 'port': '', 'pass': ''}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        print("Config created! stopping...")
        sys.exit(0)
    print("Config exists. continuing...")


# load config
def loadconfig():
    global token, redis_port, redis_host, redis_pass
    config = configparser.ConfigParser()
    config.read("config.ini")
    # krijg de ip en api-key variabelen
    token = config["bot"]["token"]
    redis_host = config["redis"]["host"]
    redis_port = config["redis"]["port"]
    redis_pass = config["redis"]["pass"]


# get proxies
def getproxies():
    global proxylist
    proxyhash = redis.hgetall("heartbeats")
    for key in proxyhash:
        proxy = key.decode("utf8")
        if proxy not in proxylist:
            proxylist.append(proxy)


# get playerlist
async def getplayercount():
    playercount = 0
    for key in proxylist:
        proxyname = "proxy:" + key + ":usersOnline"
        playerlist = redis.smembers(proxyname)
        playercount = playercount + len(playerlist)
        print(len(playerlist))
        print(playercount)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                           name=str(playercount) + " spelers"))


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    getproxies()
    await getplayercount()

# start
if __name__ == "__main__":
    checkconfig()
    loadconfig()
    redis = redis.StrictRedis(host=redis_host, port=redis_port, db=0, password=redis_pass)
    client.run(token)
