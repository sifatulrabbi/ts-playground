# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Monorepo Structure

This is a Bun workspace monorepo with the following layout:

```
ts-playground/
├── apps/           # Applications (workspaced)
├── libs/           # Shared libraries (workspaced)
├── archived/       # Old experiments (NOT workspaced, gitignored)
├── package.json    # Root workspace config
└── tsconfig.json   # Base TypeScript config
```

**Workspaces:** Only `apps/*` and `libs/*` are part of the Bun workspace. The `archived/` directory is excluded.

**Naming convention:** Packages use `@apps/<name>` for apps and `@libs/<name>` for libraries.

## Commands

All commands run from the repository root:

```bash
# Install dependencies (links workspace packages)
bun install

# Run html-canvas app
bun run dev:html-canvas      # Dev server with hot reload (port 3000)
bun run start:html-canvas    # Production server
bun run build:html-canvas    # Build to dist/

# Run any app script from root
bun run --cwd apps/<app-name> <script>

# Run scripts in specific package
bun run --filter @apps/<name> <script>
bun run --filter @libs/<name> <script>

# Run across all packages
bun run --filter '*' <script>
```

## Adding New Packages

**New app:**

1. Create `apps/<name>/package.json` with `"name": "@apps/<name>"`
2. Create `apps/<name>/tsconfig.json` extending `../../tsconfig.json`
3. Add root scripts: `"dev:<name>": "bun run --cwd apps/<name> dev"`

**New lib:**

1. Create `libs/<name>/package.json` with `"name": "@libs/<name>"`
2. Create `libs/<name>/tsconfig.json` extending `../../tsconfig.json`
3. Use in other packages: add `"@libs/<name>": "workspace:*"` to dependencies

## TypeScript Configuration

- Root `tsconfig.json` contains shared compiler options
- Each package extends root: `"extends": "../../tsconfig.json"`
- Uses Bun types (`bun-types`) for runtime APIs

## Apps

### @apps/html-canvas

Vanilla TypeScript app for serving static HTML/CSS/TS using Bun's built-in server.

- `server.ts` - Bun HTTP server that transpiles `.ts` files on-the-fly
- `public/` - Static files (HTML, CSS, client-side TS)
- Serves from `http://localhost:3000`
