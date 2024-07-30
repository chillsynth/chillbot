package main

import (
	"chillbot/internal/bot"
	"chillbot/internal/config"
	"chillbot/internal/greetings"
	"chillbot/internal/logging"
	"chillbot/internal/module"
	"chillbot/internal/reactions"
	youtube "chillbot/internal/youtube_feed"
	"log/slog"
	"os"

	"github.com/bwmarrin/discordgo"
)

// To add more modules, copy one of the existing modules and
// rename it to what you need, then add it here to the list
// Make sure it has an Init method that initializes all the common dependencies!
var modules = []module.Module{
	&reactions.ReactorModule{},
	&greetings.GreetingsModule{},
	&youtube.YoutubeFeedModule{},
}

func createDiscordSession() (*discordgo.Session, error) {
	token := os.Getenv("DISCORD_CLIENT_SECRET")

	discord, err := discordgo.New("Bot " + token)

	return discord, err
}

func main() {
	logger := &logging.Logger{
		Slog: slog.New(slog.NewJSONHandler(os.Stdout, nil)),
	}

	slog.SetDefault(logger.Slog)

	conf := &config.Config{}
	err := conf.Load(logger)
	if err != nil {
		logger.LogFatal("Cannot load config file %s", err.Error())
	}

	discord, err := createDiscordSession()
	if err != nil {
		logger.LogFatal("error creating Discord session %s", err)
	}

	// Initialize Bot
	bot := &bot.Bot{}
	bot.Init(discord, logger, conf)

	deps := &module.CommonDeps{
		Bot:    bot,
		Logger: logger,
		Config: conf,
	}

	// Initialize modules
	for _, m := range modules {
		m.Init(deps)
	}

	bot.Run()
}
