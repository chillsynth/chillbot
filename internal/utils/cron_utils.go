package utils

import "chillbot/internal/logging"

func Job(cmd func() error, l *logging.Logger) func() {
	return func() {
		err := cmd()
		if err != nil {
			l.LogError(err)
		}
	}
}
