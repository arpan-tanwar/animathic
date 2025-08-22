# Animathic Frontend

The frontend application for Animathic, built with React, TypeScript, and modern web technologies.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🛠️ Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**:
  - Tailwind CSS
  - shadcn/ui components
- **Authentication**: Clerk
- **State Management**: React Hooks
- **API Communication**: Axios
- **Routing**: React Router
- **Code Quality**:
  - ESLint
  - Prettier
  - TypeScript

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # shadcn/ui components
│   └── ...             # Custom components
├── pages/              # Page components
├── hooks/              # Custom React hooks
├── lib/                # Utility functions
└── types/              # TypeScript type definitions
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
VITE_CLERK_PUBLISHABLE_KEY=your_clerk_key
VITE_API_BASE_URL=http://localhost:8000
```

### Development

1. **Install Dependencies**

   ```bash
   npm install
   ```

2. **Start Development Server**

   ```bash
   npm run dev
   ```

3. **Build for Production**
   ```bash
   npm run build
   ```

## 🎨 UI Components

We use [shadcn/ui](https://ui.shadcn.com/) for our component library. Key components include:

- Button
- Card
- Dialog
- Input
- Toast
- And more...

## 🔒 Authentication

Authentication is handled by [Clerk](https://clerk.dev/). Features include:

- User registration
- Login/Logout
- Protected routes
- User profile management

## 📱 Responsive Design

The application is fully responsive and works on:

- Desktop
- Tablet
- Mobile devices

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage
```

## 📦 Building for Production

1. **Build the application**

   ```bash
   npm run build
   ```

2. **Preview the build**
   ```bash
   npm run preview
   ```

## 🐳 Docker Support

Build and run with Docker:

```bash
# Build the image
docker build -t animathic-frontend .

# Run the container
docker run -p 5173:5173 animathic-frontend
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.
# Force deployment - Tue Aug 19 00:14:55 EDT 2025
