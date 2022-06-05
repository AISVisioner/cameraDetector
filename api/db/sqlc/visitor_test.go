package db

import (
	"context"
	"database/sql"
	"testing"
	"time"

	"github.com/AISVisioner/greeting-kiosk/api/util"
	"github.com/stretchr/testify/require"
)

func createRandomVisitor(t *testing.T) Visitor {

	arg := CreateVisitorParams{
		VisitorID:   util.RandomUUID(),
		VisitorName: util.RandomPerson(),
		Encoding:    util.RandomEncoding(128),
		Image:       "",
		VisitsCount: util.RandomInt(1, 1000),
	}

	visitor, err := testQueries.CreateVisitor(context.Background(), arg)
	require.NoError(t, err)
	require.NotEmpty(t, visitor)

	require.Equal(t, arg.VisitorID, visitor.VisitorID)
	require.Equal(t, arg.VisitorName, visitor.VisitorName)
	require.IsType(t, []uint8{}, visitor.Encoding)
	// require.Equal(t, arg.Encoding, visitor.Encoding)
	require.Equal(t, arg.Image, visitor.Image)
	require.Equal(t, arg.VisitsCount, visitor.VisitsCount)

	require.NotZero(t, visitor.VisitorID)
	require.NotZero(t, visitor.RecentAccessAt)
	require.NotZero(t, visitor.CreatedAt)
	require.NotZero(t, visitor.UpdatedAt)

	return visitor
}

func TestCreateVisitor(t *testing.T) {
	createRandomVisitor(t)
}

func TestGetVisitor(t *testing.T) {
	visitor1 := createRandomVisitor(t)
	visitor2, err := testQueries.GetVisitor(context.Background(), visitor1.VisitorID)
	require.NoError(t, err)
	require.NotEmpty(t, visitor2)

	require.Equal(t, visitor1.VisitorID, visitor2.VisitorID)
	require.Equal(t, visitor1.VisitorName, visitor2.VisitorName)
	require.IsType(t, []uint8{}, visitor1.Encoding)
	require.IsType(t, []uint8{}, visitor2.Encoding)
	require.Equal(t, visitor1.Image, visitor2.Image)
	require.Equal(t, visitor1.VisitsCount, visitor2.VisitsCount)
	require.WithinDuration(t, visitor1.CreatedAt, visitor2.CreatedAt, time.Second)
}

func TestUpdateVisitor(t *testing.T) {
	visitor1 := createRandomVisitor(t)

	arg := UpdateVisitorParams{
		VisitorID:   visitor1.VisitorID,
		VisitorName: util.RandomPerson(),
	}

	visitor2, err := testQueries.UpdateVisitor(context.Background(), arg)
	require.NoError(t, err)
	require.NotEmpty(t, visitor2)

	require.Equal(t, visitor1.VisitorID, visitor2.VisitorID)
	require.Equal(t, arg.VisitorName, visitor2.VisitorName)
	require.IsType(t, []uint8{}, visitor1.Encoding)
	require.IsType(t, []uint8{}, visitor2.Encoding)
	require.Equal(t, visitor1.Image, visitor2.Image)
	require.Equal(t, visitor1.VisitsCount, visitor2.VisitsCount)
	require.WithinDuration(t, visitor1.CreatedAt, visitor2.CreatedAt, time.Second)
}

func TestDeleteVisitor(t *testing.T) {
	visitor1 := createRandomVisitor(t)
	err := testQueries.DeleteVisitor(context.Background(), visitor1.VisitorID)
	require.NoError(t, err)

	visitor2, err := testQueries.GetVisitor(context.Background(), visitor1.VisitorID)
	require.Error(t, err)
	require.EqualError(t, err, sql.ErrNoRows.Error())
	require.Empty(t, visitor2)
}

func TestListVisitors(t *testing.T) {

	arg := ListVisitorsParams{
		Limit:  5,
		Offset: 0,
	}

	visitors, err := testQueries.ListVisitors(context.Background(), arg)
	require.NoError(t, err)
	require.NotEmpty(t, visitors)

	for _, visitor := range visitors {
		require.NotEmpty(t, visitor)
	}
}
