import { defineEventHandler, setResponseHeader } from "h3";

export default defineEventHandler(async (event) => {
  setResponseHeader(event, "Cache-Control", "no-store, private");
  const auth0Client = useAuth0(event);
  return await auth0Client.getUser();
});
