package automoderator

import (
	"chillbot/internal/bot"
	"fmt"

	"github.com/bwmarrin/discordgo"
)

type AutoModule struct {
	bot.CommonDeps
	name string
}

func (m *AutoModule) Load(deps *bot.CommonDeps) error {
	m.Bot = deps.Bot
	m.Logger = deps.Logger
	m.Config = deps.Config
	m.name = "AutoModule"

	bot.AddHandler(m.Bot, m.MessageCheck)

	return nil
}

func (m *AutoModule) GetName() string {
	return m.name
}

func (m *AutoModule) MessageCheck(msg *discordgo.MessageCreate) error {
	var err error
	if msg.Author.Bot { // Ignore message if sent by the bot
		return fmt.Errorf("debug %s: ignoring bot-sent message in #demos", m.name)
	}

	// staff is immune
	if m.Bot.IsMemberMod(msg.Member) || m.Bot.IsMemberAdmin(msg.Member) {
		return nil
	}

	switch msg.ChannelID {
	case m.Config.DemosChannelID:
		err = m.DemosChannelModeration(msg)
	case m.Config.InstantBanChannelId:
		err = m.BotAutoBanner(msg)
	default:
		return nil
	}

	return err
}
