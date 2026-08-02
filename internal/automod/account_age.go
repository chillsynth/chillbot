package automoderator

import (
	"fmt"
	"time"

	"github.com/bwmarrin/discordgo"
)

func (m *AutoModule) AccountAgeCheck(member *discordgo.GuildMemberAdd) error {
	if m.Config.MinAccountAgeDays <= 0 {
		return nil
	}

	created, err := discordgo.SnowflakeTimestamp(member.User.ID)
	if err != nil {
		return fmt.Errorf("calculate account age: %w", err)
	}

	age := time.Since(created)
	minAge := time.Duration(m.Config.MinAccountAgeDays) * 24 * time.Hour // days * (24 * hour)

	if age < minAge {
		m.Logger.LogInfo("Account too young", "user", member.User.Username, "age", age, "minAge", minAge)

		if m.Config.ModbotChannelId != "" {
			avatarURL := member.User.AvatarURL("")
			if avatarURL == "" {
				avatarURL = "https://cdn.discordapp.com/embed/avatars/0.png" // Fallback to a default avatar if URL is empty
			}

			embed := &discordgo.MessageEmbed{
				Title:       "Suspected Bot Account Flagged",
				Description: fmt.Sprintf("Account <@%s> is too young and has been kicked.", member.User.ID),
				Color:       0xff0000,
				Fields: []*discordgo.MessageEmbedField{
					{
						Name:   "Username",
						Value:  member.User.Username,
						Inline: true,
					},
					{
						Name:   "Display Name",
						Value:  member.User.GlobalName,
						Inline: true,
					},
					{
						Name:   "Account Created",
						Value:  created.Format(time.RFC1123),
						Inline: false,
					},
					{
						Name:   "Account Age",
						Value:  age.Truncate(time.Second).String(),
						Inline: true,
					},
					{
						Name:   "User ID",
						Value:  member.User.ID,
						Inline: true,
					},
				},
				Thumbnail: &discordgo.MessageEmbedThumbnail{
					URL: avatarURL,
				},
				Timestamp: time.Now().Format(time.RFC3339),
			}

			_, err = m.Bot.Discord.ChannelMessageSendEmbed(m.Config.ModbotChannelId, embed)
			if err != nil {
				m.Logger.LogError(fmt.Errorf("send account age alert: %w", err))
			}
		}

		err = m.Bot.Discord.GuildMemberDeleteWithReason(member.GuildID, member.User.ID, fmt.Sprintf("Account too young: %s", age.Truncate(time.Hour)))
		if err != nil {
			return fmt.Errorf("kick young account: %w", err)
		}
	}

	return nil
}
