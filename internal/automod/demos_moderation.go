package automoderator

import (
	"fmt"
	"time"

	"github.com/bwmarrin/discordgo"
)

func (m *AutoModule) DemosChannelModeration(msg *discordgo.MessageCreate) error {
	var err error
	if msg.Content != "" {
		m.Logger.LogInfo(fmt.Sprintf("%s: UserID:%s(%s) tried to send text in #demos.",
			m.name, msg.Author.ID, msg.Author.GlobalName))

		err = m.DeleteMsgAndSendTempMessageToDemos(msg)

	} else if len(msg.StickerItems) != 0 {
		m.Logger.LogInfo(fmt.Sprintf("%s: UserID:%s(%s) tried to send sticker in #demos.",
			m.name, msg.Author.ID, msg.Author.GlobalName))

		err = m.DeleteMsgAndSendTempMessageToDemos(msg)
	}

	return err
}

func (m *AutoModule) DeleteMsgAndSendTempMessageToDemos(msg *discordgo.MessageCreate) error {
	err := m.Bot.Discord.ChannelMessageDelete(msg.ChannelID, msg.ID)
	if err != nil {
		return fmt.Errorf("demos channel delete message: %w", err)
	}

	err = m.DemosSendTempMessage(m.Bot.Discord, msg.Message, msg.ChannelID, msg.Author.ID, 5)

	if err != nil {
		return fmt.Errorf("demos channel send temp message: %w", err)
	}

	return nil
}

func (m *AutoModule) DemosSendTempMessage(s *discordgo.Session, msg *discordgo.Message, channelID string, userID string, duration time.Duration) error {
	// Send the automod message first
	var err error
	msg, err = s.ChannelMessageSend(channelID, fmt.Sprintf("<@%s>, this channel is for uploading files **only**.", userID))
	if err != nil {
		m.Logger.LogError(err)
		return nil
	}

	// Start a goroutine to delete the message after the specified duration
	go func() {
		time.Sleep(duration * time.Second)
		err = s.ChannelMessageDelete(channelID, msg.ID)
		if err != nil {
			m.Logger.LogError(err)
		}
	}()

	return err
}
