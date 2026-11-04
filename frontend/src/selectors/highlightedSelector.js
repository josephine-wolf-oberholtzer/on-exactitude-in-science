import { createSelector } from "@reduxjs/toolkit";
import {
	getEdgesByRole,
	getVerticesByCountry,
	getVerticesByFormat,
	getVerticesByGenre,
	getVerticesByLabel,
	getVerticesByStyle,
	getVerticesByYear,
} from "./graphSelector";

const getHighlightedRoles = (state) => state.highlighted.roles;

const getHighlightedCountries = (state) => state.highlighted.countries;

const getHighlightedFormats = (state) => state.highlighted.formats;

const getHighlightedGenres = (state) => state.highlighted.genres;

const getHighlightedLabels = (state) => state.highlighted.labels;

const getHighlightedStyles = (state) => state.highlighted.styles;

const getHighlightedYears = (state) => state.highlighted.years;

const highlightObjects = (pairs) => {
	const result = new Set();
	pairs.forEach((pair) => {
		const [labels, objectIdsByLabel] = pair;
		labels.forEach((label) => {
			(objectIdsByLabel[label] || []).forEach((objectId) => {
				result.add(objectId);
			});
		});
	});
	return result;
};

export const getHighlightedEdges = createSelector(
	[getHighlightedRoles, getEdgesByRole],
	(highlightedRoles, edgesByRole) => {
		const pairs = [[highlightedRoles, edgesByRole]];
		return highlightObjects(pairs);
	},
);

export const getHighlightedVertices = createSelector(
	[
		getHighlightedCountries,
		getHighlightedFormats,
		getHighlightedGenres,
		getHighlightedLabels,
		getHighlightedStyles,
		getHighlightedYears,
		getVerticesByCountry,
		getVerticesByFormat,
		getVerticesByGenre,
		getVerticesByLabel,
		getVerticesByStyle,
		getVerticesByYear,
	],
	(
		highlightedCountries,
		highlightedFormats,
		highlightedGenres,
		highlightedLabels,
		highlightedStyles,
		highlightedYears,
		verticesByCountry,
		verticesByFormat,
		verticesByGenre,
		verticesByLabel,
		verticesByStyle,
		verticesByYear,
	) => {
		const pairs = [
			[highlightedCountries, verticesByCountry],
			[highlightedFormats, verticesByFormat],
			[highlightedGenres, verticesByGenre],
			[highlightedLabels, verticesByLabel],
			[highlightedStyles, verticesByStyle],
			[highlightedYears, verticesByYear],
		];
		return highlightObjects(pairs);
	},
);
