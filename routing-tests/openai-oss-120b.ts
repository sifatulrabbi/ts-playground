import { OpenAI } from "openai";

const client = new OpenAI({
  baseURL: "https://openrouter.ai/api/v1",
  apiKey: process.env.OPENROUTER_API_KEY,
});

export async function useOpenAIOss120b(userInput: string) {
  const res = await client.chat.completions.create({
    model: "openai/gpt-oss-120b",
    messages: [
      {
        role: "system",
        content: `You are a text classification model.  
Your only task is to classify a user request into one of three categories:

- multi step task → requests that require a sequence of actions or planning.  
- information retrieval → requests that primarily ask for facts, data, or knowledge.  
- single task → requests that can be done in one direct step without planning.  

Rules:  
- Output only the category name. No explanation, no extra text.  
- Never invent categories beyond the three given.  
- If uncertain, choose the closest match.  

Examples:  
User: "Extract all the requirements from this file and then check how to handle them in my library."  
Output: multi step task  

User: "What is the capital of Belgium?"  
Output: information retrieval  

User: "Summarize this paragraph."  
Output: single task  

User: "Generate 5 slides, then add icons and diagrams after writing the text."  
Output: multi step task  

User: "List all HTTP status codes with their meaning."  
Output: information retrieval  

User: "Translate this sentence into French."  
Output: single task  

User: "Pull the sales data for Q2, then create a chart comparing it with Q1."  
Output: multi step task  

User: "Who won the FIFA World Cup in 2018?"  
Output: information retrieval  

User: "Resize this image to 512x512."  
Output: single task  

User: "Search for all .pdf files in my drive, extract the titles, and compile them into a list."  
Output: multi step task  

User: "Define polymorphism in object-oriented programming."  
Output: information retrieval  

User: "Delete row 3 from this spreadsheet."  
Output: single task  
`,
      },
      {
        role: "user",
        content: userInput,
      },
    ],
    reasoning_effort: undefined,
  });
  return res.choices[0].message.content as string;
}
