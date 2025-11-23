<template>
  <UContainer
    style="
      margin-top: 50px;
      width: 80%;
      max-width: 1200px;
      margin-left: auto;
      margin-right: auto;
    "
  >
    <!-- <h2>Helper Chatbot Response</h2> -->
    <UCard
      :style="{
        backgroundColor: 'rgb(250, 250, 250)',
      }"
    >
      <div v-if="definition">
        <!-- Robot icon with font-size large and dark grey color -->
        <UIcon
          name="i-material-symbols:smart-toy-outline"
          :style="{ fontSize: 'large', color: 'rgb(60, 60, 60)' }"
        />

        <!-- SMS icon with font-size large, margin-bottom 6px, and dark grey color -->
        <UIcon
          name="i-material-symbols:sms-outline"
          :style="{
            fontSize: 'large',
            marginBottom: '6px',
            color: 'rgb(60, 60, 60)',
          }"
        />
      </div>

      <div v-if="definition">
        {{ definition }}
      </div>

      <div v-if="category">
        <small
          ><br >
          Category: {{ category }}</small
        >
      </div>
      <div v-else>
        <p>No matching definition found yet.</p>
      </div>
    </UCard>
  </UContainer>
</template>

<script>
export default {
  props: {
    searchText: {
      type: String,
      required: true,
    },
    searchPerformed: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      category: null,
      definition: null,
    };
  },
  watch: {
    searchPerformed(newVal) {
      if (newVal) {
        this.classifyQuery(this.searchText);
      }
    },
  },
  methods: {
    async classifyQuery(query) {
      try {
        const { useApiClient } = await import("@/composables/useApiClient");
        const { apiClient } = useApiClient();
        const category = await apiClient("/classify_query", {
          body: { query },
          responseType: "text",
        });
        this.category = category;

        this.processCategory();
      } catch (error) {
        console.error("Error classifying query:", error);
      }
    },
    processCategory() {
      if (!this.category) {
        console.error("Category not set.");
        return;
      }

      const term = this.category.split(" (")[0];
      const tableType = this.category.match(/\(([^)]+)\)/);

      if (!tableType) {
        console.error("Invalid category format.");
        return;
      }

      const type = tableType[1];
      let table = "";

      if (type === "concept") {
        table = "Concepts";
      } else if (type === "principle") {
        table = "HCCH Principles themes";
      }

      this.fetchData(term, table);
    },

    async fetchData(term, table) {
      try {
        const { useApiClient } = await import("@/composables/useApiClient");
        const { apiClient } = useApiClient();
        const data = await apiClient("/search/full_table", { body: { table } });

        let matchedEntry;
        if (table === "HCCH Principles themes") {
          matchedEntry = data.find(
            (entry) => entry.Theme && entry.Theme.includes(term),
          );
        } else {
          matchedEntry = data.find(
            (entry) => entry.Keywords && entry.Keywords.includes(term),
          );
        }

        if (matchedEntry) {
          if (table === "HCCH Principles themes") {
            this.definition =
              matchedEntry["Full text"] || "No full text found for this term.";
          } else {
            this.definition =
              matchedEntry.Definition || "No definition found for this term.";
          }
        } else {
          this.definition = "No matching entry found for this term.";
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    },
  },
};
</script>
