package logging

import "log/slog"

type Logger struct {
	Slog *slog.Logger
}

func (l *Logger) LogInfo(msg string, args ...any) {
	l.Slog.Info(msg, args...)
}

func (l *Logger) LogWarning(msg string, args ...any) {
	l.Slog.Warn(msg, args...)
}

func (l *Logger) LogError(msg string, args ...any) {
	l.Slog.Error(msg, args...)
}
