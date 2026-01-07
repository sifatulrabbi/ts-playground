import React from "react";
import { render } from "ink";
import { config } from "dotenv";
import { HumanMessage, AIMessage, BaseMessage } from "@langchain/core/messages";
import { ChatUI } from "./tui/ChatUI";
import { MessageProps } from "./tui/Message";
import { streamAgent } from "./agent";

// Load environment variables
config();

// Validate required API keys
function validateEnvironment() {
  const requiredKeys = ["OPENAI_API_KEY", "TAVILY_API_KEY"];
  const missing = requiredKeys.filter((key) => !process.env[key]);

  if (missing.length > 0) {
    console.error("❌ Missing required environment variables:");
    missing.forEach((key) => {
      console.error(`   - ${key}`);
    });
    console.error("\nPlease create a .env file with the required keys.");
    console.error("See .env.example for reference.");
    process.exit(1);
  }
}

// Validate environment on startup
validateEnvironment();

// Store conversation history
const conversationHistory: Array<BaseMessage> = [];

// Handle messages from the UI
async function* handleMessage(
  userMessage: string,
): AsyncGenerator<MessageProps, void, unknown> {
  // Add user message to history
  conversationHistory.push(new HumanMessage(userMessage));

  try {
    // Stream the agent's response
    let lastAgentMessage: AIMessage | null = null;

    for await (const chunk of streamAgent({
      messages: conversationHistory,
    })) {
      const messages = chunk.messages;
      const lastMessage = messages[messages.length - 1];

      // Check if this is an AI message with tool calls
      if (lastMessage.type === "ai") {
        const aiMessage = lastMessage as AIMessage;

        // If there are tool calls, yield tool indicators
        if (aiMessage.tool_calls && aiMessage.tool_calls.length > 0) {
          for (const toolCall of aiMessage.tool_calls) {
            yield {
              role: "tool",
              content: toolCall.name,
            } as MessageProps;
          }
        }

        lastAgentMessage = aiMessage;
      }
    }

    // Process the final agent message
    if (lastAgentMessage) {
      conversationHistory.push(lastAgentMessage);

      // Extract content blocks from various formats
      const contentBlocks: Array<{
        type: string;
        text?: string;
        reasoning?: string;
      }> = [];

      let textContent = "";

      // Handle content as array (OpenAI reasoning models return array with type blocks)
      if (Array.isArray(lastAgentMessage.content)) {
        for (const block of lastAgentMessage.content) {
          if (typeof block === "object" && block !== null) {
            const b = block as Record<string, unknown>;
            if (b.type === "text" && typeof b.text === "string") {
              contentBlocks.push({ type: "text", text: b.text });
              textContent += b.text;
            } else if (
              b.type === "reasoning" &&
              typeof b.reasoning === "string"
            ) {
              contentBlocks.push({ type: "reasoning", reasoning: b.reasoning });
            } else if (
              b.type === "thinking" &&
              typeof b.thinking === "string"
            ) {
              // Anthropic format
              contentBlocks.push({ type: "reasoning", reasoning: b.thinking });
            }
          }
        }
      } else if (typeof lastAgentMessage.content === "string") {
        textContent = lastAgentMessage.content;
      }

      // Yield the final message
      yield {
        role: "agent",
        content: textContent || JSON.stringify(lastAgentMessage.content),
        contentBlocks: contentBlocks.length > 0 ? contentBlocks : undefined,
      } as MessageProps;
    }
  } catch (error) {
    yield {
      role: "error",
      content: `Error: ${error instanceof Error ? error.message : String(error)}`,
    } as MessageProps;
  }
}

// Handle exit
function handleExit() {
  console.log("\n👋 Goodbye!");
  process.exit(0);
}

// Handle Ctrl+C
process.on("SIGINT", () => {
  handleExit();
});

// Render the app
console.log("🚀 Starting LangGraph Agent Chat...\n");

render(
  React.createElement(ChatUI, {
    onMessage: handleMessage,
    onExit: handleExit,
  }),
);
