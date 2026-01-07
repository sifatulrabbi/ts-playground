import React from "react";
import { Box, Text } from "ink";
import { ReasoningBlock } from "./ReasoningBlock";

export interface MessageProps {
  role: "user" | "agent" | "tool" | "error";
  content: string;
  contentBlocks?: Array<{ type: string; text?: string; reasoning?: string }>;
}

export const Message: React.FC<MessageProps> = ({
  role,
  content,
  contentBlocks,
}) => {
  const roleColors = {
    user: "cyan",
    agent: "green",
    tool: "yellow",
    error: "red",
  };

  const roleLabels = {
    user: "You",
    agent: "Agent",
    tool: "Tool",
    error: "Error",
  };

  const color = roleColors[role];
  const label = roleLabels[role];

  return (
    <Box flexDirection="column" marginBottom={1}>
      <Text bold color={color}>
        {label}:
      </Text>
      {contentBlocks && contentBlocks.length > 0 ? (
        <Box flexDirection="column">
          {contentBlocks.map((block, idx) => {
            if (block?.reasoning) {
              return <ReasoningBlock key={idx} content={block.reasoning} />;
            } else if (block?.text) {
              return (
                <Box key={idx} marginLeft={2}>
                  <Text color={color}>{block.text}</Text>
                </Box>
              );
            }
            return null;
          })}
        </Box>
      ) : (
        <Box marginLeft={2}>
          <Text color={color}>{content}</Text>
        </Box>
      )}
    </Box>
  );
};
