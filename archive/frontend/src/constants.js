const COUNTRIES = "countries";
const FORMATS = "formats";
const GENRES = "genres";
const LABELS = "labels";
const ROLES = "roles";
const STYLES = "styles";
const YEARS = "years";

const CATEGORIES = new Set([
	COUNTRIES,
	FORMATS,
	GENRES,
	LABELS,
	ROLES,
	STYLES,
	YEARS,
]);

const EDGE_LIMIT_DEFAULT = 250;
const EDGE_LIMIT_MINIMUM = 0;
const EDGE_LIMIT_MAXIMUM = 500;

export {
	CATEGORIES,
	COUNTRIES,
	EDGE_LIMIT_DEFAULT,
	EDGE_LIMIT_MAXIMUM,
	EDGE_LIMIT_MINIMUM,
	FORMATS,
	GENRES,
	LABELS,
	ROLES,
	STYLES,
	YEARS,
};
