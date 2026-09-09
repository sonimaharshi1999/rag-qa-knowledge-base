# API Testing Runbook

## Purpose
This runbook provides step-by-step procedures for testing the REST API endpoints of the e-commerce platform. It is intended for QA engineers running manual or automated API test suites.

## Prerequisites
- Postman or curl installed
- Access to staging environment API (https://api-staging.example.com)
- Valid API key (obtain from QA lead)
- VPN connected to internal network

## API Authentication
All endpoints require Bearer token authentication. Obtain a token by calling:

```
POST /api/v1/auth/login
Body: {"email": "qa-user@example.com", "password": "test123"}
Response: {"token": "eyJhbGci...", "expires_in": 3600}
```

Include the token in all subsequent requests:
```
Authorization: Bearer <token>
```

## Endpoint Testing Procedures

### 1. User Management API

#### GET /api/v1/users
- **Purpose**: List all users with pagination
- **Test Steps**:
  1. Send GET request with page=1&limit=10
  2. Verify response status is 200
  3. Verify response contains "users" array and "total" count
  4. Verify pagination metadata is correct
- **Expected Response**: JSON with user list, status 200

#### POST /api/v1/users
- **Purpose**: Create a new user
- **Test Steps**:
  1. Send POST with valid user payload (name, email, role)
  2. Verify response status is 201
  3. Verify returned user has an auto-generated ID
  4. Verify duplicate email returns 409 Conflict
- **Validation**: Check database directly to confirm record creation

### 2. Product Catalog API

#### GET /api/v1/products
- **Purpose**: Search and filter products
- **Test Steps**:
  1. Test search by keyword: ?q=laptop
  2. Test filter by category: ?category=electronics
  3. Test price range: ?min_price=100&max_price=500
  4. Test sorting: ?sort=price&order=asc
- **Performance**: Response time should be under 500ms for 10,000 products

#### PUT /api/v1/products/{id}
- **Purpose**: Update product details
- **Test Steps**:
  1. Update product name and verify change persists
  2. Update price to zero - expect 400 Bad Request
  3. Update non-existent product - expect 404 Not Found

### 3. Order Management API

#### POST /api/v1/orders
- **Purpose**: Place a new order
- **Test Steps**:
  1. Create order with valid items and shipping address
  2. Verify order ID is generated
  3. Verify inventory is decremented
  4. Verify order confirmation email is triggered
- **Edge Cases**: Empty cart, out-of-stock items, invalid coupon codes

#### GET /api/v1/orders/{id}/status
- **Purpose**: Track order status
- **Expected Statuses**: pending, confirmed, shipped, delivered, cancelled

## Error Handling Verification
- 400: Malformed request body
- 401: Missing or invalid token
- 403: Insufficient permissions
- 404: Resource not found
- 429: Rate limit exceeded (max 100 requests/minute)
- 500: Internal server error (check server logs)

## Rate Limiting Tests
Send 101 requests within 60 seconds to verify rate limiter:
- Requests 1-100: Should succeed (200)
- Request 101: Should return 429 with Retry-After header

## Reporting
After completing the test run:
1. Export results from Postman as JSON
2. Log any failures in Jira under project QA-API
3. Notify the dev team on Slack #api-testing channel
4. Update the test execution tracker spreadsheet
