package config

import (
	"chillbot/internal/logging"
	"encoding/json"
	"log/slog"
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
		l.LogError("Cannot load config file", slog.String("error", err.Error()))
		panic("Cannot load config file")
	}

	err = json.Unmarshal(dat, c)

	if err != nil {
		l.LogError("Cannot load config file", slog.String("error", err.Error()))
		panic("Cannot load config file")
	}
}
