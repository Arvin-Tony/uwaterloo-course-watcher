import os
import time
import discord
import requests
from bs4 import BeautifulSoup
import asyncio
from flask import Flask
from threading import Thread

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
USER_ID = int(os.getenv("MY_DISCORD_ID"))

client = discord.Client(intents=discord.Intents.default())

# List of course URLs to monitor
COURSE_URLS = {
    "BET 210":
    "https://classes.uwaterloo.ca/cgi-bin/cgiwrap/infocour/salook.pl?level=under&sess=1255&subject=BET&cournum=210",
    "CLAS 202":
    "https://classes.uwaterloo.ca/cgi-bin/cgiwrap/infocour/salook.pl?level=under&sess=1255&subject=CLAS&cournum=202",
    "ECON 101 Online":
    "https://classes.uwaterloo.ca/cgi-bin/cgiwrap/infocour/salook.pl?level=under&sess=1255&subject=ECON&cournum=101",
    "ECON 102 Online":
    "https://classes.uwaterloo.ca/cgi-bin/cgiwrap/infocour/salook.pl?level=under&sess=1255&subject=ECON&cournum=102",
    "EARTH 123":
    "https://classes.uwaterloo.ca/cgi-bin/cgiwrap/infocour/salook.pl?level=under&sess=1255&subject=EARTH&cournum=123",

    # can add more if needed
}


def check_seats(course, url):
    print(f"Checking seats for {course}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')

    if not table:
        return None

    rows = table.find_all('tr')[1:]  # skip the header row
    subInds = 0
    LOC_COL, CAP_COL, ENRL_COL = 4, 8, 9
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= ENRL_COL - subInds:

            location = cols[LOC_COL - subInds].text.strip()
            # I only want to consider the online sections for now
            if location == "ONLN  ONLINE":

                CAP = cols[CAP_COL - subInds].text.strip()
                ENRL = cols[ENRL_COL - subInds].text.strip()

                if CAP.isdigit() and ENRL.isdigit():
                    CAP, ENRL = int(CAP), int(ENRL)
                    available = CAP - ENRL
                    return (available, CAP, ENRL)
                break

            else:
                subInds = 2
                # for some reason, based on how the posted table is formatted,
                # the column indices change when there is an offering where course is not online

    return (0, None, None)


async def seat_watcher():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    already_alerted = set()

    last_msg_time = 0  # Track last message time

    while not client.is_closed():
        status_message = ""

        has_open_seat = False
        available_courses = ""
        for course, url in COURSE_URLS.items():
            try:
                available, cap, enrl = check_seats(course, url)
                if available:
                    has_open_seat = True

                    available_courses += course + "\n"
                    status_message += (
                        f"**{course} has {available} seat(s) available!**\n"
                        f"Capacity: {cap}, Enrolled: {enrl}\n"
                        f"<@{USER_ID}>\n{url}\n\n")

                    already_alerted.add(course)
                elif available == 0:
                    if course in already_alerted:
                        already_alerted.remove(course)

                    status_message += (f"**{course} is full.**\n"
                                       f"Capacity: {cap}, Enrolled: {enrl}\n"
                                       f"{url}\n\n")
            except Exception as e:
                print(f"Error checking {course}: {e}")

        now = time.time()

        if has_open_seat:
            # immediately send a message when seats are available
            prepend_msg = f"**!!!! Seats available!** See details below: <@{USER_ID}> !!!! \n\n"
            prepend_msg += f"**Available courses:**\n{available_courses}\n"
            status_message = prepend_msg + status_message
            await channel.send(status_message)
            await asyncio.sleep(1.5)
            await channel.send("CHECK DISCORD!!!!")
            await asyncio.sleep(1.5)
            await channel.send("OPEN LINKS!!!!")
            await asyncio.sleep(1.5)
            await channel.send("SWAP COURSE!!!!")
            await asyncio.sleep(2.5)
            await channel.send(f"CHECK NOW <@{USER_ID}> !!!!")
            last_msg_time = now
        else:
            # Only message "all full" every 15 minutes, also when first run
            prepend_msg = "**No seats available!** \n\n"
            status_message = prepend_msg + status_message
            if last_msg_time == 0 or now - last_msg_time >= 900:  # 900 seconds = 15 minutes
                await channel.send(status_message)
                last_msg_time = now

        await asyncio.sleep(60)  # wait 1 minute to check courses again


# Flask app for keeping the server alive
app = Flask('')


@app.route('/')
def home():
    return "UWaterloo Course Watcher is alive! Server is running!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.daemon = True  # Ensure the thread stops when the main program stops
    t.start()


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    # Start the seat watcher once the bot is logged in and ready
    client.loop.create_task(seat_watcher())


# Start everything
keep_alive()
client.run(TOKEN)
