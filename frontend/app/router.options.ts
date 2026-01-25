export default {
  scrollBehavior(to: URL) {
    if (to.hash) {
      return {
        el: to.hash,
        behavior: "smooth",
        // Offset to account for sticky header height
        top: getNavOffset(),
      };
    }
    return { top: 0 };
  },
};

/**
 * Get the appropriate nav offset based on current scroll position.
 * Uses scrolled nav height since hash navigation typically happens after page load.
 */
function getNavOffset(): number {
  // Use CSS variable values: mobile 3.5rem (56px), desktop 4rem (64px)
  // Add 16px extra padding for visual breathing room
  const isMobile = typeof window !== "undefined" && window.innerWidth < 640;
  return isMobile ? 56 + 16 : 64 + 16;
}
