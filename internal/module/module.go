package module

import (
	"chillbot/internal/bot"
	"chillbot/internal/config"
	"chillbot/internal/logging"
)

type CommonDeps struct {
	Bot    *bot.Bot
	Logger *logging.Logger
	Config *config.Config
}

type Module interface {
	Init(deps *CommonDeps)
}
