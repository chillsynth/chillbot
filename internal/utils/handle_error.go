package utils

import (
	"log/slog"
)

func HandleError(err error) {
	if err != nil {
		slog.Error(err.Error())
	}
}
