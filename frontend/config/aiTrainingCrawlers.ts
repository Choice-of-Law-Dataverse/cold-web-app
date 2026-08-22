/**
 * Crawlers whose documented purpose is collecting content for model training
 * or reselling it as AI training datasets. These are disallowed in robots.txt,
 * matching the `ai-train=no` content signal.
 *
 * Crawlers that fetch pages to answer a user (ChatGPT-User, Claude-User,
 * Perplexity-User, DuckAssistBot, …), build a search index (OAI-SearchBot,
 * Applebot, Amazonbot, Bravebot, …), serve RAG at request time (TavilyBot,
 * FirecrawlAgent, ExaBot, …) or act as coding agents are deliberately absent:
 * they are allowed by the wildcard group under `search=yes, ai-input=yes`.
 *
 * Generic scraping frameworks (Scrapy, Crawl4AI) are also absent — blocking
 * them would block legitimate academic reuse of this CC BY 4.0 dataset.
 *
 * Sourced from https://github.com/ai-robots-txt/ai.robots.txt
 */
export const AI_TRAINING_CRAWLERS = [
  "AI2Bot",
  "Ai2Bot-Dolma",
  "aiHitBot",
  "anthropic-ai",
  "ApifyBot",
  "ApifyWebsiteContentCrawler",
  "Applebot-Extended",
  "Brightbot",
  "Bytespider",
  "CCBot",
  "ChatGLM-Spider",
  "Claude-Web",
  "ClaudeBot",
  "CloudVertexBot",
  "cohere-training-data-crawler",
  "Cotoyogi",
  "CragCrawler",
  "DeepSeekBot",
  "Diffbot",
  "FacebookBot",
  "Factset_spyderbot",
  "FriendlyCrawler",
  "Google-CloudVertexBot",
  "Google-Extended",
  "GPTBot",
  "ICC-Crawler",
  "img2dataset",
  "imageSpider",
  "ImagesiftBot",
  "ISSCyberRiskCrawler",
  "Kangaroo Bot",
  "laion-huggingface-processor",
  "LAIONDownloader",
  "LCC",
  "Linguee Bot",
  "meta-externalagent",
  "MyCentralAIScraperBot",
  "NagetBot",
  "omgili",
  "omgilibot",
  "PanguBot",
  "Panscient",
  "panscient.com",
  "Poseidon Research Crawler",
  "SBIntuitionsBot",
  "SemrushBot-OCOB",
  "Sidetrade indexer bot",
  "TikTokSpider",
  "Timpibot",
  "VelenPublicWebCrawler",
  "Webzio-Extended",
  "YandexAdditional",
  "YandexAdditionalBot",
];
