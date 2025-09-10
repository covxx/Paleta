# ProduceFlow React Frontend

Modern React frontend for the ProduceFlow Label Printer System.

## Features

- 🎨 **Modern UI**: Material-UI components with custom theme
- 🔐 **Authentication**: Secure login/logout with session management
- 📊 **Dashboard**: Real-time statistics and system status
- 👥 **User Management**: Full CRUD operations for admin users
- 📱 **Responsive**: Mobile-friendly design
- ⚡ **Real-time**: Live updates with React Query
- 🎯 **Type Safety**: Form validation with react-hook-form

## Tech Stack

- **React 18** - Modern React with hooks
- **Material-UI 5** - Component library
- **React Router 6** - Client-side routing
- **React Query** - Data fetching and caching
- **Axios** - HTTP client
- **React Hook Form** - Form handling
- **React Hot Toast** - Notifications

## Setup Instructions

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Running Flask backend on port 5002

### Installation

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm start
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

### Development

The React app runs on `http://localhost:3000` and proxies API requests to the Flask backend at `http://localhost:5002`.

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   └── Layout.js
│   ├── pages/
│   │   ├── Dashboard.js
│   │   ├── LoginPage.js
│   │   ├── UserManagement.js
│   │   └── ...
│   ├── hooks/
│   │   └── useAuth.js
│   ├── App.js
│   └── index.js
├── package.json
└── README.md
```

## API Integration

The frontend communicates with the Flask backend through REST APIs:

- `GET /api/auth/status` - Check authentication status
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/admin-users` - Get admin users
- `POST /api/admin-users` - Create admin user
- `PUT /api/admin-users/:id` - Update admin user
- `DELETE /api/admin-users/:id` - Delete admin user

## Deployment

1. **Build the React app:**
   ```bash
   npm run build
   ```

2. **Copy build files to Flask static directory:**
   ```bash
   cp -r build/* ../static/react/
   ```

3. **Update Flask to serve React app:**
   Add route in Flask to serve `index.html` for all React routes.

## Features Implemented

- ✅ Modern login page with validation
- ✅ Responsive admin dashboard
- ✅ User management with CRUD operations
- ✅ Real-time data updates
- ✅ Material-UI theme and components
- ✅ Form validation and error handling
- ✅ Toast notifications
- ✅ Authentication state management

## Next Steps

- [ ] Implement remaining management pages
- [ ] Add real-time WebSocket connections
- [ ] Implement advanced analytics
- [ ] Add data export functionality
- [ ] Implement bulk operations
- [ ] Add search and filtering
- [ ] Implement role-based permissions
