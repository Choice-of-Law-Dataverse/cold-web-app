<!-- eslint-disable vue/no-v-html -->
<template>
  <UModal
    :model-value="modelValue"
    :ui="{ rounded: 'rounded-none' }"
    @update:model-value="(v) => emit('update:modelValue', v)"
  >
    <div class="p-6">
      <h2 class="mb-4">Cite This Page</h2>
      <!-- eslint-disable-next-line vue/no-v-html -->
      <p
        class="result-value-small-citation break-words leading-relaxed"
        v-html="citationTextDisplay"
      />
      <div class="mt-2">
        <NuxtLink
          :to="route.fullPath"
          class="link-button !mb-2 no-underline"
          :aria-disabled="copying ? 'true' : 'false'"
          @click.prevent="!copying && copyToClipboard()"
        >
          {{ copied ? "Copied" : "Copy to Clipboard" }}
          <UIcon
            :name="
              copied
                ? 'i-material-symbols:check-circle-outline'
                : 'i-material-symbols:content-copy-outline'
            "
            class="relative top-[1px] inline-block"
          />
        </NuxtLink>
      </div>
    </div>
  </UModal>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { useRoute } from "vue-router";

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: "" },
});
const emit = defineEmits(["update:modelValue"]);

const route = useRoute();

const pageTitle = ref("");
const currentURL = ref("");
let titleObserver;
const copied = ref(false);
const copying = ref(false);

onMounted(() => {
  pageTitle.value = typeof document !== "undefined" ? document.title || "" : "";
  currentURL.value = typeof window !== "undefined" ? window.location.href : "";

  if (
    typeof window !== "undefined" &&
    typeof MutationObserver !== "undefined"
  ) {
    const titleEl = document.querySelector("title");
    if (titleEl) {
      titleObserver = new MutationObserver(() => {
        pageTitle.value = document.title || "";
      });
      titleObserver.observe(titleEl, {
        subtree: true,
        characterData: true,
        childList: true,
      });
    }
  }
});

onBeforeUnmount(() => {
  if (titleObserver) {
    titleObserver.disconnect();
    titleObserver = undefined;
  }
});

function slugToPageType(slug) {
  switch (slug) {
    case "jurisdiction":
      return "Country Report";
    case "court-decision":
      return "Court Decision";
    case "domestic-instrument":
      return "Domestic Instrument";
    case "regional-instrument":
      return "Regional Instrument";
    case "international-instrument":
      return "International Instrument";
    case "arbitral-rule":
      return "Arbitral Rule";
    case "arbitral-award":
      return "Arbitral Award";
    case "literature":
      return "Literature";
    case "question":
      return "Question";
    default: {
      if (!slug) return "Page";
      return slug
        .split("-")
        .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
        .join(" ");
    }
  }
}

const pageType = computed(() => {
  const segments = route.path.split("/").filter(Boolean);
  return slugToPageType(segments[0] || "");
});

const accessDate = computed(() => {
  const d = new Date();
  const day = d.getDate();
  const month = d.toLocaleString("en-US", { month: "long" });
  const year = d.getFullYear();
  return `${day} ${month} ${year}`;
});

const getTitle = (rawTitle, pageType) => {
  const tokens = rawTitle
    .split("—")
    .map((s) => s.trim())
    .filter((t) => t !== pageType);

  let title = "";
  switch (pageType) {
    case "Question":
      title = `'${tokens[1]}'  — ${tokens[0]}`;
      break;
    case "Literature":
      title = `'${tokens[0]}'`;
      break;
    default:
      title = tokens[0];
  }
  return `${title} — ${pageType}`;
};

const citationTextDisplay = computed(() => {
  const rawTitle = (props.title && props.title.trim()) || pageTitle.value || "";
  const title = getTitle(rawTitle, pageType.value);
  const url = currentURL.value;
  return `${title}, <em>Choice of Law Dataverse</em>, &lt;${url}&gt; accessed ${accessDate.value}.`;
});

const citationText = computed(() => {
  const rawTitle = (props.title && props.title.trim()) || pageTitle.value || "";
  const title = getTitle(rawTitle, pageType.value);
  const url = currentURL.value;
  return `${title}, Choice of Law Dataverse, <${url}> accessed ${accessDate.value}.`;
});

async function copyToClipboard() {
  if (copying.value) return;
  copying.value = true;
  const htmlText = citationTextDisplay.value;
  const plainText = citationText.value;

  try {
    if (navigator?.clipboard?.write) {
      const clipboardItem = new ClipboardItem({
        "text/html": new Blob([htmlText], { type: "text/html" }),
        "text/plain": new Blob([plainText], { type: "text/plain" }),
      });
      await navigator.clipboard.write([clipboardItem]);
    } else if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(plainText);
    } else {
      const ta = document.createElement("textarea");
      ta.value = plainText;
      ta.setAttribute("readonly", "");
      ta.style.position = "absolute";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
    }
    copied.value = true;
    setTimeout(() => (copied.value = false), 1500);
  } catch {
    // Silent fail
  } finally {
    copying.value = false;
  }
}
</script>
