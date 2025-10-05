import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import Footer from "@/components/Footer";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background scanlines crt-screen p-4">
      <div className="w-full max-w-2xl">
        <div className="terminal-panel text-center">
          <h1 className="mb-4 text-6xl font-bold text-error terminal-flicker">404</h1>
          <p className="mb-2 text-xl uppercase text-terminal-glow">ERROR: ROUTE_NOT_FOUND</p>
          <p className="mb-6 text-sm text-muted-foreground">
            &gt;&gt; PATH: {location.pathname}
          </p>
          <a href="/" className="terminal-button-accent inline-block">
            &gt; [RETURN_TO_HOME]
          </a>
        </div>
        
        <Footer />
      </div>
    </div>
  );
};

export default NotFound;
