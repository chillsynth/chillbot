package general

import (
	"chillbot/internal/bot"
	"fmt"

	"github.com/bwmarrin/discordgo"
)

type GeneralModule struct {
	bot.CommonDeps
	name string
}

func (m *GeneralModule) Load(deps *bot.CommonDeps) error {
	m.Bot = deps.Bot
	m.Logger = deps.Logger
	m.Config = deps.Config
	m.name = "GeneralModule"

	err := m.Bot.AddCommand(&discordgo.ApplicationCommand{
		Name:        "ping",
		Description: "pings the bot",
	}, m.Ping)

	// err2 :=

	// err = errors.Join(err, err2)

	return err
}

func (m *GeneralModule) Ping(i *discordgo.InteractionCreate) error {
	err := m.Bot.Discord.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: fmt.Sprintf("Pong! Latency is: %v", m.Bot.Discord.HeartbeatLatency()),
		},
	})
	return err
}

func (m *GeneralModule) TestMessage(msg *discordgo.MessageCreate) error {
	if msg.Author.Bot {
		return fmt.Errorf("debug %s: ignoring bot-sent message in #demos", m.name)
	}
	_, err := m.Bot.Discord.ChannelMessageSend(msg.ChannelID, "test message!")

	return err
}
