package api

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"reflect"
	"testing"

	mockdb "github.com/AISVisioner/greeting-kiosk/api/db/mock"
	db "github.com/AISVisioner/greeting-kiosk/api/db/sqlc"
	"github.com/AISVisioner/greeting-kiosk/api/util"
	"github.com/gin-gonic/gin"
	"github.com/golang/mock/gomock"
	"github.com/lib/pq"
	"github.com/stretchr/testify/require"
)

type eqCreateAdminParamsMatcher struct {
	arg      db.CreateAdminParams
	password string
}

func (e eqCreateAdminParamsMatcher) Matches(x interface{}) bool {
	arg, ok := x.(db.CreateAdminParams)
	if !ok {
		return false
	}

	err := util.CheckPassword(e.password, arg.HashedPassword)
	if err != nil {
		return false
	}

	e.arg.HashedPassword = arg.HashedPassword
	return reflect.DeepEqual(e.arg, arg)
}

func (e eqCreateAdminParamsMatcher) String() string {
	return fmt.Sprintf("matches arg %v and password %v", e.arg, e.password)
}

func EqCreateAdminParams(arg db.CreateAdminParams, password string) gomock.Matcher {
	return eqCreateAdminParamsMatcher{arg, password}
}

func TestCreateAdminAPI(t *testing.T) {
	admin, password := randomAdmin(t)

	testCases := []struct {
		name          string
		body          gin.H
		buildStubs    func(store *mockdb.MockStore)
		checkResponse func(recoder *httptest.ResponseRecorder)
	}{
		{
			name: "OK",
			body: gin.H{
				"admin_name": admin.AdminName,
				"password":   password,
				"full_name":  admin.FullName,
				"email":      admin.Email,
			},
			buildStubs: func(store *mockdb.MockStore) {
				arg := db.CreateAdminParams{
					AdminName:      admin.AdminName,
					HashedPassword: password,
					FullName:       admin.FullName,
					Email:          admin.Email,
				}
				store.EXPECT().
					CreateAdmin(gomock.Any(), EqCreateAdminParams(arg, password)).
					Times(1).
					Return(admin, nil)
			},
			checkResponse: func(recorder *httptest.ResponseRecorder) {
				require.Equal(t, http.StatusOK, recorder.Code)
				requireBodyMatchAdmin(t, recorder.Body, admin)
			},
		},
		{
			name: "InternalError",
			body: gin.H{
				"admin_name": admin.AdminName,
				"password":   password,
				"full_name":  admin.FullName,
				"email":      admin.Email,
			},
			buildStubs: func(store *mockdb.MockStore) {
				store.EXPECT().
					CreateAdmin(gomock.Any(), gomock.Any()).
					Times(1).
					Return(db.Admin{}, sql.ErrConnDone)
			},
			checkResponse: func(recorder *httptest.ResponseRecorder) {
				require.Equal(t, http.StatusInternalServerError, recorder.Code)
			},
		},
		{
			name: "DuplicateAdminname",
			body: gin.H{
				"admin_name": admin.AdminName,
				"password":   password,
				"full_name":  admin.FullName,
				"email":      admin.Email,
			},
			buildStubs: func(store *mockdb.MockStore) {
				store.EXPECT().
					CreateAdmin(gomock.Any(), gomock.Any()).
					Times(1).
					Return(db.Admin{}, &pq.Error{Code: "23505"})
			},
			checkResponse: func(recorder *httptest.ResponseRecorder) {
				require.Equal(t, http.StatusForbidden, recorder.Code)
			},
		},
		{
			name: "InvalidAdminname",
			body: gin.H{
				"admin_name": "invalid-admin#1",
				"password":   password,
				"full_name":  admin.FullName,
				"email":      admin.Email,
			},
			buildStubs: func(store *mockdb.MockStore) {
				store.EXPECT().
					CreateAdmin(gomock.Any(), gomock.Any()).
					Times(0)
			},
			checkResponse: func(recorder *httptest.ResponseRecorder) {
				require.Equal(t, http.StatusBadRequest, recorder.Code)
			},
		},
		{
			name: "InvalidEmail",
			body: gin.H{
				"admin_name": admin.AdminName,
				"password":   password,
				"full_name":  admin.FullName,
				"email":      "invalid-email",
			},
			buildStubs: func(store *mockdb.MockStore) {
				store.EXPECT().
					CreateAdmin(gomock.Any(), gomock.Any()).
					Times(0)
			},
			checkResponse: func(recorder *httptest.ResponseRecorder) {
				require.Equal(t, http.StatusBadRequest, recorder.Code)
			},
		},
		{
			name: "TooShortPassword",
			body: gin.H{
				"admin_name": admin.AdminName,
				"password":   "123",
				"full_name":  admin.FullName,
				"email":      admin.Email,
			},
			buildStubs: func(store *mockdb.MockStore) {
				store.EXPECT().
					CreateAdmin(gomock.Any(), gomock.Any()).
					Times(0)
			},
			checkResponse: func(recorder *httptest.ResponseRecorder) {
				require.Equal(t, http.StatusBadRequest, recorder.Code)
			},
		},
	}

	for i := range testCases {
		tc := testCases[i]

		t.Run(tc.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			store := mockdb.NewMockStore(ctrl)
			tc.buildStubs(store)

			server := newTestServer(t, store)
			recorder := httptest.NewRecorder()

			// Marshal body data to JSON
			data, err := json.Marshal(tc.body)
			require.NoError(t, err)

			url := "/admins"
			request, err := http.NewRequest(http.MethodPost, url, bytes.NewReader(data))
			require.NoError(t, err)

			server.router.ServeHTTP(recorder, request)
			tc.checkResponse(recorder)
		})
	}
}

