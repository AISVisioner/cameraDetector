package api

import (
	"database/sql"
	"net/http"

	db "github.com/AISVisioner/greeting-kiosk/api/db/sqlc"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/lib/pq"
)

type createVisitorRequest struct {
	VisitorID   uuid.UUID   `json:"visitor_id" binging:"required"`
	VisitorName string      `json:"visitor_name" binging:"required"`
	Encoding    interface{} `json:"encoding" binging:"required"`
	Image       string      `json:"image" binging:"required"`
	VisitsCount int32       `json:"visits_count" binging:"required"`
}

func (server *Server) createVisitor(ctx *gin.Context) {
	var req createVisitorRequest
	if err := ctx.ShouldBindJSON(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, errorResponse(err))
		return
	}

	arg := db.CreateVisitorParams{
		VisitorID:   req.VisitorID,
		VisitorName: req.VisitorName,
		Encoding:    req.Encoding,
		Image:       req.Image,
		VisitsCount: req.VisitsCount,
	}

	visitor, err := server.store.CreateVisitor(ctx, arg)
	if err != nil {
		if pqErr, ok := err.(*pq.Error); ok {
			switch pqErr.Code.Name() {
			case "foreign_key_violation", "unique_violation":
				ctx.JSON(http.StatusForbidden, errorResponse(err))
				return
			}
		}
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}

	ctx.JSON(http.StatusOK, visitor)
}

type getVisitorRequest struct {
	VisitorID uuid.UUID `uri:"id" binding:"required,min=1"`
}

func (server *Server) getVisitor(ctx *gin.Context) {
	var req getVisitorRequest
	if err := ctx.ShouldBindUri(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, errorResponse(err))
		return
	}

	visitor, err := server.store.GetVisitor(ctx, req.VisitorID)
	if err != nil {
		if err == sql.ErrNoRows {
			ctx.JSON(http.StatusNotFound, errorResponse(err))
			return
		}

		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}

	ctx.JSON(http.StatusOK, visitor)
}

type listVisitorRequest struct {
	PageID   int32 `form:"page_id" binding:"required,min=1"`
	PageSize int32 `form:"page_size" binding:"required,min=5,max=10"`
}

func (server *Server) listVisitors(ctx *gin.Context) {
	var req listVisitorRequest
	if err := ctx.ShouldBindQuery(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, errorResponse(err))
		return
	}

	arg := db.ListVisitorsParams{
		Limit:  req.PageSize,
		Offset: (req.PageID - 1) * req.PageSize,
	}

	visitors, err := server.store.ListVisitors(ctx, arg)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}

	ctx.JSON(http.StatusOK, visitors)
}
