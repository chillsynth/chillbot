package greetings

import (
	"chillbot/internal/bot"
	"chillbot/internal/module"
	"fmt"
	"slices"

	"github.com/bwmarrin/discordgo"
)

type GreetingsModule struct {
	module.CommonDeps
}

func (m *GreetingsModule) Load(deps *module.CommonDeps) {
	m.Bot = deps.Bot
	m.Logger = deps.Logger
	m.Config = deps.Config

	bot.AddHandler(m.Bot, m.GreetVerifiedUser)
}

func (m *GreetingsModule) GreetVerifiedUser(g *discordgo.GuildMemberUpdate) error {
	if g.Member.User.Bot || g.BeforeUpdate == nil || g.GuildID != m.Config.GuildID {
		return nil
	}
	if m.hasUserJustBeenVerified(g) {
		err := m.Bot.Discord.GuildMemberRoleAdd(g.Member.GuildID, g.Member.User.ID, m.Config.Roles["online_role"])
		if err != nil {
			return err
		}

		_, err = m.Bot.Discord.ChannelMessageSend(m.Config.LoungeChannelID,
			fmt.Sprintf("**Hello %s and welcome to ChillSynth!**", g.Mention()))
		if err != nil {
			return err
		}

		_, err = m.Bot.Discord.ChannelMessageSendEmbed(m.Config.LoungeChannelID, &discordgo.MessageEmbed{
			Description: fmt.Sprintf(
				"### <:Discord_Invite:1140057489941995650> Head over to <#%s> to grab your roles \n"+
					"### <:Discord_Message_SpeakTTS:1140059207106826271> "+
					"And remember to **`GIVE`** <#%s> __before__ you **`ASK`** for it!",
				m.Config.LoungeChannelID,
				m.Config.FeedbackChannelID),
			Color: 13281772,
			Footer: &discordgo.MessageEmbedFooter{
				Text: "If you have any questions, feel free to @ one of our moderators!",
			},
		})
		if err != nil {
			return err
		}
	}
	return nil
}

func (m *GreetingsModule) hasUserJustBeenVerified(g *discordgo.GuildMemberUpdate) bool {
	return g.BeforeUpdate.Pending && !g.Pending && !slices.Contains(g.BeforeUpdate.Roles, m.Config.Roles["online_role"])
}
