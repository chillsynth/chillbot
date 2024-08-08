package admin

import (
	"chillbot/internal/bot"
	"errors"
	"fmt"
	"github.com/bwmarrin/discordgo"
)

type AdminModule struct {
	bot.CommonDeps
	name string
}

func (m *AdminModule) Load(deps *bot.CommonDeps) error {
	m.Bot = deps.Bot
	m.Logger = deps.Logger
	m.Config = deps.Config
	m.name = "AdminModule"

	/*
		err, _ :=
			m.Bot.AddCommand(&discordgo.ApplicationCommand{
				Name:        "admin",
				Description: "admin command",
			}, m.AdminTest, "Admin"),
	*/

	err, _ := m.Bot.AddCommand(&discordgo.ApplicationCommand{
		Name:        "create_invite",
		Description: "Create an invite URL for a channel",
		Options: []*discordgo.ApplicationCommandOption{
			{
				Type:        discordgo.ApplicationCommandOptionChannel,
				Name:        "channel",
				Description: "Where to create the invite",
				Required:    true,
			},
			{
				Type:        discordgo.ApplicationCommandOptionInteger,
				Name:        "max_age",
				Required:    true,
				Description: "Time (in seconds) until invite expires",
			},
			{
				Type:        discordgo.ApplicationCommandOptionInteger,
				Name:        "max_uses",
				Required:    true,
				Description: "Amount of times invite can be used",
			},
			{
				Type:        discordgo.ApplicationCommandOptionBoolean,
				Name:        "temporary",
				Required:    true,
				Description: "Only grant temporary membership using invite",
			},
		},
	}, m.InviteCreator, "Admin"),
		m.Bot.AddCommand(&discordgo.ApplicationCommand{
			Name:        "deletecmd",
			Description: "Delete a command via ID",
			Options: []*discordgo.ApplicationCommandOption{
				{
					Type:        discordgo.ApplicationCommandOptionString,
					Name:        "command_id",
					Description: "Command ID to be deleted",
					Required:    true,
				},
				{
					Type:        discordgo.ApplicationCommandOptionBoolean,
					Name:        "guild_id",
					Description: "Guild ID that command belongs to",
					Required:    false,
				},
			},
		}, m.DeleteCommand, "Admin")

	// bot.AddHandler(m.Bot, m.DeleteCommand)

	return err
}

func (m *AdminModule) GetName() string {
	return m.name
}

func (m *AdminModule) AdminTest(i *discordgo.InteractionCreate) error {
	err := m.Bot.Discord.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: "im an admin command!",
		},
	})
	return err
}

func (m *AdminModule) InviteCreator(i *discordgo.InteractionCreate) error {
	channel := i.ApplicationCommandData().Options[0].ChannelValue(m.Bot.Discord)
	invite, err := m.Bot.Discord.ChannelInviteCreate(
		channel.ID,
		discordgo.Invite{
			MaxAge:    int(i.ApplicationCommandData().Options[1].IntValue()),
			MaxUses:   int(i.ApplicationCommandData().Options[2].IntValue()),
			Temporary: i.ApplicationCommandData().Options[3].BoolValue(),
		})
	if err != nil {
		// Handle error
		return err
	}

	err2 := m.Bot.Discord.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: fmt.Sprintf("New invite: https://discord.gg/%s", invite.Code),
		},
	})
	err = errors.Join(err, err2)
	return err
}

func (m *AdminModule) DeleteCommand(i *discordgo.InteractionCreate) error {
	var err error
	if i.ApplicationCommandData().Options[1].BoolValue() == false {
		err = m.Bot.Discord.ApplicationCommandDelete(
			m.Bot.Discord.State.User.ID,
			"",
			i.ApplicationCommandData().Options[0].StringValue())
	} else {
		err = m.Bot.Discord.ApplicationCommandDelete(
			m.Bot.Discord.State.User.ID,
			i.GuildID,
			i.ApplicationCommandData().Options[0].StringValue())
	}
	err2 := m.Bot.Discord.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: fmt.Sprintf("Deleted command ID: %s", i.ApplicationCommandData().Options[0].StringValue()),
		},
	})
	err = errors.Join(err, err2)
	return err
}
