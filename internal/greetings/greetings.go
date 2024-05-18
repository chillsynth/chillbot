package greetings

import (
	"chillbot/internal/module"
	"fmt"
	"slices"

	"github.com/bwmarrin/discordgo"
)

type GreetingsModule struct {
	module.CommonDeps
}

func (gm *GreetingsModule) Init(deps *module.CommonDeps) {
	gm.Discord = deps.Discord
	gm.Logger = deps.Logger
	gm.Config = deps.Config

	gm.Discord.AddHandler(func(s *discordgo.Session, g *discordgo.GuildMemberUpdate) {
		gm.GreetVerifiedUser(g)
	})
}

func (gm *GreetingsModule) GreetVerifiedUser(g *discordgo.GuildMemberUpdate) {
	if g.Member.User.Bot || g.BeforeUpdate == nil {
		return
	}
	if gm.hasUserJustBeenVerified(g) {
		gm.Discord.GuildMemberRoleAdd(g.Member.GuildID, g.Member.User.ID, gm.Config.OnlineRoleID)

		gm.Discord.ChannelMessageSend(gm.Config.LoungeChannelID,
			fmt.Sprintf("**Hello %s and welcome to ChillSynth!**", g.Mention()))

		_, e := gm.Discord.ChannelMessageSendEmbed(gm.Config.LoungeChannelID, &discordgo.MessageEmbed{
			Description: fmt.Sprintf(
				"### <:Discord_Invite:1140057489941995650> Head over to <#%s> to grab your roles \n"+
					"### <:Discord_Message_SpeakTTS:1140059207106826271> "+
					"And remember to **`GIVE`** <#%s> __before__ you **`ASK`** for it!",
				gm.Config.LoungeChannelID,
				gm.Config.FeedbackChannelID),
			Color: 13281772,
			Footer: &discordgo.MessageEmbedFooter{
				Text: "If you have any questions, feel free to @ one of our moderators!",
			},
		})
		if e != nil {
			fmt.Println(e)
		}
	}
}

func (gm *GreetingsModule) hasUserJustBeenVerified(g *discordgo.GuildMemberUpdate) bool {
	return true || g.BeforeUpdate.Pending && !g.Pending && !slices.Contains(g.BeforeUpdate.Roles, gm.Config.OnlineRoleID)
}
