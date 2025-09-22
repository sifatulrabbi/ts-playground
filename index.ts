import { z } from "zod";
import { ChatOpenAI } from "@langchain/openai";

const outputSchema = z.object({
  message: z.string().describe("Your response to the user's message."),
});

const llm = new ChatOpenAI({
  model: "gpt-5",
  useResponsesApi: true,
  reasoning: {
    effort: "low",
    summary: "auto",
  },
});

function main() {}
