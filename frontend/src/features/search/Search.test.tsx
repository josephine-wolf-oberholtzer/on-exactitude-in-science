import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { jsonResponse, renderApp } from "../../test/render";

afterEach(() => vi.restoreAllMocks());

describe("Search", () => {
	it("renders the search box", () => {
		renderApp("/");
		expect(screen.getByLabelText(/search for/i)).toBeInTheDocument();
	});

	it("lists results, linking each to its locality", async () => {
		const fetch = vi.spyOn(globalThis, "fetch").mockResolvedValue(
			jsonResponse({
				results: [
					{
						id: 42,
						index: 0,
						label: "artist",
						name: "Björk",
						url: "/entity/?id=42&label=artist",
					},
				],
			}),
		);
		renderApp("/");
		await userEvent.type(screen.getByLabelText(/search for/i), "bjork");
		const link = await screen.findByRole("link", { name: /björk/i });
		expect(link).toHaveAttribute("href", "/artist/42");
		// Typing fires a request per keystroke once past the minimum length
		const lastRequest = fetch.mock.lastCall?.[0] as Request;
		expect(lastRequest.url).toContain("/search/?name=bjork");
	});
});
