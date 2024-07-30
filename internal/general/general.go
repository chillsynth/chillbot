package general

import (
	"chillbot/internal/module"

	"github.com/bwmarrin/discordgo"
)

type GeneralModule struct {
	module.CommonDeps
}

func (m *GeneralModule) Load(deps *module.CommonDeps) {
	m.Bot = deps.Bot
	m.Logger = deps.Logger
	m.Config = deps.Config

	m.Bot.AddCommand(&discordgo.ApplicationCommand{
		Name:        "ping",
		Description: "pings the bot",
	}, m.Ping)
}

func (m *GeneralModule) Ping(i *discordgo.InteractionCreate) error {
	err := m.Bot.Discord.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: "Pong!",
		},
	})
	return err
}
