package bot

import (
	"slices"

	"github.com/bwmarrin/discordgo"
)

func (b *Bot) AddCommand(cmd *discordgo.ApplicationCommand, handler func(i *discordgo.InteractionCreate) error, requiredRoles ...string) error {
	b.Commands = append(b.Commands, cmd)

	b.RegisterCommandHandler(handler, requiredRoles)

	_, err := b.Discord.ApplicationCommandCreate(b.Discord.State.User.ID, "", cmd)

	return err
}

func (b *Bot) RegisterCommandHandler(handler func(i *discordgo.InteractionCreate) error, requiredRoles []string) func() {
	return b.Discord.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		var err error

		if b.DoesMemberHaveAnyRoles(i.Member.Roles, requiredRoles) {
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

func (b *Bot) DoesMemberHaveAnyRoles(memberRoles []string, checkRoles []string) bool {
	if len(checkRoles) == 0 {
		return true
	}
	return slices.ContainsFunc(memberRoles, func(e string) bool {
		for _, role := range checkRoles {
			if b.Config.Roles[role] == e {
				return true
			}
		}
		return false
	})
}
