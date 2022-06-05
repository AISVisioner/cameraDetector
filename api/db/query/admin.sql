-- name: CreateAdmin :one
INSERT INTO admins (
  admin_name,
  hashed_password,
  full_name,
  email
) VALUES (
  $1, $2, $3, $4
) RETURNING *;

-- name: GetAdmin :one
SELECT * FROM admins
WHERE admin_name = $1 LIMIT 1;