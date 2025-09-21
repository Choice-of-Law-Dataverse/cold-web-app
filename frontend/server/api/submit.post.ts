export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const { token, email } = body;

  const result = await verifyTurnstileToken(token);

  if (!result.success) {
    return { success: false, message: "Spam protection failed" };
  }

  return { success: true };
});
