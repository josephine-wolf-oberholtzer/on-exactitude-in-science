import { screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { jsonResponse, renderApp } from "../../test/render";

afterEach(() => vi.restoreAllMocks());

const locality = {
	countries: [],
	edge_counts: {},
	edges: [],
	formats: [],
	genres: [],
	id: 1,
	pagination: { page: 1, page_count: 1, page_size: 49, total: 1 },
	styles: [],
	vertices: [
		{
			child_count: 3,
			distance: 0,
			eid: 42,
			id: 1,
			label: "artist",
			name: "Björk",
		},
		{ distance: 1, eid: 7, id: 2, label: "release", name: "Debut" },
	],
};

describe("Locality", () => {
	it("renders the center and its neighbors", async () => {
		const fetch = vi
			.spyOn(globalThis, "fetch")
			.mockResolvedValue(jsonResponse(locality));
		renderApp("/artist/42");
		expect(
			await screen.findByRole("heading", { name: "Björk" }),
		).toBeInTheDocument();
		expect(screen.getByText("Debut")).toBeInTheDocument();
		expect(screen.getByText("3 children")).toBeInTheDocument();
		expect(String((fetch.mock.calls[0][0] as Request).url)).toContain(
			"/locality/?eid=42&index=0&label=artist&page=1",
		);
	});

	it("shows an error when the entity is not found", async () => {
		vi.spyOn(globalThis, "fetch").mockResolvedValue(
			jsonResponse({ detail: "No artist 42" }, 404),
		);
		renderApp("/artist/42");
		expect(await screen.findByText(/could not load/i)).toBeInTheDocument();
	});

	it("rejects an unknown label without calling the API", () => {
		const fetch = vi.spyOn(globalThis, "fetch");
		renderApp("/nope/42");
		expect(screen.getByText(/not a valid entity/i)).toBeInTheDocument();
		expect(fetch).not.toHaveBeenCalled();
	});
});
