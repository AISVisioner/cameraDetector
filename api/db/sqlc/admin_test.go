package db

import (
	"context"
	"testing"
	"time"

	"github.com/AISVisioner/greeting-kiosk/api/util"
	"github.com/stretchr/testify/require"
)

func createRandomAdmin(t *testing.T) Admin {
	hashedPassword, err := util.HashPassword(util.RandomString(6))
	require.NoError(t, err)

	arg := CreateAdminParams{
		AdminName:      util.RandomPerson(),
		HashedPassword: hashedPassword,
		FullName:       util.RandomPerson(),
		Email:          util.RandomEmail(),
	}

	admin, err := testQueries.CreateAdmin(context.Background(), arg)
	require.NoError(t, err)
	require.NotEmpty(t, admin)

	require.Equal(t, arg.AdminName, admin.AdminName)
	require.Equal(t, arg.HashedPassword, admin.HashedPassword)
	require.Equal(t, arg.FullName, admin.FullName)
	require.Equal(t, arg.Email, admin.Email)
	require.True(t, admin.PasswordChangedAt.IsZero())
	require.NotZero(t, admin.CreatedAt)

	return admin
}

func TestCreateAdmin(t *testing.T) {
	createRandomAdmin(t)
}

func TestGetAdmin(t *testing.T) {
	admin1 := createRandomAdmin(t)
	admin2, err := testQueries.GetAdmin(context.Background(), admin1.AdminName)
	require.NoError(t, err)
	require.NotEmpty(t, admin2)

	require.Equal(t, admin1.AdminName, admin2.AdminName)
	require.Equal(t, admin1.HashedPassword, admin2.HashedPassword)
	require.Equal(t, admin1.FullName, admin2.FullName)
	require.Equal(t, admin1.Email, admin2.Email)
	require.WithinDuration(t, admin1.PasswordChangedAt, admin2.PasswordChangedAt, time.Second)
	require.WithinDuration(t, admin1.CreatedAt, admin2.CreatedAt, time.Second)
}
