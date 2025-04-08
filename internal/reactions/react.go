package reactions

import (
	"chillbot/internal/bot"
	"chillbot/internal/config"
	"strings"

	"github.com/bwmarrin/discordgo"
)

type ReactorModule struct {
	bot.CommonDeps
	name string
}

func (m *ReactorModule) Load(deps *bot.CommonDeps) error {
	m.Bot = deps.Bot
	m.Logger = deps.Logger
	m.Config = deps.Config
	m.name = "ReactorModule"

	bot.AddHandler(m.Bot, m.React)

	return nil
}

func (m *ReactorModule) GetName() string {
	return m.name
}

func getReaction(r map[string]config.Reaction) (string, config.Reaction) {
	var word string
	var reaction config.Reaction
	for k, v := range r {
		word = k
		reaction = v
		break
	}
	return word, reaction
}

func wordIsInMessage(msg string, word string) bool {
	return strings.ToLower(msg) == strings.ToLower(word) || 
		strings.HasPrefix( strings.ToLower(msg), strings.ToLower(word) + " " ) || 
		strings.HasSuffix( strings.ToLower(msg), " " + strings.ToLower(word) ) || 
		strings.Contains( strings.ToLower(msg), " " + strings.ToLower(word) + " " )
}

func (m *ReactorModule) React(msg *discordgo.MessageCreate) error {
	var err error
	for _, messageReaction := range m.Config.Reactions.InMessage {
		word, reaction := getReaction(messageReaction)
		if wordIsInMessage(msg.Content, word) {
			err = m.HandleReaction(msg, reaction)
		}
	}

	if len(msg.StickerItems) == 0 {
		return err
	}
	for _, stickerNameReaction := range m.Config.Reactions.InStickerName {
		word, reaction := getReaction(stickerNameReaction)
		if strings.Contains(msg.StickerItems[0].Name, word) {
			err = m.HandleReaction(msg, reaction)
		}
	}

	return err
}

func (m *ReactorModule) HandleReaction(msg *discordgo.MessageCreate, val config.Reaction) error {
	var err error
	if val.Emoji != nil {
		err = m.Bot.Discord.MessageReactionAdd(msg.Message.ChannelID, msg.Message.ID, *val.Emoji)
	} else if val.Message != nil {
		_, err = m.Bot.Discord.ChannelMessageSend(msg.ChannelID, *val.Message)
	}
	return err
}
