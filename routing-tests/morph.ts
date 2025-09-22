import { OpenAI } from "openai";

const client = new OpenAI({
  baseURL: "https://openrouter.ai/api/v1",
  apiKey: process.env.OPENROUTER_API_KEY,
});
const start = Date.now();

const res = await client.completions.create({
  model: "morph/morph-v3-large",
  prompt: `Classify the following user request into exactly one of these categories:  
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

Now classify:  
User: "Translate this sentence into French."  
Output:
`,
  stop: ["\n", "User:", "Output:"],
});

console.log(res.choices[0].text);
console.log(((Date.now() - start) / 1000).toFixed(2), "seconds");
