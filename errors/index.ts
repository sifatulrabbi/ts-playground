const longRunningTool = async () => {
  for (let i = 0; i < 7; i++) {
    await new Promise((r) => setTimeout(r, 1000));
    console.log("From tool |", i, "seconds went by...");
  }
  console.log("From tool | Done with the tool call");
  return "Tool Result";
};

const james2 = async () => {
  let i = 0; // we'll throw error after the 3rd second.
  const isCanceled = async () => {
    if (i < 2) {
      await new Promise((r) => setTimeout(r, 1000));
      i++;
      await isCanceled();
    } else {
      throw new Error("Testing error throwing");
    }
  };
  isCanceled();

  const toolRes = await longRunningTool();
  console.log("From James2 | tool result:", toolRes);
  console.log("From James2 | done");
};

const main = async () => {
  try {
    await james2();
  } catch (err) {
    console.error("Error in James2 |", err);
  }

  while (true) {
    // just not letting the program stop.
    await new Promise((r) => setTimeout(r, 1000));
  }
};

await main();
