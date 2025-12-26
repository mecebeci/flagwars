# Flag Wars API Documentation

This document provides detailed information about the Flag Wars REST API endpoints.

## Base URL

- **Development:** `http://localhost:8000/api`
- **Production:** `https://flagwars.mecebeci.com/api`

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the access token in the Authorization header for protected endpoints:

```
Authorization: Bearer <access_token>
```

## Interactive Documentation

- **Swagger UI:** `http://localhost:8000/api/docs/`
- **OpenAPI Schema:** `http://localhost:8000/api/schema/`

## Endpoints

### Authentication Endpoints

#### Register New User

```http
POST /api/auth/register/
```

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "password2": "string"
}
```

**Response:** `201 Created`
```json
{
  "user": {
    "id": 1,
    "username": "string",
    "email": "string"
  },
  "tokens": {
    "access": "string",
    "refresh": "string"
  }
}
```

**Errors:**
- `400 Bad Request` - Validation errors (passwords don't match, user exists, etc.)

---

#### Login

```http
POST /api/auth/login/
```

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:** `200 OK`
```json
{
  "access": "string",
  "refresh": "string",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string"
  }
}
```

**Errors:**
- `401 Unauthorized` - Invalid credentials

---

#### Refresh Token

```http
POST /api/auth/refresh/
```

**Request Body:**
```json
{
  "refresh": "string"
}
```

**Response:** `200 OK`
```json
{
  "access": "string"
}
```

**Errors:**
- `401 Unauthorized` - Invalid or expired refresh token

---

#### Logout

```http
POST /api/auth/logout/
```

**Authentication:** Required

**Request Body:**
```json
{
  "refresh": "string"
}
```

**Response:** `205 Reset Content`
```json
{
  "message": "Logged out successfully"
}
```

---

#### Get Current User

```http
GET /api/auth/me/
```

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "total_score": 0,
  "games_played": 0,
  "average_score": 0.0
}
```

---

### User Profile Endpoints

#### Get User Statistics

```http
GET /api/auth/profile/stats/
```

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "total_games": 0,
  "total_score": 0,
  "average_score": 0.0,
  "best_score": 0,
  "total_correct_answers": 0,
  "total_wrong_answers": 0,
  "accuracy_percentage": 0.0,
  "total_skips_used": 0,
  "average_game_duration": "00:00:00"
}
```

---

#### Get Recent Games

```http
GET /api/auth/profile/games/
```

**Authentication:** Required

**Query Parameters:**
- `limit` (optional) - Number of games to return (default: 10)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "score": 100,
    "started_at": "2024-01-15T10:30:00Z",
    "finished_at": "2024-01-15T10:45:00Z",
    "duration": "00:15:00",
    "correct_answers": 10,
    "wrong_answers": 2,
    "skips_used": 1
  }
]
```

---

### Game Endpoints

#### Start New Game

```http
POST /api/game/start/
```

**Authentication:** Required

**Response:** `201 Created`
```json
{
  "id": 1,
  "user": 1,
  "started_at": "2024-01-15T10:30:00Z",
  "score": 0,
  "skips_remaining": 3,
  "skips_used": 0,
  "is_completed": false,
  "current_country_id": null,
  "viewed_countries": []
}
```

**Errors:**
- `400 Bad Request` - No countries in database

---

#### Get Question

```http
GET /api/game/question/
```

**Authentication:** Required

**Description:** Retrieves the current flag question. If no current question exists, generates a new random flag that hasn't been shown yet in this session.

**Response:** `200 OK`
```json
{
  "country_id": 1,
  "flag_url": "http://flagwars.mecebeci.com/flags/us.png",
  "session_id": 1,
  "question_number": 5,
  "score": 40,
  "skips_remaining": 2
}
```

**Errors:**
- `404 Not Found` - No active game session found

**Notes:**
- Flag data is cached for 1 hour to reduce database load
- The same country won't appear twice in a single game session
- When all countries have been viewed, the pool resets

---

#### Submit Answer

```http
POST /api/game/answer/
```

**Authentication:** Required

**Request Body:**
```json
{
  "answer": "United States"
}
```

**Response:** `200 OK` (Correct)
```json
{
  "correct": true,
  "country_name": "United States",
  "score": 10,
  "total_score": 50,
  "message": "Correct!"
}
```

**Response:** `200 OK` (Incorrect)
```json
{
  "correct": false,
  "country_name": "United States",
  "your_answer": "United Kingdom",
  "score": 0,
  "total_score": 40,
  "message": "Incorrect. The correct answer was United States"
}
```

