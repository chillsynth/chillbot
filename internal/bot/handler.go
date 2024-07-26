package bot

import "github.com/bwmarrin/discordgo"

func AddHandler[T any](b *Bot, handler func(dat *T) error) func() {
	return b.Discord.AddHandler(func(s *discordgo.Session, dat *T) {
		err := handler(dat)
		if err != nil {
			b.Logger.LogError(err)
		}
	})
}
