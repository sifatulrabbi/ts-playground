import React, { useState } from "react";
import { Box, Text } from "ink";
import { MessageList } from "./MessageList";
import { MessageProps } from "./Message";
import { Input } from "./Input";
import { ThinkingIndicator } from "./ThinkingIndicator";
import { ToolIndicator } from "./ToolIndicator";

interface ChatUIProps {
  onMessage: (
    message: string,
  ) => Promise<AsyncGenerator<MessageProps, void, unknown>>;
  onExit: () => void;
}

export const ChatUI: React.FC<ChatUIProps> = ({ onMessage, onExit }) => {
  const [messages, setMessages] = useState<MessageProps[]>([]);
  const [input, setInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [currentTool, setCurrentTool] = useState<string | null>(null);

  const handleSubmit = async (value: string) => {
    if (!value.trim() || isProcessing) return;

    const userMessage = value.trim();
    setInput("");

    // Handle special commands
    if (userMessage === "/exit") {
      onExit();
      return;
    }

    if (userMessage === "/clear") {
      setMessages([]);
      return;
    }

    // Add user message
    setMessages((prev) => [
      ...prev,
      { role: "user", content: userMessage } as MessageProps,
    ]);

    setIsProcessing(true);
    setIsThinking(true);

    try {
      const stream = await onMessage(userMessage);

      for await (const chunk of stream) {
        setIsThinking(false);

        // Handle different chunk types
        if (chunk.role === "agent" || chunk.role === "error") {
          setMessages((prev) => [...prev, chunk]);
        } else if (chunk.role === "tool") {
          setCurrentTool(chunk.content);
          // Don't add tool status to message list, just show indicator
        }
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "error",
          content: `Error: ${error instanceof Error ? error.message : String(error)}`,
        } as MessageProps,
      ]);
    } finally {
      setIsProcessing(false);
      setIsThinking(false);
      setCurrentTool(null);
    }
  };

  return (
    <Box flexDirection="column" padding={1}>
      <Box
        borderStyle="round"
        borderColor="blue"
        flexDirection="column"
        padding={1}
      >
        <Text bold color="blue">
          LangGraph Agent Chat
        </Text>
        <Text dimColor>Type /exit to quit, /clear to clear history</Text>
      </Box>

      <Box flexDirection="column" marginTop={1} marginBottom={1}>
        <MessageList messages={messages} />

        {isThinking && (
          <Box marginTop={1}>
            <ThinkingIndicator />
          </Box>
        )}

        {currentTool && (
          <Box marginTop={1}>
            <ToolIndicator toolName={currentTool} />
          </Box>
        )}
      </Box>

      <Input
        value={input}
        onChange={setInput}
        onSubmit={handleSubmit}
        disabled={isProcessing}
      />
    </Box>
  );
};
