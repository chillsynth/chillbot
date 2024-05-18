package main

import (
	"chillbot/internal/config"
	"chillbot/internal/reactions"
	"fmt"
	"log"
	"log/slog"
	"os"
	"os/signal"
	"syscall"

	"github.com/bwmarrin/discordgo"
)

// To add more modules, copy the reactions code and rename it
// add a reference to the new module here, then register it
// in the main function as we do with ReactorModule
var (
	reactor reactions.ReactorModule
)

type Bot struct {
	Discord *discordgo.Session
	Logger  *slog.Logger
	Config  *config.Config
}

func createDiscordSession() (*discordgo.Session, error) {
	token := os.Getenv("DISCORD_CLIENT_SECRET")

	// New Discord session
	discord, err := discordgo.New("Bot " + token)

	return discord, err
}

func (b *Bot) runBot() {
	discord, logger, _ := b.Discord, b.Logger, b.Config

	discord.AddHandler(func(s *discordgo.Session, r *discordgo.Ready) {
		logger.Info(fmt.Sprintf("Logged in as: %v#%v", s.State.User.Username, s.State.User.Discriminator))
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

		reactor.React(m)
	})

	discord.Identify.Intents = discordgo.IntentsGuildMessages

	err := discord.Open()
	if err != nil {
		log.Fatalf("Unable to open a connection to Discord %s", err)
	}

	fmt.Println("Bot is now running.  Press CTRL-C to exit.")
	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt)
	<-sc

	// Cleanly close down the Discord session.
	discord.Close()
}

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

	conf := &config.Config{}
	conf.Load(logger)

	discord, err := createDiscordSession()
	if err != nil {
		log.Fatalf("error creating Discord session %s", err)
	}

	// Initialize Modules
	reactor = reactions.ReactorModule{
		Discord: discord,
		Logger:  logger,
		Config:  conf,
	}

	// Initialize Bot
	bot := &Bot{Discord: discord, Logger: logger, Config: conf}

	bot.runBot()
}
