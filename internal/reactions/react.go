package reactions

import (
	"chillbot/internal/config"
	"chillbot/internal/module"
	"chillbot/internal/utils"
	"strings"

	"github.com/bwmarrin/discordgo"
)

type ReactorModule struct {
	module.CommonDeps
}

func (m *ReactorModule) Init(deps *module.CommonDeps) {
	m.Discord = deps.Discord
	m.Logger = deps.Logger
	m.Config = deps.Config

	m.Discord.AddHandler(func(s *discordgo.Session, msg *discordgo.MessageCreate) {
		m.React(msg)
	})
}

func getReaction(r map[string]config.Reaction) (string, config.Reaction) {
	var key string
	var val config.Reaction
	for k, v := range r {
		key = k
		val = v
		break
	}
	return key, val
}

func wordIsInMessage(msg string, word string) bool {
	return msg == word || strings.HasPrefix(msg, word+" ") || strings.HasSuffix(msg, " "+word) || strings.Contains(msg, " "+word+" ")
}

func (m *ReactorModule) React(msg *discordgo.MessageCreate) {
	for _, messageReaction := range m.Config.Reactions.InMessage {
		key, val := getReaction(messageReaction)
		if wordIsInMessage(msg.Content, key) {
			err := m.Discord.MessageReactionAdd(msg.Message.ChannelID, msg.Message.ID, *val.Emoji)
			utils.HandleError(err)
		}
	}

	for _, stickerNameReaction := range m.Config.Reactions.InStickerName {
		if len(msg.StickerItems) == 0 {
			break
		}
		key, val := getReaction(stickerNameReaction)
		if strings.Contains(msg.StickerItems[0].Name, key) {
			_, err := m.Discord.ChannelMessageSend(msg.ChannelID, *val.Message)
			utils.HandleError(err)
		}
	}
}
