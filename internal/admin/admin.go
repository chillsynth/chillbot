package admin

import (
	"chillbot/internal/bot"

	"github.com/bwmarrin/discordgo"
)

type AdminModule struct {
	bot.CommonDeps
	name string
}

func (m *AdminModule) Load(deps *bot.CommonDeps) error {
	m.Bot = deps.Bot
	m.Logger = deps.Logger
	m.Config = deps.Config
	m.name = "AdminModule"

	err := m.Bot.AddCommand(&discordgo.ApplicationCommand{
		Name:        "admin",
		Description: "admin command",
	}, m.AdminTest, "Admin")

	// bot.AddHandler(m.Bot, m.DeleteCommand)

	return err
}

func (m *AdminModule) AdminTest(i *discordgo.InteractionCreate) error {
	err := m.Bot.Discord.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: "im an admin command!",
		},
	})
	return err
}

/*
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
*/
