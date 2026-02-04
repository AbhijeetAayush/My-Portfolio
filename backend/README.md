# Portfolio Website Backend

AWS SAM-based backend for portfolio website with blog functionality.

## Prerequisites

- AWS CLI configured
- AWS SAM CLI installed
- Python 3.11
- Upstash Redis account
- Cloudinary account

## Setup

1. Install dependencies:
```bash
pip install -r src/requirements.txt
```

2. Create admin user (run this script once):
```python
import bcrypt
from db.dynamodb import DynamoDBClient

db = DynamoDBClient()
email = "your-email@example.com"
password = "your-secure-password"

password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

db.users_table.put_item(
    Item={
        'email': email,
        'password_hash': password_hash,
        'created_at': int(__import__('time').time())
    }
)
```

3. Set environment variables in `samconfig.toml` or via AWS Systems Manager Parameter Store:
   - `JWT_SECRET`: Secret key for JWT tokens
   - `REDIS_URL`: Upstash Redis connection URL
   - `CLOUDINARY_URL`: Cloudinary API URL

## Deployment

```bash
sam build
sam deploy --guided
```

## API Endpoints

### Public Endpoints
- `GET /portfolio` - Get portfolio data
- `GET /blogs` - Get all blogs (paginated)
- `GET /blogs/{id}` - Get single blog by ID or slug
- `GET /blogs/{id}/comments` - Get comments for a blog
- `POST /blogs/{id}/comments` - Create a comment
- `GET /blogs/{id}/likes` - Get likes count
- `POST /blogs/{id}/likes` - Add a like

### Admin Endpoints (Require JWT)
- `POST /auth/login` - Login and get JWT tokens
- `PUT /portfolio` - Update portfolio data
- `POST /blogs` - Create a blog post
- `PUT /blogs/{id}` - Update a blog post
- `DELETE /blogs/{id}` - Delete a blog post
- `DELETE /comments/{id}` - Delete a comment

## Testing

Use the `events/` directory for test events:

```bash
sam local invoke PortfolioFunction --event events/get-portfolio.json
```
