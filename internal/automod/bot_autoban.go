package automoderator

import (
	"fmt"

	"github.com/bwmarrin/discordgo"
)

func (m *AutoModule) BotAutoBanner(msg *discordgo.MessageCreate) error {
	var err error

	err = m.Bot.Discord.ChannelMessageDelete(msg.ChannelID, msg.ID)

	if err != nil {
		return fmt.Errorf("delete bot message: %w", err)
	}

	err = m.Bot.Discord.GuildBanCreateWithReason(msg.GuildID, msg.Author.ID, "Suspected bot", 7, discordgo.WithRetryOnRatelimit(true))

	if err != nil {
		return fmt.Errorf("guild ban bot: %w", err)
	}

	return nil
}

func (m *AutoModule) SetupInstantBanButton() error {
	msgs, err := m.Bot.Discord.ChannelMessages(m.Config.InstantBanChannelId, 1, "", "", "")
	if err != nil {
		return fmt.Errorf("fetch instant ban channel messages: %w", err)
	}

	if len(msgs) > 0 {
		if msgs[0].Author.ID != m.Bot.Discord.State.User.ID || msgs[0].Content != "Click below to ban yourself" {
			_, err = m.Bot.Discord.ChannelMessageSendComplex(m.Config.InstantBanChannelId, &discordgo.MessageSend{
				Content: "Click below to ban yourself",
				Components: []discordgo.MessageComponent{
					&discordgo.ActionsRow{
						Components: []discordgo.MessageComponent{
							&discordgo.Button{
								Label:    "Get Banned",
								Style:    discordgo.DangerButton,
								CustomID: "ban_button",
							},
						},
					},
				},
			})

			if err != nil {
				return fmt.Errorf("create instant ban button: %w", err)
			}
		}
	}

	m.Bot.Discord.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		if i.Type != discordgo.InteractionMessageComponent {
			return
		}

		data := i.Data.(discordgo.MessageComponentInteractionData)

		if data.CustomID == "ban_button" {
			// acknowledge the interaction but do nothing
			err := m.Bot.Discord.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseDeferredMessageUpdate,
			})

			if err != nil {
				m.Bot.HandleError(fmt.Errorf("acknowledge interaction: %w", err))
			}

			// GET BANNED
			err = m.Bot.Discord.GuildBanCreateWithReason(i.GuildID, i.Member.User.ID, "Suspected bot", 7, discordgo.WithRetryOnRatelimit(true))

			if err != nil {
				m.Bot.HandleError(fmt.Errorf("ban user from ban button interaction: %w", err))
			}
		}
	})

	return nil
}
