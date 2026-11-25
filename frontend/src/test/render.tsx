import { render } from "@testing-library/react";
import { createMemoryRouter } from "react-router";
import { RouterProvider } from "react-router/dom";
import { Providers } from "../app/Providers";
import { routes } from "../app/routes";
import { setupStore } from "../app/store";

/**
 * Render the whole app at a URL, with a fresh store.
 */
export const renderApp = (url: string) => {
	const router = createMemoryRouter(routes, { initialEntries: [url] });
	return render(
		<Providers store={setupStore()}>
			<RouterProvider router={router} />
		</Providers>,
	);
};

export const jsonResponse = (body: unknown, status = 200) =>
	new Response(JSON.stringify(body), {
		headers: { "content-type": "application/json" },
		status,
	});
