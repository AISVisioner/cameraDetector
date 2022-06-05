package log

import (
	"fmt"
	"os"
	"sync"
)

type Log struct {
	ErrorLog *Logger
	WarnLog  *Logger
	InfoLog  *Logger
	DebugLog *Logger
	TraceLog *Logger
}

// Warn global og 情報を記録
func (log *Log) Warn(args ...interface{}) {
	clog.WarnLog.Log(WarnLevel, args...)
}

// Info global og 情報を記録
func Error(args error) {
	clog.ErrorLog.Log(ErrorLevel, fmt.Sprintf("%+v", args))
}

func Errors(args ...interface{}) {
	clog.ErrorLog.Log(ErrorLevel, args...)
}

// Info global og 情報を記録
func Info(args ...interface{}) {
	clog.InfoLog.Log(InfoLevel, args...)
}

func Debug(args ...interface{}) {
	clog.DebugLog.Log(DebugLevel, args...)
}

var (
	clog    Log
	initLog sync.Once
)

func InitLog() {
	initLog.Do(func() {
		level, err := GetLogLevel()
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		clog = Log{
			DebugLog: NewLogger(os.Stdout, DebugLevel, Ldate|Ltime|Lshortfile, "ADMIN-API", level),
			InfoLog:  NewLogger(os.Stdout, InfoLevel, Ldate|Ltime|Lshortfile, "ADMIN-API", level),
			WarnLog:  NewLogger(os.Stdout, WarnLevel, Ldate|Ltime|Lshortfile, "ADMIN-API", level),
			ErrorLog: NewLogger(os.Stdout, ErrorLevel, Ldate|Ltime|Lshortfile, "ADMIN-API", level),
		}
	})
}
func GetLogLevel() (Level, error) {
	var l Level
	var err error
	if os.Getenv("LOG_LEVEL") == "" {
		l = TraceLevel
	} else {
		l, err = ParseLevel(os.Getenv("LOG_LEVEL"))
	}
	return l, err
}
