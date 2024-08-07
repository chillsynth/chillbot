package bot

import "strings"

func (b *Bot) HandleError(err error) {
	if err != nil {
		isDebugError := strings.HasPrefix(err.Error(), "debug")

		if b.Config.Environment == "local" && isDebugError {
			b.Logger.LogDebug("debug", "err", err)
		} else if !isDebugError {
			b.Logger.LogError(err)
		}
	}
}
