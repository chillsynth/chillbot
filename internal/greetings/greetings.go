package greetings

import (
	"chillbot/internal/module"
	"chillbot/internal/utils"
	"fmt"
	"slices"

	"github.com/bwmarrin/discordgo"
)

type GreetingsModule struct {
	module.CommonDeps
}

func (m *GreetingsModule) Init(deps *module.CommonDeps) {
	m.Discord = deps.Discord
	m.Logger = deps.Logger
	m.Config = deps.Config

	m.Discord.AddHandler(func(s *discordgo.Session, g *discordgo.GuildMemberUpdate) {
		m.GreetVerifiedUser(g)
	})
}

func (m *GreetingsModule) GreetVerifiedUser(g *discordgo.GuildMemberUpdate) {
	if g.Member.User.Bot || g.BeforeUpdate == nil || g.GuildID != m.Config.GuildID {
		return
	}
	if m.hasUserJustBeenVerified(g) {
		err := m.Discord.GuildMemberRoleAdd(g.Member.GuildID, g.Member.User.ID, m.Config.OnlineRoleID)
		utils.HandleError(err)

		_, err = m.Discord.ChannelMessageSend(m.Config.LoungeChannelID,
			fmt.Sprintf("**Hello %s and welcome to ChillSynth!**", g.Mention()))
		utils.HandleError(err)

		_, err = m.Discord.ChannelMessageSendEmbed(m.Config.LoungeChannelID, &discordgo.MessageEmbed{
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
		utils.HandleError(err)
	}
}

func (m *GreetingsModule) hasUserJustBeenVerified(g *discordgo.GuildMemberUpdate) bool {
	return g.BeforeUpdate.Pending && !g.Pending && !slices.Contains(g.BeforeUpdate.Roles, m.Config.OnlineRoleID)
}
