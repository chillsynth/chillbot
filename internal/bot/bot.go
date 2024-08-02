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
	Discord         *discordgo.Session
	Logger          *logging.Logger
	Config          *config.Config
	Commands        map[string]BotCommand
	CommandHandlers map[string]func(i *discordgo.InteractionCreate) error
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
	discord.Identify.Intents = discordgo.IntentsAll
	// discord.Identify.Intents = discordgo.IntentsGuildMessages | discordgo.IntentGuildMembers

	err := discord.Open()
	if err != nil {
		logger.LogFatal("Unable to open a connection to Discord %s", err)
	}

	discord.AddHandler(func(s *discordgo.Session, r *discordgo.Ready) {
		logger.LogInfo(fmt.Sprintf("Logged in as: %v#%v", s.State.User.Username, s.State.User.Discriminator))
	})

	b.Commands = make(map[string]BotCommand)
	b.CommandHandlers = make(map[string]func(i *discordgo.InteractionCreate) error)

	b.RegisterCommandHandler()
}

func (b *Bot) Run() {
	defer b.Discord.Close()
	fmt.Println("Bot is now running.  Press CTRL-C to exit.")
	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt)
	<-sc

	// delete registered commands when not in prod
	if b.Config.Environment != "prod" {
		for _, v := range b.Commands {
			err := b.Discord.ApplicationCommandDelete(b.Discord.State.User.ID, "", v.ID)
			if err != nil {
				b.Logger.LogFatal("Cannot delete '%v' command: %v", v.Name, err)
			}
		}
	}
}
