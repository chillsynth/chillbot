package bot

import (
	"slices"

	"github.com/bwmarrin/discordgo"
)

func (b *Bot) AddCommand(commandName string, commandDescription string, requiredRoles string, handler func(i *discordgo.InteractionCreate) error) error {
	cmd := &discordgo.ApplicationCommand{
		Name:        commandName,
		Description: commandDescription,
	}

	b.Commands = append(b.Commands, cmd)

	b.RegisterCommandHandler(handler, requiredRoles)

	_, err := b.Discord.ApplicationCommandCreate(b.Discord.State.User.ID, "", cmd)

	return err
}

func (b *Bot) RegisterCommandHandler(handler func(i *discordgo.InteractionCreate) error, requiredRoles string) func() {
	return b.Discord.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		var err error

		if slices.Contains(i.Member.Roles, b.Config.Roles[requiredRoles]) {
			err = handler(i)
		} else {
			err = b.Discord.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{
					Content: "Sorry, you do not have permission to run this command",
					Flags:   discordgo.MessageFlagsEphemeral,
				},
			})
		}

		if err != nil {
			b.Logger.LogError(err)
		}
	})
}