**Answer Validation:**
- Case-insensitive matching
- Accent/diacritic normalization (e.g., "Côte d'Ivoire" matches "Cote d'Ivoire")
- Special character removal
- Common name variations supported

**Errors:**
- `400 Bad Request` - No answer provided or no active game
- `404 Not Found` - No current question available

---

#### Skip Question

```http
POST /api/game/skip/
```

**Authentication:** Required

**Description:** Skips the current question. Players have 3 skips per game.

**Response:** `200 OK`
```json
{
  "message": "Question skipped",
  "country_name": "United States",
  "skips_remaining": 2,
  "total_score": 40
}
```

**Errors:**
- `400 Bad Request` - No skips remaining or no active game
- `404 Not Found` - No current question to skip

---

#### Finish Game

```http
POST /api/game/finish/
```

**Authentication:** Required

**Description:** Ends the current game session and triggers background statistics calculation.

**Response:** `200 OK`
```json
{
  "message": "Game finished successfully",
  "final_score": 85,
  "duration": "00:12:34",
  "correct_answers": 10,
  "wrong_answers": 3,
  "skips_used": 1,
  "session_id": 1
}
```

**Background Tasks:**
- Leaderboard update (async)
- User statistics recalculation (async)

**Errors:**
- `404 Not Found` - No active game session

---

#### Get Game History

```http
GET /api/game/history/
```

**Authentication:** Required

**Query Parameters:**
- `limit` (optional) - Number of games to return (default: 20)

**Response:** `200 OK`
```json
[
  {
    "id": 5,
    "started_at": "2024-01-15T10:30:00Z",
    "finished_at": "2024-01-15T10:45:00Z",
    "score": 100,
    "correct_answers": 12,
    "wrong_answers": 2,
    "skips_used": 1,
    "duration": "00:15:00"
  }
]
```

---

#### Get Random Country (Testing)

```http
GET /api/game/random-country/
```

**Authentication:** Required

**Description:** Returns a random country with flag. Useful for testing.

**Response:** `200 OK`
```json
{
  "id": 42,
  "name": "Japan",
  "code": "JP",
  "flag_url": "http://flagwars.mecebeci.com/flags/jp.png"
}
```

---

### Leaderboard Endpoints

#### Get Global Leaderboard

```http
GET /api/leaderboard/
```

**Authentication:** Optional (public endpoint)

**Query Parameters:**
- `limit` (optional) - Number of players to return (default: 100)

**Response:** `200 OK`
```json
[
  {
    "rank": 1,
    "username": "flagmaster",
    "total_score": 5420,
    "games_played": 42,
    "average_score": 129.0,
    "best_score": 250
  },
  {
    "rank": 2,
    "username": "geowizard",
    "total_score": 4890,
    "games_played": 38,
    "average_score": 128.7,
    "best_score": 245
  }
]
```

**Caching:**
- Leaderboard data is cached for 5 minutes
- Cache is invalidated when new high scores are achieved

---

## Error Responses

All endpoints may return these standard error responses:

### 400 Bad Request
```json
{
  "error": "Detailed error message",
  "field_errors": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "An unexpected error occurred"
}
```

---

## Rate Limiting

Currently, there are no rate limits enforced. This may change in future versions.

---

## Webhooks

No webhooks are currently available.

---

## Pagination

List endpoints that return multiple items support pagination:

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

**Response:**
```json
{
  "count": 150,
  "next": "http://api.example.com/resource/?page=3",
  "previous": "http://api.example.com/resource/?page=1",
  "results": []
}
```

---

## CORS

The API supports CORS for the following origins:
- `http://localhost:5173` (development)
- `https://flagwars.mecebeci.com` (production)

Credentials (cookies, authorization headers) are allowed.

---

## Versioning

The current API version is `v1`. No versioning prefix is used in URLs yet. Future versions may introduce `/api/v2/` paths.

---

## Testing with cURL

### Register and Login
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"securepass123","password2":"securepass123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"securepass123"}'
```

### Start Game
```bash
export TOKEN="your_access_token_here"

curl -X POST http://localhost:8000/api/game/start/ \
  -H "Authorization: Bearer $TOKEN"
```

### Get Question
```bash
curl -X GET http://localhost:8000/api/game/question/ \
  -H "Authorization: Bearer $TOKEN"
```

### Submit Answer
```bash
curl -X POST http://localhost:8000/api/game/answer/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"answer":"United States"}'
```

---

## Change Log

### Version 1.0.0 (Current)
- Initial API release
- JWT authentication
- Game session management
- Leaderboard system
- User statistics
- Redis caching integration

---

## Support

For API issues or questions:
- GitHub Issues: https://github.com/yourusername/flagwars/issues
- Email: support@mecebeci.com
