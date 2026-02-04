# Quick Start Guide

Get your portfolio website up and running in minutes!

## Prerequisites Checklist

- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] AWS CLI installed and configured
- [ ] AWS SAM CLI installed (`pip install aws-sam-cli`)
- [ ] Upstash Redis account (free tier available)
- [ ] Cloudinary account (free tier available)
- [ ] Vercel account (free tier available)

## Quick Setup (5 Steps)

### 1. Backend Setup (5 minutes)

```bash
cd backend

# Install dependencies
pip install -r src/requirements.txt

# Configure SAM (edit samconfig.toml with your values)
cp samconfig.toml.example samconfig.toml
# Edit samconfig.toml with your Redis URL, Cloudinary URL, and JWT secret

# Build and deploy
sam build
sam deploy --guided

# Create admin user
export USERS_TABLE=UsersTable
python scripts/create_admin_user.py
```

### 2. Frontend Setup (3 minutes)

```bash
cd frontend

# Install dependencies
npm install

# Configure API URL
echo "NEXT_PUBLIC_API_URL=https://your-api-url.execute-api.region.amazonaws.com/prod" > .env.local
# Replace with your actual API Gateway URL from Step 1

# Run locally
npm run dev
```

### 3. Test Locally

1. Open http://localhost:3000
2. Go to http://localhost:3000/admin/login
3. Login with your admin credentials
4. Create a blog post
5. Update your profile

### 4. Deploy Frontend to Vercel

```bash
cd frontend
vercel
# Follow prompts, add NEXT_PUBLIC_API_URL environment variable
```

### 5. You're Done! 🎉

Visit your Vercel URL and start managing your portfolio!

## Common Issues

### "Module not found" errors
- Run `npm install` in frontend directory
- Run `pip install -r requirements.txt` in backend directory

### "Table not found" errors
- Make sure DynamoDB tables are created (they're created automatically by SAM)
- Check AWS credentials are configured: `aws configure`

### "CORS error" in browser
- Verify API Gateway URL is correct
- Check that CORS is enabled in `template.yaml`

### Can't login
- Make sure admin user was created successfully
- Check password is correct
- Verify JWT_SECRET is set in SAM config

## Next Steps

- Customize the design in `frontend/app/globals.css`
- Add your projects and experience via admin panel
- Write your first blog post!
- Set up a custom domain in Vercel

## Need Help?

- Check `DEPLOYMENT.md` for detailed deployment instructions
- Review `README.md` for architecture overview
- Check AWS CloudWatch logs for backend errors
- Check Vercel logs for frontend errors
