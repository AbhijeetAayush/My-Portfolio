# Deployment Guide

This guide walks you through deploying the portfolio website backend to AWS and frontend to Vercel.

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI installed and configured
3. AWS SAM CLI installed
4. Upstash Redis account
5. Cloudinary account
6. Vercel account (for frontend)

## Backend Deployment (AWS)

### Step 1: Set Up Upstash Redis

1. Go to [Upstash Console](https://console.upstash.com/)
2. Create a new Redis database
3. Copy the Redis URL (format: `redis://default:password@host:port`)

### Step 2: Set Up Cloudinary

1. Go to [Cloudinary Console](https://cloudinary.com/console)
2. Get your Cloudinary URL (format: `cloudinary://api_key:api_secret@cloud_name`)

### Step 3: Configure AWS SAM

1. Copy `samconfig.toml.example` to `samconfig.toml`:
```bash
cd backend
cp samconfig.toml.example samconfig.toml
```

2. Edit `samconfig.toml` and update:
   - `stack_name`: Your stack name
   - `region`: Your AWS region
   - `parameter_overrides`: Add your actual values:
     - `JWTSecret`: Generate a secure random string
     - `RedisUrl`: Your Upstash Redis URL
     - `CloudinaryUrl`: Your Cloudinary URL

### Step 4: Build and Deploy

```bash
cd backend
sam build
sam deploy
```

### Step 5: Create Admin User

After deployment, create your admin user:

```bash
# Set the table name
export USERS_TABLE=UsersTable

# Run the script
python scripts/create_admin_user.py
```

Or manually using AWS CLI:
```bash
aws dynamodb put-item \
  --table-name UsersTable \
  --item '{
    "email": {"S": "your-email@example.com"},
    "password_hash": {"S": "<bcrypt-hashed-password>"},
    "created_at": {"N": "<timestamp>"}
  }'
```

### Step 6: Get API Gateway URL

After deployment, SAM will output the API Gateway URL. Copy it for the frontend configuration.

```bash
aws cloudformation describe-stacks \
  --stack-name portfolio-backend \
  --query 'Stacks[0].Outputs[?OutputKey==`PortfolioApiUrl`].OutputValue' \
  --output text
```

## Frontend Deployment (Vercel)

### Step 1: Prepare Environment Variables

Create `.env.local` in the frontend directory:
```
NEXT_PUBLIC_API_URL=https://your-api-id.execute-api.region.amazonaws.com/prod
```

### Step 2: Deploy to Vercel

#### Option A: Using Vercel CLI

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
cd frontend
vercel
```

3. Follow the prompts and add the environment variable when asked.

#### Option B: Using GitHub Integration

1. Push your code to GitHub
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "New Project"
4. Import your GitHub repository
5. Set root directory to `frontend`
6. Add environment variable:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: Your API Gateway URL
7. Deploy

### Step 3: Configure Custom Domain (Optional)

1. In Vercel dashboard, go to your project settings
2. Navigate to "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

## Post-Deployment

### 1. Test API Endpoints

Test your API is working:
```bash
curl https://your-api-url.execute-api.region.amazonaws.com/prod/portfolio
```

### 2. Test Frontend

1. Visit your Vercel deployment URL
2. Navigate to `/admin/login`
3. Login with your admin credentials
4. Test creating a blog post
5. Test updating your profile

### 3. Set Up Monitoring

- Enable CloudWatch logs for Lambda functions
- Set up Vercel analytics
- Configure error tracking (Sentry, etc.)

## Troubleshooting

### Backend Issues

**Lambda function errors:**
- Check CloudWatch logs
- Verify environment variables are set correctly
- Ensure DynamoDB tables exist

**CORS errors:**
- Verify API Gateway CORS configuration in `template.yaml`
- Check that frontend URL is allowed

**Authentication errors:**
- Verify JWT_SECRET is set correctly
- Check token expiration settings
- Verify user exists in DynamoDB

### Frontend Issues

**API connection errors:**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS configuration on backend
- Verify API Gateway is deployed and accessible

**Build errors:**
- Check Node.js version (should be 18+)
- Verify all dependencies are installed
- Check for TypeScript errors

## Cost Optimization

### AWS Costs

- DynamoDB: Use on-demand billing for low traffic
- Lambda: Free tier includes 1M requests/month
- API Gateway: Free tier includes 1M requests/month
- Upstash Redis: Free tier available

### Vercel Costs

- Free tier includes:
  - 100GB bandwidth/month
  - Unlimited deployments
  - Custom domains

## Security Checklist

- [ ] JWT_SECRET is strong and unique
- [ ] Redis URL uses SSL
- [ ] API Gateway has proper CORS configuration
- [ ] Admin password is strong
- [ ] Environment variables are not committed to git
- [ ] HTTPS is enabled on custom domain
- [ ] CloudWatch logs are monitored

## Scaling Considerations

- **High Traffic**: Consider CloudFront CDN for frontend
- **Database**: DynamoDB auto-scales, but monitor costs
- **Caching**: Redis caching reduces Lambda invocations
- **CDN**: Use Cloudinary CDN for images
