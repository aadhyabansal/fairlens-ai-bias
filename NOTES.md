# Frontend notes — figuring out React for FairLens

Writing this down while building Phase 7 so I can explain this stuff in an interview without just reciting definitions.

## The mental shift from "normal" web dev

Old way: find an element, change it directly (jQuery-style).
React way: describe what the UI *should* look like for some data, and let React handle updating the actual page when that data changes. You basically never touch the DOM by hand.

## Components are just functions

`Navbar.jsx`, `NewAudit.jsx` — each one is a function that returns some JSX (HTML-looking syntax that gets compiled to real JS under the hood). The app is just these functions nested inside each other. That's really it, there's nothing more than "function returns markup."

## Props = how a parent hands data down

`<Link to="/dashboard">` — `to` is a prop. Same idea as a function argument, just named and passed in through the JSX tag.

## useState — the thing to actually understand well

```js
const [currentAudit, setCurrentAudit] = useState(null);
```

The part that tripped me up at first: you can't just do `currentAudit = x`.
You HAVE to call `setCurrentAudit(x)`, because that's the only thing that tells React "hey, re-render whatever depends on this." Plain reassignment would update the variable but React would have no idea anything changed, so nothing on screen would update. (can be a question)

## Context — for when props-passing gets annoying

Normal data flow is parent → child only. Problem: my Upload page sets an audit result, but the Dashboard page (a totally different route) needs to read it. Passing it down through every component in between ("prop drilling") would be miserable.

Context fixes this — `AuditContext.jsx` makes a shared bucket of state any component can reach into via `useAudit()`, no matter how far apart they are in the tree. `AuditProvider` wraps the whole app once in `App.jsx`.

Didn't reach for Redux/Zustand here on purpose — 3 pages, modest shared state, Context (free, built-in) covers it. Would've been the same mistake as the LLM-provider-abstraction overkill thing from the backend.

## React Router — fake multi-page feel

Actual browsers reload the whole page on navigation. React apps are usually one single HTML page where React just swaps components based on the URL — no reload, feels instant.

- `BrowserRouter` watches the URL
- `Routes`/`Route` = "this path → render this component"
- `Link` changes the URL without reloading the page

## Vite

Browsers can't run JSX straight hence needs compiling to plain JS first. Vite does that compiling, runs the dev server, and later bundles everything for deployment. Basically the thing sitting between my code and what the browser actually gets.

## Why there's a proxy in vite.config.js

Frontend = localhost:5173, backend = localhost:8000 → different origins as far as the browser's concerned, and browsers block that by default (CORS).
The proxy quietly forwards my `/api/...` calls to the backend server-side, so the browser only ever thinks it's talking to itself. Avoids dealing with CORS at all in dev.

## Tailwind

Styling straight in the JSX with small utility classes (`px-4 py-2 bg-blue-600`) instead of separate CSS files with custom class names. Took a sec to stop finding this ugly, but it's genuinely faster once you're used to it.

## "walk me through your frontend"

It's a React SPA built with Vite, React Router for client-side nav across the three pages, shared state in a Context provider instead of a state library since the app didn't need that much, Tailwind for styling, and a dev proxy to the FastAPI backend to sidestep CORS locally.

## Bugs I actually hit (keeping these honest, not cleaning them up)

- Blank white screen, no visible error on page → console said App.jsx
  wasn't exporting a default — turned out the file had leftover/broken
  content from editing
- "Invalid hook call" + duplicate React copies error → broken/partial
  node_modules install → `rm -rf node_modules package-lock.json && npm
  install` fixed it
- Tried following an old Tailwind v3 setup (postcss, autoprefixer, config
  file) but this project's on Tailwind v4 via Vite v8, which only needs the
  `@tailwindcss/vite` plugin + one `@import "tailwindcss";` line — v3
  tutorials don't apply here