package main

import (
	"chillbot/internal/bot"

	"github.com/bwmarrin/discordgo"
)

type Container struct {
	Discord *discordgo.Session
	Bot     *bot.Bot
}
