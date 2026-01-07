import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";
import { evaluate } from "mathjs";

export const calculatorTool = new DynamicStructuredTool({
  name: "calculator",
  description:
    "Perform mathematical calculations. Supports basic arithmetic, algebra, trigonometry, and more.",
  schema: z.object({
    expression: z
      .string()
      .describe(
        "The mathematical expression to evaluate (e.g., '2 + 2', 'sqrt(16)', 'sin(pi/2)')",
      ),
  }),
  func: async ({ expression }) => {
    const result = evaluate(expression);
    return `${expression} = ${result}`;
  },
});
