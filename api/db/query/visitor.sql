-- name: CreateVisitor :one
INSERT INTO visitors (
  visitor_id,
  visitor_name,
  encoding,
  image,
  visits_count
) VALUES (
  $1, $2, $3, $4, $5
) RETURNING *;

-- name: GetVisitor :one
SELECT * FROM visitors
WHERE visitor_id = $1 LIMIT 1;

-- name: ListVisitors :many
SELECT * FROM visitors
ORDER BY visitor_id
LIMIT $1
OFFSET $2;

-- name: UpdateVisitor :one
UPDATE visitors
SET visitor_name = $2
WHERE visitor_id = $1
RETURNING *;

-- name: AddVisitorCount :one
UPDATE visitors
SET visitor_count = visitor_count + 1
WHERE visitor_id = sqlc.arg(visitor_id)
RETURNING *;

-- name: DeleteVisitor :exec
DELETE FROM visitors
WHERE visitor_id = $1;
