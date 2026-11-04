import * as QueryString from "query-string";
import { CATEGORIES } from "./constants";

const buildDiscogsURL = (label, eid) => {
	const discogsPrefix = "https://discogs.com";
	if (label === "track") {
		const releaseEid = eid.split("-")[0];
		return `${discogsPrefix}/release/${releaseEid}`;
	}
	if (label === "company") {
		return `${discogsPrefix}/label/${eid}`;
	}
	return `${discogsPrefix}/${label}/${eid}`;
};

const freezeEdge = (edge) => {
	const frozen = { ...edge };
	delete frozen.controlPosition;
	delete frozen.sourcePosition;
	delete frozen.targetPosition;
	return frozen;
};

const freezeVertex = (vertex) => {
	const frozen = { ...vertex };
	delete frozen.position;
	delete frozen.rudderPosition;
	return frozen;
};

const queryStringToObject = (queryString) => {
	const queryObject = {
		...QueryString.parse(queryString, { arrayFormat: "bracket" }),
	};
	Object.entries(queryObject).forEach((entry) => {
		const [key, value] = entry;
		if (typeof value === "string" && CATEGORIES.has(key)) {
			queryObject[key] = [value];
		}
	});
	return queryObject;
};

const queryObjectToString = (queryObject) => {
	const queryString = QueryString.stringify(queryObject, {
		arrayFormat: "bracket",
	})
		.replace(/%2B/g, "+")
		.replace(/%20/g, "+");
	return queryString.length > 0 ? `?${queryString}` : "";
};

function union(setA, setB) {
	const result = new Set(setA);
	setB.forEach((elem) => {
		result.add(elem);
	});
	return result;
}

export {
	buildDiscogsURL,
	freezeEdge,
	freezeVertex,
	queryObjectToString,
	queryStringToObject,
	union,
};
