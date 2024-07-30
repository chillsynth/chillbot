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
	Discord  *discordgo.Session
	Logger   *logging.Logger
	Config   *config.Config
	Commands []*discordgo.ApplicationCommand
}

func NewBot(s *discordgo.Session, l *logging.Logger, c *config.Config) *Bot {
	return &Bot{
		Discord: s,
		Logger:  l,
		Config:  c,
	}
}

func (b *Bot) Init() {
	discord, logger, _ := b.Discord, b.Logger, b.Config
	discord.Identify.Intents = discordgo.IntentsGuildMessages | discordgo.IntentGuildMembers

	err := discord.Open()
	if err != nil {
		logger.LogFatal("Unable to open a connection to Discord %s", err)
	}

	discord.AddHandler(func(s *discordgo.Session, r *discordgo.Ready) {
		logger.LogInfo(fmt.Sprintf("Logged in as: %v#%v", s.State.User.Username, s.State.User.Discriminator))
	})
}

func (b *Bot) Run() {
	defer b.Discord.Close()
	fmt.Println("Bot is now running.  Press CTRL-C to exit.")
	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt)
	<-sc

	// for _, v := range commands {
	// 	err := discord.ApplicationCommandDelete(discord.State.User.ID, "", v.ID)
	// 	if err != nil {
	// 		logger.LogFatal("Cannot delete '%v' command: %v", v.Name, err)
	// 	}
	// }
}
