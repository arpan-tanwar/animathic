# Animathic - AI-Powered Mathematical Animation Generator

Transform your mathematical concepts into stunning visualizations using natural language. Animathic leverages the power of AI to create beautiful mathematical animations through simple text descriptions.

[Animathic Demo](https://animathic.vercel.app/)

## ✨ Features

- 🎨 **Natural Language to Animation**: Describe your mathematical concept in plain English
- 🤖 **AI-Powered Generation**: Powered by advanced language models for accurate mathematical interpretation
- 🎥 **High-Quality Animations**: Professional-grade animations using Manim
- 💾 **Easy Download**: Download your animations in MP4 format
- 📱 **Modern UI**: Beautiful, responsive interface built with React and Tailwind CSS
- 🔒 **Secure Authentication**: User authentication and secure video storage
- 📊 **Dashboard**: Manage and organize your animations

## 🛠️ Tech Stack

### Frontend

- React 18 with TypeScript
- Vite for fast development and building
- Tailwind CSS for styling
- shadcn/ui for beautiful components
- Clerk for authentication
- Axios for API communication

### Backend

- FastAPI (Python)
- Manim Community Edition for animation generation
- OpenAI API for natural language processing
- SQLite for data storage
- Docker for containerization

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- Docker (optional)
- OpenAI API key
- Clerk API keys

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/animathic.git
   cd animathic
   ```

2. **Set up the frontend**

   ```bash
   cd frontend
   npm install
   ```

3. **Set up the backend**

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create `.env` files in both frontend and backend directories:

   Frontend (.env):

   ```
   VITE_CLERK_PUBLISHABLE_KEY=your_clerk_key
   VITE_API_BASE_URL=http://localhost:8000
   ```

   Backend (.env):

   ```
   OPENAI_API_KEY=your_openai_key
   ```

5. **Start the development servers**

   Frontend:

   ```bash
   cd frontend
   npm run dev
   ```

   Backend:

   ```bash
   cd backend
   uvicorn main:app --reload
   ```

## 📝 Usage

1. **Sign Up/Login**: Create an account or log in to your existing account
2. **Create Animation**:
   - Go to the dashboard
   - Enter your mathematical concept in natural language
   - Click "Generate"
3. **View & Download**:
   - Watch the animation preview
   - Download in MP4 format
   - Access from your dashboard anytime

## 🏗️ Project Structure

```
animathic/
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom React hooks
│   │   └── lib/           # Utility functions
│   └── public/            # Static assets
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core functionality
│   │   └── services/     # Business logic
│   └── media/            # Generated animations
└── docker/               # Docker configuration
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Manim Community](https://www.manim.community/) for the animation engine
- [OpenAI](https://openai.com/) for the language model
- [Clerk](https://clerk.dev/) for authentication
- [shadcn/ui](https://ui.shadcn.com/) for the UI components

## 📞 Support

For support, please:

- Open an issue in the GitHub repository
