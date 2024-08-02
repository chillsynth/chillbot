package main

import (
	"chillbot/internal/config"
	"chillbot/internal/logging"
	"log/slog"
	"os"
)

func main() {
	opts := &slog.HandlerOptions{
		Level: slog.LevelDebug, // Can be changed from LevelDebug to LevelInfo between LIVE and DEV states
	}

	logger := &logging.Logger{
		Slog: slog.New(slog.NewJSONHandler(os.Stdout, opts)),
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
