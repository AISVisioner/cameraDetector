package log

import (
	"fmt"
	"io"
	"os"
	"runtime"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

const (
	Ldate         = 1 << iota     // the date in the local time zone: 2009/01/23
	Ltime                         // the time in the local time zone: 01:23:23
	Lmicroseconds                 // microsecond resolution: 01:23:23.123123.  assumes Ltime.
	Llongfile                     // full file name and line number: /a/b/c/d.go:23
	Lshortfile                    // final file name element and line number: d.go:23. overrides Llongfile
	LUTC                          // if Ldate or Ltime is set, use UTC rather than the local time zone
	Lmsgprefix                    // move the "prefix" from the beginning of the line to before the message
	LstdFlags     = Ldate | Ltime // initial values for the standard logger
)

type Logger struct {
	mu     sync.Mutex // ensures atomic writes; protects the following fields
	prefix string     // prefix on each line to identify the logger (but see Lmsgprefix)
	task   string
	flag   int       // properties
	out    io.Writer // destination for output
	buf    []byte    // for accumulating text to write
	Level  Level
}

func New(out io.Writer, prefix string, flag int) *Logger {
	return &Logger{out: out, flag: flag, prefix: prefix}
}

func NewLogger(out io.Writer, priefix Level, flag int, task string, level Level) *Logger {
	prefix, _ := MarshalText(priefix)
	return &Logger{out: out, flag: flag, task: task, prefix: string(prefix), Level: level}
}

// SetOutput sets the output destination for the logger.
func (l *Logger) SetOutput(w io.Writer) {
	l.mu.Lock()
	defer l.mu.Unlock()
	l.out = w
}

var std = New(os.Stderr, "", LstdFlags)

// Default returns the standard logger used by the package-level output functions.
func Default() *Logger { return std }

// Cheap integer to fixed-width decimal ASCII. Give a negative width to avoid zero-padding.
func itoa(buf *[]byte, i int, wid int) {
	// Assemble decimal in reverse order.
	var b [20]byte
	bp := len(b) - 1
	for i >= 10 || wid > 1 {
		wid--
		q := i / 10
		b[bp] = byte('0' + i - q*10)
		bp--
		i = q
	}
	// i < 10
	b[bp] = byte('0' + i)
	*buf = append(*buf, b[bp:]...)
}

func (l *Logger) formatHeader(buf *[]byte, t time.Time, file string, line int) {

	if l.flag&(Ldate|Ltime|Lmicroseconds) != 0 {
		if l.flag&LUTC != 0 {
			t = t.UTC()
		}
		if l.flag&Ldate != 0 {
			year, month, day := t.Date()
			itoa(buf, year, 4)
			*buf = append(*buf, '-')
			itoa(buf, int(month), 2)
			*buf = append(*buf, '-')
			itoa(buf, day, 2)
			*buf = append(*buf, ' ')
		}
		if l.flag&(Ltime|Lmicroseconds) != 0 {
			hour, min, sec := t.Clock()
			itoa(buf, hour, 2)
			*buf = append(*buf, ':')
			itoa(buf, min, 2)
			*buf = append(*buf, ':')
			itoa(buf, sec, 2)
			if l.flag&Lmicroseconds != 0 {
				*buf = append(*buf, '.')
				itoa(buf, t.Nanosecond()/1e3, 6)
			}
			*buf = append(*buf, ' ')
		}
	}

	if l.task != "" {
		*buf = append(*buf, '[')
		*buf = append(*buf, l.task...)
		*buf = append(*buf, ']', ' ')
	}

	if l.flag&Lmsgprefix == 0 {
		*buf = append(*buf, l.prefix...)
	}
	if l.flag&Lmsgprefix != 0 {
		*buf = append(*buf, l.prefix...)
	}

	if l.flag&(Lshortfile|Llongfile) != 0 {
		if l.flag&Lshortfile != 0 {
			short := file
			for i := len(file) - 1; i > 0; i-- {
				if file[i] == '/' {
					short = file[i+1:]
					break
				}
			}
			file = short
		}
		*buf = append(*buf, file...)
		*buf = append(*buf, ':')
		itoa(buf, line, -1)
		*buf = append(*buf, ": "...)
	}

}

func (l *Logger) Output(calldepth int, s string) error {

	now := time.Now() // get this early.
	var file string
	var line int
	l.mu.Lock()
	defer l.mu.Unlock()
	if l.flag&(Lshortfile|Llongfile) != 0 {
		// Release lock while getting caller info - it's expensive.
		l.mu.Unlock()
		var ok bool
		_, file, line, ok = runtime.Caller(calldepth)
		if !ok {
			file = "???"
			line = 0
		}
		l.mu.Lock()
	}
	l.buf = l.buf[:0]
	l.formatHeader(&l.buf, now, file, line)
	l.buf = append(l.buf, s...)
	if len(s) == 0 || s[len(s)-1] != '\n' {
		l.buf = append(l.buf, '\n')
	}
	_, err := l.out.Write(l.buf)
	return err
}

func (l *Logger) Printf(format string, v ...interface{}) {
	l.Output(4, fmt.Sprintf(format, v...))
}

func (l *Logger) Print(v ...interface{}) { l.Output(4, fmt.Sprint(v...)) }

func (l *Logger) Println(v ...interface{}) { l.Output(4, fmt.Sprintln(v...)) }

func (l *Logger) Fatal(v ...interface{}) {
	l.Output(2, fmt.Sprint(v...))
	os.Exit(1)
}

// Fatalf is equivalent to l.Printf() followed by a call to os.Exit(1).
func (l *Logger) Fatalf(format string, v ...interface{}) {
	l.Output(2, fmt.Sprintf(format, v...))
	os.Exit(1)
}

// Fatalln is equivalent to l.Println() followed by a call to os.Exit(1).
func (l *Logger) Fatalln(v ...interface{}) {
	l.Output(2, fmt.Sprintln(v...))
	os.Exit(1)
}

// Panic is equivalent to l.Print() followed by a call to panic().
func (l *Logger) Panic(v ...interface{}) {
	s := fmt.Sprint(v...)
	l.Output(2, s)
	panic(s)
}

// Panicf is equivalent to l.Printf() followed by a call to panic().
func (l *Logger) Panicf(format string, v ...interface{}) {
	s := fmt.Sprintf(format, v...)
	l.Output(2, s)
	panic(s)
}

// Panicln is equivalent to l.Println() followed by a call to panic().
func (l *Logger) Panicln(v ...interface{}) {
	s := fmt.Sprintln(v...)
	l.Output(2, s)
	panic(s)
}

// Flags returns the output flags for the logger.
// The flag bits are Ldate, Ltime, and so on.
func (l *Logger) Flags() int {
	l.mu.Lock()
	defer l.mu.Unlock()
	return l.flag
}

// SetFlags sets the output flags for the logger.
// The flag bits are Ldate, Ltime, and so on.
func (l *Logger) SetFlags(flag int) {
	l.mu.Lock()
	defer l.mu.Unlock()
	l.flag = flag
}

// Prefix returns the output prefix for the logger.
func (l *Logger) Prefix() string {
	l.mu.Lock()
	defer l.mu.Unlock()
	return l.prefix
}

// SetPrefix sets the output prefix for the logger.
func (l *Logger) SetPrefix(prefix string) {
	l.mu.Lock()
	defer l.mu.Unlock()
	l.prefix = prefix
}

// Writer returns the output destination for the logger.
func (l *Logger) Writer() io.Writer {
	l.mu.Lock()
	defer l.mu.Unlock()
	return l.out
}

// SetOutput sets the output destination for the standard logger.
func SetOutput(w io.Writer) {
	std.mu.Lock()
	defer std.mu.Unlock()
	std.out = w
}

// Flags returns the output flags for the standard logger.
// The flag bits are Ldate, Ltime, and so on.
func Flags() int {
	return std.Flags()
}

// SetFlags sets the output flags for the standard logger.
// The flag bits are Ldate, Ltime, and so on.
func SetFlags(flag int) {
	std.SetFlags(flag)
}

// Prefix returns the output prefix for the standard logger.
func Prefix() string {
	return std.Prefix()
}

// SetPrefix sets the output prefix for the standard logger.
func SetPrefix(prefix string) {
	std.SetPrefix(prefix)
}

// Writer returns the output destination for the standard logger.
func Writer() io.Writer {
	return std.Writer()
}

func Print(v ...interface{}) {
	std.Output(4, fmt.Sprint(v...))
}

func Printf(format string, v ...interface{}) {
	std.Output(4, fmt.Sprintf(format, v...))
}

func Println(v ...interface{}) {
	std.Output(4, fmt.Sprintln(v...))
}

// Fatal is equivalent to Print() followed by a call to os.Exit(1).
func Fatal(v ...interface{}) {
	std.Output(2, fmt.Sprint(v...))
	os.Exit(1)
}

// Fatalf is equivalent to Printf() followed by a call to os.Exit(1).
func Fatalf(format string, v ...interface{}) {
	std.Output(2, fmt.Sprintf(format, v...))
	os.Exit(1)
}

// Fatalln is equivalent to Println() followed by a call to os.Exit(1).
func Fatalln(v ...interface{}) {
	std.Output(2, fmt.Sprintln(v...))
	os.Exit(1)
}

// Panic is equivalent to Print() followed by a call to panic().
func Panic(v ...interface{}) {
	s := fmt.Sprint(v...)
	std.Output(2, s)
	panic(s)
}

// Panicf is equivalent to Printf() followed by a call to panic().
func Panicf(format string, v ...interface{}) {
	s := fmt.Sprintf(format, v...)
	std.Output(2, s)
	panic(s)
}

// Panicln is equivalent to Println() followed by a call to panic().
func Panicln(v ...interface{}) {
	s := fmt.Sprintln(v...)
	std.Output(2, s)
	panic(s)
}

func Output(calldepth int, s string) error {
	return std.Output(calldepth+1, s) // +1 for this frame.
}

const (
	PanicLevel Level = iota
	FatalLevel
	ErrorLevel
	WarnLevel
	InfoLevel
	DebugLevel
	TraceLevel
)

func MarshalText(level Level) ([]byte, error) {
	switch level {
	case TraceLevel:
		return []byte("TRACE "), nil
	case DebugLevel:
		return []byte("DEBUG "), nil
	case InfoLevel:
		return []byte("INFO "), nil
	case WarnLevel:
		return []byte("WARN "), nil
	case ErrorLevel:
		return []byte("ERROR "), nil
	case FatalLevel:
		return []byte("FATAL "), nil
	case PanicLevel:
		return []byte("PANIC "), nil
	}

	return nil, fmt.Errorf("not a valid log level %d", level)
}
func ParseLevel(lvl string) (Level, error) {
	switch strings.ToLower(lvl) {
	case "panic", "PANIC":
		return PanicLevel, nil
	case "fatal", "FATAL":
		return FatalLevel, nil
	case "error", "ERROR":
		return ErrorLevel, nil
	case "warn", "warning", "WARN", "WARNING":
		return WarnLevel, nil
	case "info", "INFO":
		return InfoLevel, nil
	case "debug", "DEBUG":
		return DebugLevel, nil
	case "trace", "TRACE":
		return TraceLevel, nil
	}
	var l Level
	return l, fmt.Errorf("not a valid log Level: %q", lvl)
}

// Level type
type Level uint32

func (l *Logger) IsLevelEnabled(level Level) bool {
	return l.level() >= level
}
func (l *Logger) level() Level {
	return Level(atomic.LoadUint32((*uint32)(&l.Level)))
}

// SetLevel sets the logger level.
func (l *Logger) SetLevel(level Level) {
	atomic.StoreUint32((*uint32)(&l.Level), uint32(level))
}

func (l *Logger) SetTask(task string) {
	l.task = task
}

func (l *Logger) Error(args ...interface{}) {
	l.Log(ErrorLevel, args...)
}
func (l *Logger) Log(level Level, args ...interface{}) {
	if l.IsLevelEnabled(level) {
		l.Println(args...)
	}
}
