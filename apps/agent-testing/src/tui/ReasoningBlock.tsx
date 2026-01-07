import React from "react";
import { Box, Text } from "ink";

interface ReasoningBlockProps {
  content: string;
}

export const ReasoningBlock: React.FC<ReasoningBlockProps> = ({ content }) => {
  return (
    <Box
      flexDirection="column"
      marginLeft={2}
      marginBottom={1}
      borderStyle="single"
      borderColor="gray"
      paddingX={1}
    >
      <Text color="gray" bold>
        Thinking
      </Text>
      <Text color="gray" dimColor>
        {content}
      </Text>
    </Box>
  );
};
