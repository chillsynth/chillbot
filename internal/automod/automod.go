package automod

import (
	"chillbot/internal/module"
	"github.com/bwmarrin/discordgo"
	"time"
)

type AutomodModule struct {
	module.CommonDeps
}

func (m *AutomodModule) Load(deps *module.CommonDeps) error {
	m.Bot = deps.Bot
	m.Logger = deps.Logger
	m.Config = deps.Config

	return nil
}

func (m *AutomodModule) SendTempMessage(s *discordgo.Session, msg *discordgo.Message, channelID string, content string, duration time.Duration) error {
	// Send the message first
	var err error
	msg, err = s.ChannelMessageSend(channelID, content)
	if err != nil {
		m.Logger.LogError(err)
		return nil
	}

	// Start a goroutine to delete the message after the specified duration
	go func() {
		time.Sleep(duration)
		err = s.ChannelMessageDelete(channelID, msg.ID)
		if err != nil {
			m.Logger.LogError(err)
		}
	}()

	return err
}

func (m *AutomodModule) MessageCheck(msg *discordgo.MessageCreate) error {
	var err error
	if msg.Author == m.Bot.Discord.State.User { // Ignore message if sent by the bot
		return nil
	}
	if msg.ChannelID == m.Config.DemosChannelID { // If message sent in #demos, allow ONLY attachments
		if msg.Content != "" {
			m.Logger.LogInfo("automod.go: tried to send text in #demos.")
			// err = m.Bot.Discord.ChannelMessageDelete(msg.ChannelID, msg.ID)
			// err = m.SendTempMessage(m.Bot.Discord, msg.Message, msg.ChannelID, "<@{message.author.id}>, this channel is for uploading files **only**.", 5)
		}
	}

	return err
}
