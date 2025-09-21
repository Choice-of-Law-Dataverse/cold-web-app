export default defineAppConfig({
  ui: {
    card: {
      rounded: "rounded-none", // Remove border radius
      shadow: "shadow-none", // Remove box shadow
      ring: "ring-1 ring-[var(--color-cold-gray)]", // Add border with custom color
      divide: "divide-y divide-[var(--color-cold-gray)]", // Override divider color
    },
    primary: "cool",
    gray: "cool",
  },
});
