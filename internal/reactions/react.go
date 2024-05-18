package reactions

import (
	"chillbot/internal/config"
	"chillbot/internal/module"
	"log/slog"
	"strings"

	"github.com/bwmarrin/discordgo"
)

type ReactorModule struct {
	module.CommonDeps
}

func (rm *ReactorModule) Init(deps *module.CommonDeps) {
	rm.Discord = deps.Discord
	rm.Logger = deps.Logger
	rm.Config = deps.Config
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

func (rm *ReactorModule) React(m *discordgo.MessageCreate) {
	for _, messageReaction := range rm.Config.Reactions.InMessage {
		key, val := getReaction(messageReaction)
		if strings.Contains(m.Content, key) {
			err := rm.Discord.MessageReactionAdd(m.Message.ChannelID, m.Message.ID, *val.Emoji)
			if err != nil {
				rm.Logger.LogError("Cannot add reaction", slog.String("error", err.Error()))
			}
		}

	}

	for _, stickerNameReaction := range rm.Config.Reactions.InStickerName {
		if len(m.StickerItems) == 0 {
			break
		}
		key, val := getReaction(stickerNameReaction)
		if strings.Contains(m.StickerItems[0].Name, key) {
			_, err := rm.Discord.ChannelMessageSend(m.ChannelID, *val.Message)
			if err != nil {
				rm.Logger.LogError("Cannot send message", slog.String("error", err.Error()))
			}
		}

	}
}
