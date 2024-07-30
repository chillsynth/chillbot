package bot

import (
	"slices"

	"github.com/bwmarrin/discordgo"
)

type BotCommand struct {
	*discordgo.ApplicationCommand
	RequiredRoles []string
}

func (b *Bot) AddCommand(cmd *discordgo.ApplicationCommand, handler func(i *discordgo.InteractionCreate) error, requiredRoles ...string) error {

	b.CommandHandlers[cmd.Name] = handler

	regCmd, err := b.Discord.ApplicationCommandCreate(b.Discord.State.User.ID, "", cmd)

	botCmd := BotCommand{
		ApplicationCommand: regCmd,
		RequiredRoles:      requiredRoles,
	}

	b.Commands[cmd.Name] = botCmd

	return err
}

func (b *Bot) RegisterCommandHandler() {
	b.Discord.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		var err error

		if h, ok := b.CommandHandlers[i.ApplicationCommandData().Name]; ok {
			if b.DoesMemberHaveAnyRoles(i.Member.Roles, b.Commands[i.ApplicationCommandData().Name].RequiredRoles) {
				err = h(i)
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