func TestLoginAdminAPI(t *testing.T) {
	admin, password := randomAdmin(t)

	testCases := []struct {
		name          string
		body          gin.H
		buildStubs    func(store *mockdb.MockStore)
		checkResponse func(recoder *httptest.ResponseRecorder)
	}{
		{
			name: "OK",
			body: gin.H{
				"admin_name": admin.AdminName,
				"password":   password,
			},
			buildStubs: func(store *mockdb.MockStore) {
				store.EXPECT().
					GetAdmin(gomock.Any(), gomock.Eq(admin.AdminName)).
					Times(1).
					Return(admin, nil)
				store.EXPECT().
					CreateSession(gomock.Any(), gomock.Any()).
					Times(1)
			},
			checkResponse: func(recorder *httptest.ResponseRecorder) {
				require.Equal(t, http.StatusOK, recorder.Code)
			},
		},
		{
			name: "AdminNotFound",
			body: gin.H{
				"admin_name": "NotFound",
				"password":   password,
			},
			buildStubs: func(store *mockdb.MockStore) {
				store.EXPECT().
					GetAdmin(gomock.Any(), gomock.Any()).
					Times(1).
					Return(db.Admin{}, sql.ErrNoRows)
			},
			checkResponse: func(recorder *httptest.ResponseRecorder) {
				require.Equal(t, http.StatusNotFound, recorder.Code)
			},
		},
		{
			name: "IncorrectPassword",
			body: gin.H{
				"admin_name": admin.AdminName,
				"password":   "incorrect",
			},
			buildStubs: func(store *mockdb.MockStore) {
				store.EXPECT().
					GetAdmin(gomock.Any(), gomock.Eq(admin.AdminName)).
					Times(1).
					Return(admin, nil)
			},
			checkResponse: func(recorder *httptest.ResponseRecorder) {
				require.Equal(t, http.StatusUnauthorized, recorder.Code)
			},
		},
		{
			name: "InternalError",
			body: gin.H{
				"admin_name": admin.AdminName,
				"password":   password,
			},
			buildStubs: func(store *mockdb.MockStore) {
				store.EXPECT().
					GetAdmin(gomock.Any(), gomock.Any()).
					Times(1).
					Return(db.Admin{}, sql.ErrConnDone)
			},
			checkResponse: func(recorder *httptest.ResponseRecorder) {
				require.Equal(t, http.StatusInternalServerError, recorder.Code)
			},
		},
		{
			name: "InvalidAdminname",
			body: gin.H{
				"admin_name": "invalid-admin#1",
				"password":   password,
				"full_name":  admin.FullName,
				"email":      admin.Email,
			},
			buildStubs: func(store *mockdb.MockStore) {
				store.EXPECT().
					GetAdmin(gomock.Any(), gomock.Any()).
					Times(0)
			},
			checkResponse: func(recorder *httptest.ResponseRecorder) {
				require.Equal(t, http.StatusBadRequest, recorder.Code)
			},
		},
	}

	for i := range testCases {
		tc := testCases[i]

		t.Run(tc.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			store := mockdb.NewMockStore(ctrl)
			tc.buildStubs(store)

			server := newTestServer(t, store)
			recorder := httptest.NewRecorder()

			// Marshal body data to JSON
			data, err := json.Marshal(tc.body)
			require.NoError(t, err)

			url := "/admins/login"
			request, err := http.NewRequest(http.MethodPost, url, bytes.NewReader(data))
			require.NoError(t, err)

			server.router.ServeHTTP(recorder, request)
			tc.checkResponse(recorder)
		})
	}
}

func randomAdmin(t *testing.T) (admin db.Admin, password string) {
	password = util.RandomString(6)
	hashedPassword, err := util.HashPassword(password)
	require.NoError(t, err)

	admin = db.Admin{
		AdminName:      util.RandomPerson(),
		HashedPassword: hashedPassword,
		FullName:       util.RandomPerson(),
		Email:          util.RandomEmail(),
	}
	return
}

func requireBodyMatchAdmin(t *testing.T, body *bytes.Buffer, admin db.Admin) {
	data, err := ioutil.ReadAll(body)
	require.NoError(t, err)

	var gotAdmin db.Admin
	err = json.Unmarshal(data, &gotAdmin)

	require.NoError(t, err)
	require.Equal(t, admin.AdminName, gotAdmin.AdminName)
	require.Equal(t, admin.FullName, gotAdmin.FullName)
	require.Equal(t, admin.Email, gotAdmin.Email)
	require.Empty(t, gotAdmin.HashedPassword)
}
