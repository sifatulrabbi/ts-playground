import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";

export const currentTimeTool = new DynamicStructuredTool({
  name: "get_current_time",
  description:
    "Get the current date and time. Optionally specify a timezone (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo').",
  schema: z.object({
    timezone: z
      .string()
      .optional()
      .describe(
        "Optional timezone identifier (e.g., 'America/New_York'). Defaults to UTC.",
      ),
  }),
  func: async ({ timezone }) => {
    const now = new Date();

    if (timezone) {
      try {
        const formatter = new Intl.DateTimeFormat("en-US", {
          timeZone: timezone,
          dateStyle: "full",
          timeStyle: "long",
        });
        return `Current time in ${timezone}: ${formatter.format(now)}`;
      } catch {
        return `Invalid timezone: ${timezone}. Using UTC: ${now.toUTCString()}`;
      }
    }

    return `Current time (UTC): ${now.toUTCString()}`;
  },
});
