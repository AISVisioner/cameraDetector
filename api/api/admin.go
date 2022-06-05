package api

import (
	"database/sql"
	"fmt"
	"net/http"
	"time"

	db "github.com/AISVisioner/greeting-kiosk/api/db/sqlc"
	"github.com/AISVisioner/greeting-kiosk/api/util"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/lib/pq"
)

type createAdminRequest struct {
	AdminName string `json:"admin_name" binding:"required,alphanum"`
	Password  string `json:"password" binding:"required,min=6"`
	FullName  string `json:"full_name" binding:"required"`
	Email     string `json:"email" binding:"required,email"`
}

type adminResponse struct {
	AdminName         string    `json:"admin_name"`
	FullName          string    `json:"full_name"`
	Email             string    `json:"email"`
	PasswordChangedAt time.Time `json:"password_changed_at"`
	CreatedAt         time.Time `json:"created_at"`
}

func newAdminResponse(admin db.Admin) adminResponse {
	return adminResponse{
		AdminName:         admin.AdminName,
		FullName:          admin.FullName,
		Email:             admin.Email,
		PasswordChangedAt: admin.PasswordChangedAt,
		CreatedAt:         admin.CreatedAt,
	}
}

func (server *Server) createAdmin(ctx *gin.Context) {
	fmt.Println("createAdmin -->")
	var req createAdminRequest
	fmt.Println(req)
	if err := ctx.ShouldBindJSON(&req); err != nil {
		fmt.Println("createdAdmin --> StatusBadRequest")
		ctx.JSON(http.StatusBadRequest, errorResponse(err))
		return
	}

	hashedPassword, err := util.HashPassword(req.Password)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}

	arg := db.CreateAdminParams{
		AdminName:      req.AdminName,
		HashedPassword: hashedPassword,
		FullName:       req.FullName,
		Email:          req.Email,
	}

	admin, err := server.store.CreateAdmin(ctx, arg)
	if err != nil {
		if pqErr, ok := err.(*pq.Error); ok {
			switch pqErr.Code.Name() {
			case "unique_violation":
				ctx.JSON(http.StatusForbidden, errorResponse(err))
				return
			}
		}
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}

	rsp := newAdminResponse(admin)
	ctx.JSON(http.StatusOK, rsp)
	fmt.Println("createAdmin <--")
}

type loginAdminRequest struct {
	Adminname string `json:"admin_name" binding:"required,alphanum"`
	Password  string `json:"password" binding:"required,min=6"`
}

type loginAdminResponse struct {
	SessionID             uuid.UUID     `json:"session_id"`
	AccessToken           string        `json:"access_token"`
	AccessTokenExpiresAt  time.Time     `json:"access_token_expires_at"`
	RefreshToken          string        `json:"refresh_token"`
	RefreshTokenExpiresAt time.Time     `json:"refresh_token_expires_at"`
	Admin                 adminResponse `json:"admin"`
}

func (server *Server) loginAdmin(ctx *gin.Context) {
	var req loginAdminRequest
	if err := ctx.ShouldBindJSON(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, errorResponse(err))
		return
	}

	admin, err := server.store.GetAdmin(ctx, req.Adminname)
	if err != nil {
		if err == sql.ErrNoRows {
			ctx.JSON(http.StatusNotFound, errorResponse(err))
			return
		}
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}

	err = util.CheckPassword(req.Password, admin.HashedPassword)
	if err != nil {
		ctx.JSON(http.StatusUnauthorized, errorResponse(err))
		return
	}

	accessToken, accessPayload, err := server.tokenMaker.CreateToken(
		admin.AdminName,
		server.config.AccessTokenDuration,
	)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}

	refreshToken, refreshPayload, err := server.tokenMaker.CreateToken(
		admin.AdminName,
		server.config.RefreshTokenDuration,
	)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}

	session, err := server.store.CreateSession(ctx, db.CreateSessionParams{
		SessionID:    refreshPayload.ID,
		Username:     admin.AdminName,
		RefreshToken: refreshToken,
		UserAgent:    ctx.Request.UserAgent(),
		ClientIp:     ctx.ClientIP(),
		IsBlocked:    false,
		ExpiresAt:    refreshPayload.ExpiredAt,
	})
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}

	rsp := loginAdminResponse{
		SessionID:             session.SessionID,
		AccessToken:           accessToken,
		AccessTokenExpiresAt:  accessPayload.ExpiredAt,
		RefreshToken:          refreshToken,
		RefreshTokenExpiresAt: refreshPayload.ExpiredAt,
		Admin:                 newAdminResponse(admin),
	}
	ctx.JSON(http.StatusOK, rsp)
}
