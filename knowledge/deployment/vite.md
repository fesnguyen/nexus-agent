# Vite Complete Learning Roadmap
> Learn Vite from absolute beginner to advanced through mental models, examples, and hands-on practice.

---

# 1. Introduction to Vite

## Objectives

Learn:

- What Vite is
- Why Vite was created
- The problems with Webpack
- Development vs Production
- ES Modules
- Hot Module Replacement (HMR)

## Mental Model

Traditional bundler:

```
Source Files
      │
      ▼
 Bundle Everything
      │
      ▼
 Start Dev Server
```

Vite:

```
Source Files
      │
      ▼
 Vite Dev Server
      │
      ▼
 Browser requests files only when needed
```

---

## Why is Vite Fast?

When the browser requests

```tsx
App.tsx
```

Vite only serves

```
App.tsx
```

If App imports

```tsx
Navbar.tsx
```

only Navbar is transformed.

Nothing else.

---

## Development

```
Browser
     │
     ▼
localhost:5173
     │
     ▼
Vite Dev Server
     │
     ▼
Transforms files on demand
```

---

## Production

```
Source

↓

Rollup

↓

Optimized Bundle

↓

dist/
```

---

# 2. Creating a Project

## Install

```bash
npm create vite@latest
```

or

```bash
pnpm create vite
```

Choose

```
React

TypeScript
```

Install dependencies

```bash
npm install
```

Run

```bash
npm run dev
```

Output

```
Local:

http://localhost:5173
```

---

## Build

```bash
npm run build
```

Preview

```bash
npm run preview
```

---

# 3. Understanding Project Structure

```
my-app/

├── public/
│
├── src/
│   ├── assets/
│   ├── components/
│   ├── App.tsx
│   └── main.tsx
│
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── node_modules/
```

---

## public/

Used for static assets.

```
public/

logo.png
robots.txt
favicon.ico
```

Access directly

```
/logo.png
```

Example

```tsx
<img src="/logo.png" />
```

---

## src/

Everything here is compiled.

```
src/

App.tsx

main.tsx

components/

assets/
```

---

## main.tsx

Application entry point.

```tsx
import ReactDOM from "react-dom/client";
import App from "./App";

ReactDOM.createRoot(
    document.getElementById("root")!
).render(
    <App />
);
```

---

## App.tsx

```tsx
function App() {
    return (
        <h1>Hello Vite</h1>
    );
}

export default App;
```

---

# 4. npm Scripts

Open

```
package.json
```

Example

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

---

## npm run dev

Starts

```
Vite Dev Server
```

---

## npm run build

Creates

```
dist/
```

---

## npm run preview

Runs the production build locally.

---

# 5. Vite Configuration

Open

```
vite.config.ts
```

Basic

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
    plugins: [react()]
});
```

---

## Server Port

```ts
export default defineConfig({
    server: {
        port: 3000
    }
});
```

Run

```
localhost:3000
```

---

## Auto Open Browser

```ts
server: {
    open: true
}
```

---

## Host

```ts
server: {
    host: true
}
```

Allows other devices on the LAN to access the dev server.

---

# 6. Aliases

Without alias

```tsx
import Button from "../../../../components/Button";
```

With alias

```tsx
import Button from "@/components/Button";
```

Configuration

```ts
import path from "path";

resolve: {
    alias: {
        "@": path.resolve(__dirname, "./src")
    }
}
```

---

# 7. Static Assets

Import image

```tsx
import logo from "./assets/logo.png";

<img src={logo} />
```

---

SVG

```tsx
import icon from "./icon.svg";

<img src={icon} />
```

---

JSON

```tsx
import users from "./users.json";

