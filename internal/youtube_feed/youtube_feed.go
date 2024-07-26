package youtube

import (
	"chillbot/internal/module"
	"chillbot/internal/utils"
	"fmt"
	"os"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/mmcdole/gofeed"
	"github.com/robfig/cron/v3"
)

type YoutubeFeedModule struct {
	module.CommonDeps
	fp               *gofeed.Parser
	channels         map[string]string
	pollingFrequency string
}

func (m *YoutubeFeedModule) Init(deps *module.CommonDeps) {
	m.Bot = deps.Bot
	m.Logger = deps.Logger
	m.Config = deps.Config
	m.channels = map[string]string{}
	m.fp = gofeed.NewParser()

	m.LoadLatestVideos()

	m.pollingFrequency = "1m"

	c := cron.New()

	c.AddFunc("@every "+m.pollingFrequency, utils.Job(m.PostLatestVideos, m.Logger))

	c.Start()
}

func (m *YoutubeFeedModule) LoadLatestVideos() {
	for _, channel := range m.Config.YoutubeChannels {
		feed, err := m.fp.ParseURL(channel.Feed)
		if err != nil {
			break
		}
		m.channels[channel.Feed] = feed.Items[0].Link
	}
}

func (m *YoutubeFeedModule) PostLatestVideos() error {
	m.Logger.LogInfo("Checking for latest videos")
	for channel, lastVideoLink := range m.channels {
		feed, err := m.fp.ParseURL(channel)
		if err != nil {
			break
		}

		fmt.Println(feed.Authors[0].Name)
		fmt.Printf("Pub time: %s\n", feed.Items[0].PublishedParsed)
		fmt.Printf("Time since: %s\n", time.Since(*feed.Items[0].PublishedParsed))

		if feed.Items[0].Link != lastVideoLink {
			m.channels[channel] = feed.Items[0].Link

			_, err := m.Bot.Discord.WebhookExecute(os.Getenv("YOUTUBE_WEBHOOK_ID"), os.Getenv("YOUTUBE_WEBHOOK_TOKEN"), false, &discordgo.WebhookParams{
				Content: fmt.Sprintf("%s: %s", feed.Items[0].Title, feed.Items[0].Link),
			})

			return err
		}
	}
	return nil
}
