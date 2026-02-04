# Portfolio Frontend

Next.js frontend for the portfolio website with blog functionality.

## Features

- Modern, responsive design with parallax effects
- Blog reader with comments and likes
- Admin dashboard for content management
- Rich text editor for blog posts
- JWT authentication

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```
NEXT_PUBLIC_API_URL=http://localhost:3001
```

3. Run development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:3001)

## Deployment

Deploy to Vercel:

```bash
vercel
```

Or connect your GitHub repository to Vercel for automatic deployments.

## Project Structure

- `app/` - Next.js app router pages
- `components/` - React components
- `lib/` - Utility functions and API client
- `styles/` - Global styles
