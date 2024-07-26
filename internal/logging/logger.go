package logging

import (
	"log"
	"log/slog"
)

type Logger struct {
	Slog *slog.Logger
}

func (l *Logger) LogInfo(msg string, args ...any) {
	l.Slog.Info(msg, args...)
}

func (l *Logger) LogWarning(msg string, args ...any) {
	l.Slog.Warn(msg, args...)
}

func (l *Logger) LogError(err error) {
	l.Slog.Error("error", "err", err)
}

func (l *Logger) LogFatal(fmt string, args ...any) {
	log.Fatalf(fmt, args...)
}
