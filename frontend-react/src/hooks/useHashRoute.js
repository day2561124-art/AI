import { useEffect, useState } from "react";

export function useHashRoute() {
  const [route, setRoute] = useState(() => location.hash.replace("#/", "") || "chat");
  useEffect(() => {
    const onHashChange = () => setRoute(location.hash.replace("#/", "") || "chat");
    addEventListener("hashchange", onHashChange);
    return () => removeEventListener("hashchange", onHashChange);
  }, []);
  return route;
}

