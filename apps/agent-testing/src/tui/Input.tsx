import React from "react";
import { Box, Text } from "ink";
import TextInput from "ink-text-input";

interface InputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (value: string) => void;
  disabled?: boolean;
}

export const Input: React.FC<InputProps> = ({
  value,
  onChange,
  onSubmit,
  disabled = false,
}) => {
  return (
    <Box marginTop={1}>
      <Text color="blue" bold>
        {"> "}
      </Text>
      {!disabled ? (
        <TextInput value={value} onChange={onChange} onSubmit={onSubmit} />
      ) : (
        <Text dimColor>Processing...</Text>
      )}
    </Box>
  );
};
