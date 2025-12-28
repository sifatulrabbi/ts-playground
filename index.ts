const f = Bun.file("./something.txt");
const value = await f.text();
