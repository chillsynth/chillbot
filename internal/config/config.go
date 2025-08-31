package config

import (
	"encoding/json"
	"fmt"
	"os"
)

type Config struct {
	Environment          string            `json:"environment"`
	GuildID              string            `json:"guild_id"`
	LoungeChannelID      string            `json:"lounge_channel_id"`
	FeedbackChannelID    string            `json:"feedback_channel_id"`
	DemosChannelID       string            `json:"demos_channel_id"`
	EventStageChannelId  string            `json:"event_stage_channel_id"`
	EventStreamChannelId string            `json:"event_stream_channel_id"`
	EventChatChannelId   string            `json:"event_chat_channel_id"`
	HangoutRoomId        string            `json:"hangout_room_id"`
	InstantBanChannelId  string            `json:"instant_ban_channel_id"`
	YoutubeChannels      []YoutubeChannel  `json:"youtube_channels"`
	Roles                map[string]string `json:"roles"`
	Reactions            Reactions         `json:"reactions"`
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

func (c *Config) Load() error {
	dir, _ := os.Getwd()

	currentEnv := os.Getenv("ENV")

	dat, err := os.ReadFile(dir + fmt.Sprintf("/config/config.%s.json", currentEnv)) //TODO: DO NOT PUSH WITHOUT CHANGING BACK TO CONFIG.JSON!!!

	if err != nil {
		return err
	}

	err = json.Unmarshal(dat, c)

	return err
}
