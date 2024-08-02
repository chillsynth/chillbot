package automoderator

import (
	"chillbot/internal/bot"
	"chillbot/internal/module"
	"fmt"
	"time"

	"github.com/bwmarrin/discordgo"
)

type AutoModule struct {
	module.CommonDeps
}

func (m *AutoModule) Load(deps *module.CommonDeps) error {
	m.Bot = deps.Bot
	m.Logger = deps.Logger
	m.Config = deps.Config

	bot.AddHandler(m.Bot, m.MessageCheck)

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

func (m *AutoModule) MessageCheck(msg *discordgo.MessageCreate) error {
	var err error
	if msg.Author.Bot == true { // Ignore message if sent by the bot
		m.Logger.LogDebug("automod.go: ignoring bot-sent message in #demos")
		return nil
	} else {
		if msg.ChannelID == m.Config.DemosChannelID { // If message sent in #demos, allow ONLY attachments
			if msg.Content != "" {
				m.Logger.LogInfo(fmt.Sprintf("automod.go: UserID:%s(%s) tried to send text in #demos.",
					msg.Author.ID, msg.Author.GlobalName))
				err = m.Bot.Discord.ChannelMessageDelete(msg.ChannelID, msg.ID)
				err = m.DemosSendTempMessage(m.Bot.Discord, msg.Message, msg.ChannelID, msg.Author.ID, 5)
			}
		}
	}
	return err
}
