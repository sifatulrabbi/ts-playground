/// <reference types="bun-types" />

const f = Bun.file("./txt.txt");

let text = await f.text();
const parsed = JSON.parse(JSON.parse(text));

console.log(parsed, "\n", typeof parsed);
