import React, { useState, useEffect } from "react";
import { Box, Text } from "ink";

const SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"];

interface ToolIndicatorProps {
  toolName: string;
}

export const ToolIndicator: React.FC<ToolIndicatorProps> = ({ toolName }) => {
  const [frame, setFrame] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setFrame((prev) => (prev + 1) % SPINNER_FRAMES.length);
    }, 80);

    return () => clearInterval(interval);
  }, []);

  const toolDisplayNames: Record<string, string> = {
    tavily_search: "Searching the web",
    calculator: "Calculating",
    get_current_time: "Getting current time",
  };

  const displayName = toolDisplayNames[toolName] || `Using ${toolName}`;

  return (
    <Box marginLeft={2}>
      <Text color="yellow">{SPINNER_FRAMES[frame]} </Text>
      <Text color="yellow">{displayName}...</Text>
    </Box>
  );
};
