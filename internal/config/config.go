package config

import (
	"chillbot/internal/logging"
	"encoding/json"
	"os"
)

type Config struct {
	GuildID           string            `json:"guild_id"`
	LoungeChannelID   string            `json:"lounge_channel_id"`
	FeedbackChannelID string            `json:"feedback_channel_id"`
	DemosChannelID    string            `json:"demos_channel_id"`
	YoutubeChannels   []YoutubeChannel  `json:"youtube_channels"`
	Roles             map[string]string `json:"roles"`
	Reactions         Reactions         `json:"reactions"`
}

type Reactions struct {
	InMessage     []map[string]Reaction `json:"inMessage"`
	InStickerName []map[string]Reaction `json:"inStickerName"`
}

type Reaction struct {
	Emoji   *string `json:"emoji"`
	Message *string `json:"message"`
}

type YoutubeChannel struct {
	Name string `json:"name"`
	Feed string `json:"feed"`
}

func (c *Config) Load(l *logging.Logger) error {
	dir, _ := os.Getwd()

	dat, err := os.ReadFile(dir + "/config/config.json") //TODO: DO NOT PUSH WITHOUT CHANGING BACK TO CONFIG.JSON!!!

	if err != nil {
		return err
	}

	err = json.Unmarshal(dat, c)

	return err
}
