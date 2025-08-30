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
