package main

import (
	"chillbot/internal/config"
	"chillbot/internal/logging"
	"log/slog"
	"os"
)

func main() {
	logger := &logging.Logger{
		Slog: slog.New(slog.NewJSONHandler(os.Stdout, nil)),
	}

	slog.SetDefault(logger.Slog)

	conf := &config.Config{}
	err := conf.Load(logger)
	if err != nil {
		logger.LogFatal("Cannot load config file %s", err.Error())
	}

	b := NewBuilder(logger, conf)

	err = b.Build()
	if err != nil {
		logger.LogFatal("Error building the bot %s", err.Error())
	}

	b.Bot.Run()
}
