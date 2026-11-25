import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter } from "react-router";
import { RouterProvider } from "react-router/dom";
import { Providers } from "./app/Providers";
import { routes } from "./app/routes";
import { setupStore } from "./app/store";

const store = setupStore();
const router = createBrowserRouter(routes);

// biome-ignore lint/style/noNonNullAssertion: index.html always has #root
createRoot(document.getElementById("root")!).render(
	<StrictMode>
		<Providers store={store}>
			<RouterProvider router={router} />
		</Providers>
	</StrictMode>,
);
