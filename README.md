# 🎓 UWaterloo Course Seat Watcher

This is a Discord bot that monitors course enrollment at the University of Waterloo and alerts me when a seat opens up in a list of specified courses.

## 📌 Features

- ✅ Periodically checks selected UWaterloo courses for open seats
- 🔔 Sends notifications to a Discord channel I made
- 👤 Tags my Discord user when a seat becomes available
- 🌐 Hosted with a keep-alive Flask server (Replit-compatible)
- 🛡️ Secure setup using environment variables (`.env` file)

## 🚀 How It Works

1. Scrapes course enrollment data from the UWaterloo course offerings site using `BeautifulSoup`.
2. Parses enrollment tables for each course.
3. Sends alerts to my Discord channel and pings me when a seat becomes available.
4. Posts regular updates even if seats are full.

## 🛠 Tech Stack

- Python
- Discord.py
- BeautifulSoup (for HTML parsing)
- Flask (for uptime monitoring)
- Replit (hosting + keep-alive)
- UptimeRobot (to keep Replit alive 24/7)
