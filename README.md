# _ChillBot_
![ChillSynth Badge](https://img.shields.io/discord/488405912659427358?color=ff4000&label=ChillSynth&logo=discord&logoColor=%23fff&style=for-the-badge)
## The in-house Discord bot made for the [ChillSynth Discord](https://chillsynth.com/discord) server

## Release Versions:
![badge](https://img.shields.io/badge/V5-TBD-%23EC2D2B?style=for-the-badge)
![badge](https://img.shields.io/badge/Release%20Date-TBD-%23fff?style=for-the-badge)

![badge](https://img.shields.io/badge/Server%20Backup%20System%20(TBD)-v5-%23EC2D2B?style=for-the-badge)
### \> - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - <
![badge](https://img.shields.io/badge/V4-In%20Beta-%232e8fff?style=for-the-badge)
![badge](https://img.shields.io/badge/Release%20Date-Fall%20/%20Winter%202024-%23fff?style=for-the-badge)

![badge](https://img.shields.io/badge/Ticketing%20system%20for%20members%20using%20threads-Not%20Started-%23ff4000?style=for-the-badge)\
![badge](https://img.shields.io/badge/Appeal%20process%20server%20link-Not%20Started-%23ff4000?style=for-the-badge)\
![badge](https://img.shields.io/badge/SoundCloud%20x%20Discord%20Link%20for%20Feedback%20Streams-Not%20Started-%23ff4000?style=for-the-badge)
### \> - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - <
![badge](https://img.shields.io/badge/V3-Released-%2300ff80?style=for-the-badge)
![badge](https://img.shields.io/badge/Release%20Date-March%202024-%23fff?style=for-the-badge)

![badge](https://img.shields.io/badge/Revamp%20Feedback%20Stream%20setup%20w%2F%20queue-Complete-%2300ff80?style=for-the-badge)\
![badge](https://img.shields.io/badge/Update%20auto--emoji%20to%20automate%20new%20emojis-Complete-%2300ff80?style=for-the-badge)\
![badge](https://img.shields.io/badge/Database%20integration%20for%20logs%20and%20functionality-Complete-%2300ff80?style=for-the-badge)

[//]: # ( RED    - Not Started    : ff4000 )
[//]: # ( ORANGE - In Progress    : ffbf00 )
[//]: # ( GREEN  - Complete       : 00ff80 )
[//]: # ( BLUE   - In Beta        : 0080ff )

## Running locally
Copy `.env.example` to `.env`  
Put your bot token in the `DISCORD_CLIENT_SECRET` variable  
The `config.json` config is active while running locally

Make sure you have `make` installed  
Run `make run/live`.  
Now you have auto reloading when changing code files!

## Running in the dev environment
Put your bot token in Github the actions secret `DISCORD_DEV_CLIENT_SECRET`  
Simply push your code to the develop branch and it will auto deploy in about a minute  
The `config.dev.json` config is active while running in the dev environment

## Running in the production environment (not setup yet)
Put your bot token in Github the actions secret `DISCORD_PROD_CLIENT_SECRET`  
~~Simply push your code to the main branch and it will auto deploy in about a minute~~  
Add your new version with changes to CHANGELOG.md  
Make a pull request from develop into main  
Complete that PR and the new version will get auto tagged and released on github and deployed to the prod environment  
The `config.prod.json` config is active while running in the prod environment