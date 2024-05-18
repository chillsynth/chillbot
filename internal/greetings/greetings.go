package greetings

import (
	"chillbot/internal/module"
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
	if g.BeforeUpdate.User.Bot {
		return
	}
	if gm.hasUserJustBeenVerified(g) {
		go gm.Discord.GuildMemberRoleAdd(g.Member.GuildID, g.Member.User.ID, gm.Config.OnlineRoleID)

		go gm.Discord.ChannelMessageSend(gm.Config.LoungeChannelID, "Welcome! "+g.Mention())
	}
}

func (gm *GreetingsModule) hasUserJustBeenVerified(g *discordgo.GuildMemberUpdate) bool {
	return g.BeforeUpdate.Pending && !g.Pending && slices.Contains(g.BeforeUpdate.Roles, gm.Config.OnlineRoleID)
}
