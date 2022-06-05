package util

import (
	"fmt"
	"math/rand"
	"strconv"
	"strings"
	"time"

	"github.com/google/uuid"
)

const alphabet = "abcdefghijklmnopqrstuvwxyz"

func init() {
	rand.Seed(time.Now().UnixNano())
}

// RandomInt generates a random integer between min and max
func RandomInt(min, max int32) int32 {
	return min + rand.Int31n(max-min+1)
}

// RandomString generates a random string of length n
func RandomString(n int) string {
	var sb strings.Builder
	k := len(alphabet)

	for i := 0; i < n; i++ {
		c := alphabet[rand.Intn(k)]
		sb.WriteByte(c)
	}

	return sb.String()
}

// RandomPerson generates a random owner name
func RandomPerson() string {
	return RandomString(6)
}

// RandomEmail generates a random email
func RandomEmail() string {
	return fmt.Sprintf("%s@email.com", RandomString(6))
}

// RandomEncoding generates a random encoding
func RandomEncoding(size int) string {

	slice := make([]string, size)
	for i := 0; i < size; i++ {
		slice[i] = strconv.FormatFloat(rand.Float64()-rand.Float64(), 'f', -1, 64)
	}
	joinedStr := "{" + strings.Join(slice, ", ") + "}"
	return joinedStr
}

func RandomUUID() uuid.UUID {
	u, _ := uuid.NewRandom()
	return u
}
