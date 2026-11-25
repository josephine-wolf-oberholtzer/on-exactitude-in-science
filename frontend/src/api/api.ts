import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { components } from "./schema";

type Schemas = components["schemas"];

export type LocalityResponse = Schemas["LocalityResponse"];
export type LocalityVertex = Schemas["LocalityVertex"];
export type SearchResponse = Schemas["SearchResponse"];
export type VertexLabelName = Schemas["VertexLabelName"];

export const VERTEX_LABEL_NAMES: readonly VertexLabelName[] = [
	"artist",
	"company",
	"master",
	"release",
	"track",
];

export interface LocalityArgs {
	countries?: string[];
	eid: number;
	formats?: string[];
	genres?: string[];
	index?: number;
	label: VertexLabelName;
	labels?: VertexLabelName[];
	page?: number;
	roles?: string[];
	size?: number;
	styles?: string[];
	// START:END, either end optional
	years?: string;
}

export interface SearchArgs {
	label?: VertexLabelName;
	limit?: number;
	name: string;
}

/**
 * FastAPI reads list parameters from repeated keys (``?genres=a&genres=b``),
 * not from comma-joined values, so serialize them that way.
 */
export const serializeParams = (params: Record<string, unknown>): string => {
	const query = new URLSearchParams();
	for (const [key, value] of Object.entries(params)) {
		if (value === undefined || value === null) continue;
		for (const item of Array.isArray(value) ? value : [value]) {
			query.append(key, String(item));
		}
	}
	return query.toString();
};

export const api = createApi({
	baseQuery: fetchBaseQuery({
		baseUrl: import.meta.env.VITE_API_URL ?? "/api",
		paramsSerializer: serializeParams,
	}),
	endpoints: (builder) => ({
		getLocality: builder.query<LocalityResponse, LocalityArgs>({
			query: (params) => ({ params, url: "locality/" }),
		}),
		search: builder.query<SearchResponse, SearchArgs>({
			query: (params) => ({ params, url: "search/" }),
		}),
	}),
	reducerPath: "api",
});

export const { useGetLocalityQuery, useSearchQuery } = api;
