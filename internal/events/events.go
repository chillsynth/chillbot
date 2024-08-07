package events

import (
	"chillbot/internal/bot"
	"fmt"

	"github.com/bwmarrin/discordgo"
)

type EventsModule struct {
	bot.CommonDeps
	name string
}

func (m *EventsModule) Load(deps *bot.CommonDeps) error {
	m.Bot = deps.Bot
	m.Logger = deps.Logger
	m.Config = deps.Config
	m.name = "EventsModule"

	err := m.Bot.AddCommand(&discordgo.ApplicationCommand{
		Name:        "event",
		Description: "Sets Event Mode on and off.",
		Options: []*discordgo.ApplicationCommandOption{
			{
				Type:        discordgo.ApplicationCommandOptionInteger,
				Name:        "event_type",
				Description: "Type of event channel",
				Required:    true,
				Choices: []*discordgo.ApplicationCommandOptionChoice{
					{
						Name:  "Stage",
						Value: 0,
					},
					{
						Name:  "Stream",
						Value: 1,
					},
				},
			},
			{
				Type:        discordgo.ApplicationCommandOptionBoolean,
				Name:        "enable",
				Required:    true,
				Description: "Whether to enable or disable",
			},
		},
	}, m.Event)

	// err = errors.Join(err, err2)

	return err
}

func (m *EventsModule) GetName() string {
	return m.name
}

func (m *EventsModule) Event(i *discordgo.InteractionCreate) error {
	var err error
	eventType := i.ApplicationCommandData().Options[0].IntValue()
	enableEvent := i.ApplicationCommandData().Options[1].BoolValue()
	event_chat_id := m.Config.EventChatChannelId
	online_role := m.Config.Roles["online_role"]
	var eventStr string

	if enableEvent {
		m.Bot.Discord.ChannelPermissionSet(event_chat_id, online_role, discordgo.PermissionOverwriteTypeRole, discordgo.PermissionSendMessages|discordgo.PermissionAttachFiles, 0)
		err = m.openEventVoiceChannel(eventType)
	} else {
		m.Bot.Discord.ChannelPermissionSet(event_chat_id, online_role, discordgo.PermissionOverwriteTypeRole, 0, discordgo.PermissionSendMessages|discordgo.PermissionAttachFiles)
		err = m.closeEventVoiceChannel(eventType)
	}

	if err != nil {
		return err
	}

	if eventType == 0 {
		eventStr = "Stage"
	} else if eventType == 1 {
		eventStr = "Stream"
	}

	err = m.Bot.Discord.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: fmt.Sprintf("Event %s mode is now set to %t", eventStr, enableEvent),
		},
	})
	return err
}

func (m *EventsModule) openEventVoiceChannel(eventType int64) error {
	var err error
	if eventType == 0 { // STAGE
		err = m.Bot.Discord.ChannelPermissionSet(m.Config.EventStageChannelId, m.Config.Roles["online_role"], discordgo.PermissionOverwriteTypeRole, discordgo.PermissionVoiceConnect, discordgo.PermissionSendMessages|discordgo.PermissionAttachFiles)
	} else if eventType == 1 { // STREAM VC
		err = m.Bot.Discord.ChannelPermissionSet(m.Config.EventStreamChannelId, m.Config.Roles["online_role"], discordgo.PermissionOverwriteTypeRole, discordgo.PermissionVoiceConnect, discordgo.PermissionSendMessages|discordgo.PermissionAttachFiles)
	}
	return err
}

func (m *EventsModule) closeEventVoiceChannel(eventType int64) error {
	var err error
	if eventType == 0 { // STAGE
		err = m.Bot.Discord.ChannelPermissionSet(m.Config.EventStageChannelId, m.Config.Roles["online_role"], discordgo.PermissionOverwriteTypeRole, 0, discordgo.PermissionVoiceConnect|discordgo.PermissionSendMessages|discordgo.PermissionAttachFiles)
	} else if eventType == 1 { // STREAM VC
		err = m.Bot.Discord.ChannelPermissionSet(m.Config.EventStreamChannelId, m.Config.Roles["online_role"], discordgo.PermissionOverwriteTypeRole, 0, discordgo.PermissionVoiceConnect|discordgo.PermissionSendMessages|discordgo.PermissionAttachFiles)
	}
	return err
}
