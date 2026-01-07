import { ChatOpenAIResponses } from "@langchain/openai";
import {
  StateGraph,
  MessagesAnnotation,
  START,
  END,
  Annotation,
} from "@langchain/langgraph";
import { ToolNode } from "@langchain/langgraph/prebuilt";
import {
  AIMessage,
  BaseMessage,
  SystemMessage,
  ToolMessage,
} from "@langchain/core/messages";
import { tools } from "./tools";

const model = new ChatOpenAIResponses({
  modelName: "gpt-5.2",
  reasoning: {
    effort: "low",
    summary: "auto",
  },
}).bindTools(tools);

function shouldContinue(
  state: typeof MessagesAnnotation.State,
): "tools" | typeof END {
  const lastMessage = state.messages.at(-1) as AIMessage | undefined;

  if (lastMessage?.tool_calls?.length) {
    return "tools";
  }
  return END;
}

async function callModel(state: typeof MessagesAnnotation.State) {
  const sysPrompt = new SystemMessage({
    content:
      "You are a helpful assistant here to serve the user like a loyal servant.",
  });
  const response = await model.invoke([
    sysPrompt,
    new AIMessage({
      content: "",
      tool_calls: [
        {
          name: "get_memory",
          id: "get_memory",
          args: {},
        },
      ],
    }),
    new ToolMessage({
      name: "get_memory",
      content: "- User's name is Sifatul\n- User lives drinking Coffee",
      tool_call_id: "get_memory",
    }),
    ...state.messages,
  ]);
  return {
    messages: [response],
  };
}

const StateAnnotation = Annotation.Root({
  ...MessagesAnnotation.spec,
});

const workflow = new StateGraph(StateAnnotation)
  .addNode("agent", callModel)
  .addNode("tools", new ToolNode(tools))
  .addEdge(START, "agent")
  .addConditionalEdges("agent", shouldContinue, {
    tools: "tools",
    [END]: END,
  })
  .addEdge("tools", "agent");

export const graph = workflow.compile();

export interface AgentInput {
  messages: BaseMessage[];
}

export async function* streamAgent(input: AgentInput) {
  const stream = await graph.stream(input, { streamMode: "values" });

  for await (const chunk of stream) {
    yield chunk;
  }
}
