import { useMercury } from "./mercury";
import { useMistral } from "./mistral";

export const testCases = [
  {
    input:
      "Extract all the requirements from this file and then check how to handle them in my library.",
    expected: "multi step task",
  },
  {
    input: "What is the capital of Belgium?",
    expected: "information retrieval",
  },
  {
    input: "Summarize this paragraph.",
    expected: "single task",
  },
  {
    input:
      "Generate 5 slides, then add icons and diagrams after writing the text.",
    expected: "multi step task",
  },
  {
    input: "List all HTTP status codes with their meaning.",
    expected: "information retrieval",
  },
  {
    input: "Translate this sentence into French.",
    expected: "single task",
  },
  {
    input:
      "Pull the sales data for Q2, then create a chart comparing it with Q1.",
    expected: "multi step task",
  },
  {
    input: "Who won the FIFA World Cup in 2018?",
    expected: "information retrieval",
  },
  {
    input: "Resize this image to 512x512.",
    expected: "single task",
  },
  {
    input:
      "Search for all .pdf files in my drive, extract the titles, and compile them into a list.",
    expected: "multi step task",
  },
  {
    input: "Define polymorphism in object-oriented programming.",
    expected: "information retrieval",
  },
  {
    input: "Delete row 3 from this spreadsheet.",
    expected: "single task",
  },
];

async function testRunner(useModel: (input: string) => Promise<string>) {
  for (const testCase of testCases) {
    const start = Date.now();
    const res = await useModel(testCase.input);
    console.log("I:", testCase.input);
    console.log("O:", res, "    ", res === testCase.expected);
    console.log(((Date.now() - start) / 1000).toFixed(2), "seconds");
    console.log();
  }
}

console.log(">>> using mercury\n");
await testRunner(useMercury);

console.log(">>> using mistral-3b\n");
await testRunner(useMistral);
