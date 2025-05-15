import { useUser } from "@clerk/clerk-react";
import { Navigate } from "react-router-dom";

interface RequireAuthProps {
  children: React.ReactNode;
}

export const RequireAuth = ({ children }: RequireAuthProps) => {
  const { user, isLoaded } = useUser();

  if (!isLoaded) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-2 border-t-primary border-r-transparent border-b-primary border-l-transparent"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};
