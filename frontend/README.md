# Frontend

React 19, TypeScript, Vite, Redux Toolkit (RTK Query), React Router and Material UI.

    npm install
    npm run dev          # http://localhost:5173, proxies /api to the backend on :9090
    npm test             # Vitest + Testing Library
    npm run lint         # Biome (config lives in the repository root)
    npm run build        # type-check, then bundle to dist/

## API types

`src/api/schema.d.ts` is generated from the backend's OpenAPI schema. After
changing the backend's request or response models, regenerate it:

    npm run api:schema   # dump the schema from the FastAPI app into openapi.json
    npm run api:types    # generate src/api/schema.d.ts from it

The legacy webpack frontend is kept in `archive/frontend/`.
