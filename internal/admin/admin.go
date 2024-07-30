package admin

import (
	"chillbot/internal/bot"
	"chillbot/internal/module"
	"errors"
	"strings"

	"github.com/bwmarrin/discordgo"
)

type AdminModule struct {
	module.CommonDeps
}

func (m *AdminModule) Load(deps *module.CommonDeps) error {
	m.Bot = deps.Bot
	m.Logger = deps.Logger
	m.Config = deps.Config

	err := m.Bot.AddCommand(&discordgo.ApplicationCommand{
		Name:        "admin",
		Description: "admin command",
	}, m.Ping, "Admin")

	bot.AddHandler(m.Bot, m.DeleteCommand)

	return err
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

func (m *AdminModule) DeleteCommand(msg *discordgo.MessageCreate) error {
	var err error
	if !m.Bot.DoesMemberHaveAnyRoles(msg.Member.Roles, []string{"Admin"}) {
		return errors.New("Does not have permission to execute this")
	}
	if strings.HasPrefix(msg.Content, "!delcmd") {
		msgArgs := strings.Split(msg.Content, " ")
		if len(msgArgs) > 1 {
			err = m.Bot.Discord.ApplicationCommandDelete(m.Bot.Discord.State.User.ID, "", m.Bot.Commands[msgArgs[1]].ID)
		}
	}
	return err
}
