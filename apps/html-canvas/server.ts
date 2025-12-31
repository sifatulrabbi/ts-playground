const PORT = 3000;

const MIME_TYPES: Record<string, string> = {
  ".html": "text/html",
  ".css": "text/css",
  ".js": "text/javascript",
  ".ts": "text/javascript",
  ".json": "application/json",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
};

function getMimeType(path: string): string {
  const ext = path.substring(path.lastIndexOf("."));
  return MIME_TYPES[ext] || "application/octet-stream";
}

const server = Bun.serve({
  port: PORT,

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    let pathname = url.pathname;

    // Serve index.html for root path
    if (pathname === "/") {
      pathname = "/index.html";
    }

    // Handle TypeScript files - transpile on the fly
    if (pathname.endsWith(".ts") && !pathname.includes("server.ts")) {
      const filePath = "./public" + pathname;
      const file = Bun.file(filePath);

      if (await file.exists()) {
        const transpiler = new Bun.Transpiler({ loader: "ts" });
        const code = await file.text();
        const result = transpiler.transformSync(code);

        return new Response(result, {
          headers: { "Content-Type": "text/javascript" },
        });
      }
    }

    // Serve static files
    const filePath = "./public" + pathname;
    const file = Bun.file(filePath);

    if (await file.exists()) {
      return new Response(file, {
        headers: { "Content-Type": getMimeType(pathname) },
      });
    }

    return new Response("Not Found", { status: 404 });
  },
});

console.log(`Server running at http://localhost:${PORT}`);
