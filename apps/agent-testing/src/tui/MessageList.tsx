import React from "react";
import { Box } from "ink";
import { Message, MessageProps } from "./Message";

interface MessageListProps {
  messages: MessageProps[];
}

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  return (
    <Box flexDirection="column">
      {messages.map((message, idx) => (
        <Message key={idx} {...message} />
      ))}
    </Box>
  );
};
