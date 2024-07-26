package bot

import "github.com/bwmarrin/discordgo"

func AddHandler[T any](b *Bot, handler func(event *T) error) func() {
	return b.Discord.AddHandler(func(s *discordgo.Session, event *T) {
		err := handler(event)
		if err != nil {
			b.Logger.LogError(err)
		}
	})
}
