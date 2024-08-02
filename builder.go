package main

import (
	"chillbot/internal/admin"
	"chillbot/internal/automod"
	"chillbot/internal/bot"
	"chillbot/internal/config"
	"chillbot/internal/general"
	"chillbot/internal/greetings"
	"chillbot/internal/logging"
	"chillbot/internal/module"
	"chillbot/internal/reactions"
	"chillbot/internal/youtube_feed"
	"os"

	"github.com/bwmarrin/discordgo"
)

var modules = []module.Module{
	&reactions.ReactorModule{},
	&greetings.GreetingsModule{},
	&youtube.YoutubeFeedModule{},
	&general.GeneralModule{},
	&admin.AdminModule{},
	&automoderator.AutoModule{},
}

type Builder struct {
	Bot       *bot.Bot
	logger    *logging.Logger
	config    *config.Config
	container *Container
}

func NewBuilder(l *logging.Logger, c *config.Config) *Builder {
	return &Builder{
		logger:    l,
		config:    c,
		container: &Container{},
	}
}

func (b *Builder) Build() error {
	err := b.BuildDiscordClient()
	if err != nil {
		return err
	}

	b.BuildBot()

	b.Bot.Init()

	b.BuildModules()

	return nil
}

func (b *Builder) BuildDiscordClient() error {
	token := os.Getenv("DISCORD_CLIENT_SECRET")

	discord, err := discordgo.New("Bot " + token)

	b.container.Discord = discord

	return err
}

func (b *Builder) BuildBot() {
	b.Bot = bot.NewBot(b.container.Discord, b.logger, b.config)
}

func (b *Builder) BuildModules() {
	deps := &module.CommonDeps{
		Bot:    b.Bot,
		Logger: b.logger,
		Config: b.config,
	}

	for _, m := range modules {
		err := m.Load(deps)
		if err != nil {
			b.logger.LogFatal("Error loading module %s, error %s", m, err.Error())
		}
	}
}
