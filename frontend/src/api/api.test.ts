import { describe, expect, it } from "vitest";
import { serializeParams } from "./api";

describe("serializeParams", () => {
	it("repeats keys for lists, as FastAPI expects", () => {
		expect(serializeParams({ genres: ["Jazz", "Funk"], page: 2 })).toBe(
			"genres=Jazz&genres=Funk&page=2",
		);
	});

	it("omits undefined values", () => {
		expect(serializeParams({ index: undefined, page: 1 })).toBe("page=1");
	});
});
