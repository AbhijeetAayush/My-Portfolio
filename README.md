# Portfolio Website with Blog

A full-stack portfolio website with blog functionality, built with Next.js frontend and AWS Lambda backend.

## Features

- **Portfolio Pages**: Home, About, Projects, Experience with parallax effects
- **Blog System**: Full-featured blog with likes
- **Admin Dashboard**: Complete CMS for managing portfolio content and blog posts
- **Modern UI**: Beautiful, responsive design with animations
- **Serverless Backend**: AWS Lambda, DynamoDB, Redis caching
- **Authentication**: JWT-based admin authentication

## Tech Stack

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Framer Motion (animations)
- React Quill (rich text editor)

### Backend
- AWS SAM (Serverless Application Model)
- AWS Lambda (Python)
- DynamoDB
- Upstash Redis (caching)
- Cloudinary (media storage)

## Project Structure

```
.
├── frontend/          # Next.js application
│   ├── app/          # Pages and routes
│   ├── components/   # React components
│   └── lib/          # Utilities and API client
│
└── backend/          # AWS SAM project
    ├── src/
    │   ├── handlers/ # Lambda function handlers
    │   ├── db/       # Database clients
    │   └── utils/    # Utility functions
    └── template.yaml # SAM infrastructure template
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- AWS CLI configured
- AWS SAM CLI installed
- Upstash Redis account
- Cloudinary account

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r src/requirements.txt
```

3. Create admin user (run once):
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

4. Deploy backend:
```bash
sam build
sam deploy --guided
```

5. Set environment variables in AWS Systems Manager Parameter Store or samconfig.toml:
   - `JWT_SECRET`: Secret key for JWT tokens
   - `REDIS_URL`: Upstash Redis connection URL
   - `CLOUDINARY_URL`: Cloudinary API URL

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local`:
```
NEXT_PUBLIC_API_URL=https://your-api-gateway-url.execute-api.region.amazonaws.com/prod
```

4. Run development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000)

## Deployment

### Backend (AWS)

```bash
cd backend
sam build
sam deploy
```

### Frontend (Vercel)

1. Push code to GitHub
2. Import project in Vercel
3. Set environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy

## Usage

1. Access admin dashboard at `/admin/login`
2. Login with your credentials
3. Edit profile, projects, and experience from the admin panel
4. Create and manage blog posts
5. View your portfolio at the public pages

## API Endpoints

### Public
- `GET /portfolio` - Get portfolio data
- `GET /blogs` - Get all blogs
- `GET /blogs/{id}` - Get single blog
- `GET /blogs/{id}/likes` - Get likes
- `POST /blogs/{id}/likes` - Add like

### Admin (JWT Required)
- `POST /auth/login` - Login
- `PUT /portfolio` - Update portfolio
- `POST /blogs` - Create blog
- `PUT /blogs/{id}` - Update blog
- `DELETE /blogs/{id}` - Delete blog

## License

MIT
