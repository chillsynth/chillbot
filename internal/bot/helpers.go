package bot

import "slices"

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
