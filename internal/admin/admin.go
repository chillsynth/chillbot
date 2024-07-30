package admin

import (
	"chillbot/internal/module"

	"github.com/bwmarrin/discordgo"
)

type AdminModule struct {
	module.CommonDeps
}

func (m *AdminModule) Load(deps *module.CommonDeps) {
	m.Bot = deps.Bot
	m.Logger = deps.Logger
	m.Config = deps.Config

	m.Bot.AddCommand(&discordgo.ApplicationCommand{
		Name:        "admin",
		Description: "admin command",
	}, m.Ping, "Admin")
}

func (m *AdminModule) Ping(i *discordgo.InteractionCreate) error {
	err := m.Bot.Discord.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: "im an admin command!",
		},
	})
	return err
}
