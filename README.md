# 🎵 Private Discord Music Bot

A Discord music bot with **owner-controlled access**: only members the server owner
authorizes can control playback. Built for small servers that want a shared music bot
without letting anyone hijack the queue.

## Why I Built This

I own a Discord server that grew from a group of friends to over 100 members, mostly friends of friends.
With that growth came pranks: the public music bots we relied on kept getting removed or hijacked, and they
crashed often enough that music barely worked. Waiting on someone else's dev team for fixes wasn't working,
so I built my own bot where only members I authorize can control playback, and where I can fix bugs myself
as soon as they show up.

## Features

- **Access control:** the owner grants and revokes permission per user, stored in SQLite
- **YouTube playback:** search by name or URL, streamed into voice via yt-dlp and FFmpeg
- **Per-server queues:** each server keeps its own queue, with auto-advance to the next song
- **Slash commands:** native Discord `/` commands with descriptions

## Commands

| Command | Who | Description |
|---|---|---|
| `/authorize @user` | Owner | Grant a user access to the bot |
| `/revoke @user` | Owner | Remove a user's access |
| `/authorized` | Owner | List all authorized users |
| `/join` | Authorized | Join your current voice channel |
| `/play <song>` | Authorized | Search YouTube and add a song to the queue |
| `/queue` | Authorized | Show the current queue |
| `/pause` / `/resume` | Authorized | Pause or resume playback |
| `/skip` | Authorized | Skip the current song |
| `/stop` | Authorized | Stop playback and clear the queue |
| `/leave` | Authorized | Disconnect from voice |

## Tech Stack

Python · discord.py 2.x · yt-dlp · FFmpeg · aiosqlite (SQLite)

## Project Structure

    bot.py               # Entry point: intents, startup, slash command sync
    cogs/
      music.py           # Playback, queue management, voice commands
      owner.py           # Owner-only access control commands
    database/
      database.py        # Async SQLite helpers for authorized users

## Setup

1. Install Python 3.10+, FFmpeg, and Opus (macOS: `brew install ffmpeg opus`)
2. Clone the repo and install dependencies:

       pip install -r requirements.txt

3. Create `config.py` in the project root:

       TOKEN = "your-discord-bot-token"
       OWNER_ID = 123456789012345678  # your Discord user ID

4. Run the bot:

       python bot.py

## Design Notes

Authorization lives in a SQLite table keyed by Discord user ID, so access survives
restarts. Every playback command checks it before acting, and owner commands verify
the caller against `OWNER_ID`.

## Roadmap

- [ ] Load the Opus library cross-platform (currently uses a macOS Homebrew path)
- [ ] Per-server owners instead of a single global owner
- [ ] Now-playing embeds with song duration and progress
