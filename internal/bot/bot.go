package bot

import (
	"chillbot/internal/config"
	"chillbot/internal/logging"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/bwmarrin/discordgo"
)

type Bot struct {
	Discord *discordgo.Session
	Logger  *logging.Logger
	Config  *config.Config
}

func (b *Bot) Init(d *discordgo.Session, l *logging.Logger, c *config.Config) {
	b.Discord = d
	b.Logger = l
	b.Config = c
}

func (b *Bot) Run() {
	discord, logger, _ := b.Discord, b.Logger, b.Config

	discord.AddHandler(func(s *discordgo.Session, r *discordgo.Ready) {
		logger.LogInfo(fmt.Sprintf("Logged in as: %v#%v", s.State.User.Username, s.State.User.Discriminator))
	})

	// Listen to new messages
	discord.AddHandler(func(s *discordgo.Session, m *discordgo.MessageCreate) {
		if m.Author.ID == s.State.User.ID {
			return
		}

		if m.Content == "ping" {
			s.ChannelMessageSend(m.ChannelID, "Pong!")
		}

		if m.Content == "pong" {
			s.ChannelMessageSend(m.ChannelID, "Ping!")
		}
	})

	discord.Identify.Intents = discordgo.IntentsGuildMessages | discordgo.IntentGuildMembers

	err := discord.Open()
	if err != nil {
		logger.LogFatal("Unable to open a connection to Discord %s", err)
	}

	fmt.Println("Bot is now running.  Press CTRL-C to exit.")
	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt)
	<-sc

	// Cleanly close down the Discord session.
	discord.Close()
}
