import { createRoot } from "react-dom/client";
import { useEffect } from "react";
import { Layout } from "./components/Layout";
import { useHashRoute } from "./hooks/useHashRoute";
import { AdminPage } from "./pages/AdminPage";
import { ChatPage } from "./pages/ChatPage";
import { ContactPage } from "./pages/ContactPage";
import { CoursesPage } from "./pages/CoursesPage";
import { FaqPage } from "./pages/FaqPage";
import { ProcessPage } from "./pages/ProcessPage";
import { trackVisit } from "./services/api";
import "./styles.css";

function App() {
  const route = useHashRoute();
  useEffect(() => {
    trackVisit(route).catch(() => {});
  }, [route]);
  const pages = {
    chat: <ChatPage />,
    courses: <CoursesPage />,
    faq: <FaqPage />,
    process: <ProcessPage />,
    contact: <ContactPage />,
    admin: <AdminPage />,
  };
  return <Layout route={route}>{pages[route] || pages.chat}</Layout>;
}

createRoot(document.getElementById("root")).render(<App />);