console.log(users);
```

---

CSS

```tsx
import "./index.css";
```

---

# 8. Environment Variables

Create

```
.env
```

Example

```
VITE_API_URL=http://localhost:8000
```

Access

```ts
console.log(import.meta.env.VITE_API_URL);
```

Wrong

```
API_URL=
```

Cannot be accessed.

Must begin with

```
VITE_
```

---

Production

```
.env.production
```

Development

```
.env.development
```

---

# 9. Hot Module Replacement

Suppose

```tsx
function App() {
    return (
        <h1>Hello</h1>
    );
}
```

Change

```tsx
<h1>Hello World</h1>
```

Browser updates instantly.

No page refresh.

No losing state.

---

# 10. Plugins

Install React plugin

```bash
npm install @vitejs/plugin-react
```

Configure

```ts
plugins: [
    react()
]
```

Multiple plugins

```ts
plugins: [
    react(),
    svgr(),
    checker()
]
```

---

# 11. Build Optimization

Code Splitting

```tsx
const Admin = lazy(() => import("./Admin"));
```

Only loads when needed.

---

Dynamic Import

```ts
const module = await import("./math");
```

---

Tree Shaking

Unused code

```ts
export function hello() {}

export function unused() {}
```

Only

```
hello()
```

will exist in production.

---

# 12. Proxy API

Instead of

```
localhost:8000
```

everywhere

Configure

```ts
server: {
    proxy: {
        "/api": {
            target: "http://localhost:8000",
            changeOrigin: true
        }
    }
}
```

Request

```ts
fetch("/api/chat");
```

Automatically becomes

```
http://localhost:8000/api/chat
```

---

# 13. Deployment

Build

```bash
npm run build
```

Produces

```
dist/
```

Deploy

```
dist/
```

to

- Vercel
- Netlify
- GitHub Pages
- Nginx
- Docker

---

If hosted under

```
example.com/my-app/
```

Configure

```ts
export default defineConfig({
    base: "/my-app/"
});
```

---

# 14. Debugging

Useful logs

```ts
console.log(import.meta.env);
```

Clear cache

```bash
rm -rf node_modules
```

Install again

```bash
npm install
```

Delete Vite cache

```bash
rm -rf node_modules/.vite
```

Restart

```bash
npm run dev
```

---

Common Errors

### Module not found

Usually wrong import.

---

### Alias not working

Forgot

```ts
resolve.alias
```

---

### Environment variable undefined

Forgot

```
VITE_
```

---

### Changes not updating

Restart

```bash
npm run dev
```

---

# 15. Advanced Topics

## Library Mode

```ts
export default defineConfig({
    build: {
        lib: {
            entry: "src/index.ts",
            name: "MyLibrary"
        }
    }
});
```

---

## Manual Chunks

```ts
build: {
    rollupOptions: {
        output: {
            manualChunks: {
                react: [
                    "react",
                    "react-dom"
                ]
            }
        }
    }
}
```

---

## Analyze Bundle

```bash
npm install rollup-plugin-visualizer
```

```ts
import { visualizer } from "rollup-plugin-visualizer";

plugins: [
    visualizer()
]
```

Produces

```
stats.html
```

Open it to inspect bundle size.

---

## Vitest

Install

```bash
npm install -D vitest
```

Example

```ts
import { expect, test } from "vitest";

test("sum", () => {
    expect(1 + 1).toBe(2);
});
```

---

## Plugin Example

```ts
export default function MyPlugin() {
    return {
        name: "my-plugin",

        transform(code, id) {
            console.log(id);

            return code;
        }
    };
}
```

---

## How Vite Internally Works

```
Browser

↓

Request App.tsx

↓

Vite

↓

Transform TypeScript

↓

Transform JSX

↓

Resolve Imports

↓

Serve JavaScript

↓

Browser Executes
```

During production:

```
Source Files

↓

Plugin Pipeline

↓

Rollup

↓

Tree Shaking

↓

Code Splitting

↓

Minify

↓

Hash Assets

↓

dist/
```

---

# Final Project Ideas

After finishing this guide, try building:

1. Todo App
2. Weather App
3. Notes App
4. Chat Application
5. Blog
6. Dashboard
7. File Explorer
8. AI Chat UI
9. Kanban Board
10. Portfolio Website

Each project will reinforce a different part of the Vite ecosystem while preparing you for production-scale frontend development.