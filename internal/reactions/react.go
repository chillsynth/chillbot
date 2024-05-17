package emojireactions

import (
	"chillbot/internal/config"
	"log/slog"
	"strings"

	"github.com/bwmarrin/discordgo"
)

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

func React(s *discordgo.Session, m *discordgo.MessageCreate, conf *config.Config, l *slog.Logger) {
	for _, messageReaction := range conf.Reactions.InMessage {
		key, val := getReaction(messageReaction)
		if strings.Contains(m.Content, key) {
			err := s.MessageReactionAdd(m.Message.ChannelID, m.Message.ID, *val.Emoji)
			if err != nil {
				l.Error("Cannot add reaction", slog.String("error", err.Error()))
			}
		}

	}

	for _, stickerNameReaction := range conf.Reactions.InStickerName {
		if len(m.StickerItems) == 0 {
			break
		}
		key, val := getReaction(stickerNameReaction)
		if strings.Contains(m.StickerItems[0].Name, key) {
			_, err := s.ChannelMessageSend(m.ChannelID, *val.Message)
			if err != nil {
				l.Error("Cannot send message", slog.String("error", err.Error()))
			}
		}

	}
}
