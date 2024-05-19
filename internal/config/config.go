package config

import (
	"chillbot/internal/logging"
	"encoding/json"
	"os"
)

type Config struct {
	GuildID           string    `json:"guild_id"`
	LoungeChannelID   string    `json:"lounge_channel_id"`
	FeedbackChannelID string    `json:"feedback_channel_id"`
	OnlineRoleID      string    `json:"online_role_id"`
	Reactions         Reactions `json:"reactions"`
}

type Reactions struct {
	InMessage     []map[string]Reaction `json:"inMessage"`
	InStickerName []map[string]Reaction `json:"inStickerName"`
}

type Reaction struct {
	Emoji   *string `json:"emoji"`
	Message *string `json:"message"`
}

func (c *Config) Load(l *logging.Logger) {
	dir, _ := os.Getwd()

	dat, err := os.ReadFile(dir + "/config/config.json")

	if err != nil {
		l.LogFatal("Cannot load config file %s", err.Error())
	}

	err = json.Unmarshal(dat, c)

	if err != nil {
		l.LogFatal("Cannot load config file %s", err.Error())
	}
}
