
import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <main className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] px-4">
      <div className="text-center space-y-6">
        <h1 className="text-5xl sm:text-6xl md:text-7xl font-bold">404</h1>
        <h2 className="text-2xl font-medium">Page not found</h2>
        <p className="text-muted-foreground max-w-md mx-auto">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="pt-6">
          <Link
            to="/"
            className="inline-flex items-center justify-center px-5 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
          >
            Return Home
          </Link>
        </div>
      </div>
    </main>
  );
}
