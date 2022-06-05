// Code generated by sqlc. DO NOT EDIT.
// versions:
//   sqlc v1.13.0

package db

import (
	"time"

	"github.com/google/uuid"
)

type Admin struct {
	AdminName         string        `json:"admin_name"`
	HashedPassword    string        `json:"hashed_password"`
	FullName          string        `json:"full_name"`
	Email             string        `json:"email"`
	PasswordChangedAt time.Time     `json:"password_changed_at"`
	CreatedAt         time.Time     `json:"created_at"`
	ChangedUserID     uuid.NullUUID `json:"changed_user_id"`
	DeletedUserID     uuid.NullUUID `json:"deleted_user_id"`
}

type Session struct {
	SessionID    uuid.UUID `json:"session_id"`
	Username     string    `json:"username"`
	RefreshToken string    `json:"refresh_token"`
	UserAgent    string    `json:"user_agent"`
	ClientIp     string    `json:"client_ip"`
	IsBlocked    bool      `json:"is_blocked"`
	ExpiresAt    time.Time `json:"expires_at"`
	CreatedAt    time.Time `json:"created_at"`
}

type Visitor struct {
	VisitorID      uuid.UUID   `json:"visitor_id"`
	VisitorName    string      `json:"visitor_name"`
	Encoding       interface{} `json:"encoding"`
	Image          string      `json:"image"`
	VisitsCount    int32       `json:"visits_count"`
	RecentAccessAt time.Time   `json:"recent_access_at"`
	CreatedAt      time.Time   `json:"created_at"`
	UpdatedAt      time.Time   `json:"updated_at"`
}
