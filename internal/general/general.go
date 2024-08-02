package general

import (
	"chillbot/internal/module"
	"fmt"

	"github.com/bwmarrin/discordgo"
)

type GeneralModule struct {
	module.CommonDeps
}

func (m *GeneralModule) Load(deps *module.CommonDeps) error {
	m.Bot = deps.Bot
	m.Logger = deps.Logger
	m.Config = deps.Config

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
