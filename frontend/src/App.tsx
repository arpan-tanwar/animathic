import { ClerkProvider } from "@clerk/clerk-react";
import { Outlet, BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as SonnerToaster } from "sonner";
import { ThemeProvider } from "@/components/ThemeProvider";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { RequireAuth } from "@/components/RequireAuth";
import { Toaster } from "react-hot-toast";

// Import pages
import LandingPage from "@/pages/LandingPage";
import HowItWorksPage from "@/pages/HowItWorksPage";
import GeneratePage from "@/pages/GeneratePage";
import DashboardPage from "@/pages/DashboardPage";
import NotFoundPage from "@/pages/NotFoundPage";
import ExamplesPage from "@/pages/ExamplesPage";
import ChatPage from "@/pages/ChatPage";

// Get publishable key from environment variables
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
const CLERK_DOMAIN = import.meta.env.VITE_CLERK_DOMAIN;

if (!PUBLISHABLE_KEY) {
  throw new Error("Missing VITE_CLERK_PUBLISHABLE_KEY environment variable");
}

const ClerkWithRoutes = () => {
  return (
    <ClerkProvider
      publishableKey={PUBLISHABLE_KEY}
      {...(CLERK_DOMAIN && { domain: CLERK_DOMAIN })}
    >
      <ThemeProvider defaultTheme="dark">
        <Routes>
          {/* Marketing/site routes using the global layout */}
          <Route element={<Layout />}>
            <Route path="/" element={<LandingPage />} />
            <Route path="/how-it-works" element={<HowItWorksPage />} />
            <Route path="/examples" element={<ExamplesPage />} />
            <Route
              path="/generate"
              element={
                <RequireAuth>
                  <GeneratePage />
                </RequireAuth>
              }
            />
            <Route
              path="/dashboard"
              element={
                <RequireAuth>
                  <DashboardPage />
                </RequireAuth>
              }
            />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
          {/* Chat canvas as separate route if needed */}
          <Route path="/chat" element={<ChatPage />} />
        </Routes>
        <SonnerToaster position="bottom-right" />
      </ThemeProvider>
    </ClerkProvider>
  );
};

const Layout = () => {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      <div className="mt-auto">
        <Footer />
      </div>
    </div>
  );
};

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <ClerkWithRoutes />
    </BrowserRouter>
  );
}
