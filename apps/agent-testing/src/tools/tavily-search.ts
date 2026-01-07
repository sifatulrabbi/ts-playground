import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";
import { tavily, TavilyClient } from "@tavily/core";

let tavilyClient: TavilyClient | null = null;

function getClient(): TavilyClient {
  if (!tavilyClient) {
    tavilyClient = tavily({ apiKey: process.env.TAVILY_API_KEY || "" });
  }
  return tavilyClient;
}

export const tavilySearchTool = new DynamicStructuredTool({
  name: "tavily_search",
  description:
    "Search the web for current information. Use this when you need to find recent data, news, or information not in your training data.",
  schema: z.object({
    query: z.string().describe("The search query to look up"),
  }),
  func: async ({ query }) => {
    if (!process.env.TAVILY_API_KEY) {
      return "Error: TAVILY_API_KEY not configured. Cannot perform web search.";
    }

    const response = await getClient().search(query, { maxResults: 5 });

    if (!response.results || response.results.length === 0) {
      return `No results found for query: "${query}"`;
    }

    const formattedResults = response.results
      .map(
        (
          result: { title: string; url: string; content: string },
          idx: number,
        ) =>
          `${idx + 1}. ${result.title}\n   URL: ${result.url}\n   ${result.content}`,
      )
      .join("\n\n");

    return `Search results for "${query}":\n\n${formattedResults}`;
  },
});
