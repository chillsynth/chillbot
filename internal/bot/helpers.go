package bot

import (
	"slices"

	"github.com/bwmarrin/discordgo"
)

func (b *Bot) DoesMemberHaveAnyRoles(memberRoles []string, checkRoles []string) bool {
	if len(checkRoles) == 0 {
		return true
	}
	return slices.ContainsFunc(memberRoles, func(e string) bool {
		for _, role := range checkRoles {
			if b.Config.Roles[role] == e {
				return true
			}
		}
		return false
	})
}

func (b *Bot) IsMemberMod(member *discordgo.Member) bool {
	modRoleId := b.Config.Roles["Mod"]
	return slices.Contains(member.Roles, modRoleId)
}

func (b *Bot) IsMemberAdmin(member *discordgo.Member) bool {
	adminRoleId := b.Config.Roles["Admin"]
	return slices.Contains(member.Roles, adminRoleId)
}
