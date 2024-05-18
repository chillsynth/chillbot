package module

import (
	"chillbot/internal/config"
	"chillbot/internal/logging"

	"github.com/bwmarrin/discordgo"
)

type CommonDeps struct {
	Discord *discordgo.Session
	Logger  *logging.Logger
	Config  *config.Config
}

type Module interface {
	Init(deps *CommonDeps)
}
