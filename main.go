package main

import (
	"chillbot/internal/config"
	"chillbot/internal/logging"
	"log"
	"log/slog"
	"os"
)

func main() {
	conf := &config.Config{}
	err := conf.Load()
	if err != nil {
		log.Fatalf("Cannot load config file %s", err.Error())
	}

	logLevel := slog.LevelInfo
	if conf.Environment == "local" {
		logLevel = slog.LevelDebug
	}

	opts := &slog.HandlerOptions{
		Level: logLevel,
	}

	logger := &logging.Logger{
		Slog: slog.New(slog.NewJSONHandler(os.Stdout, opts)),
	}

	slog.SetDefault(logger.Slog)

	b := NewBuilder(logger, conf)

	err = b.Build()
	if err != nil {
		log.Fatalf("Error building the bot %s", err.Error())
	}

	b.Bot.Run()
}
