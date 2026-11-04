import axios from "axios";

const urlBase = () => {
	if (process.env.NODE_ENV === "production") {
		return "https://api.on-exactitude-in.science";
	}
	return "http://localhost:9090";
};

const fetchLocalityByEntity = async (label, id, filters) => {
	const url = `${urlBase()}/locality/${label}/${id}`;
	const response = await axios.get(url, { params: filters || {} });
	return response;
};

const fetchLocalityByVertex = async (id, filters) => {
	const url = `${urlBase()}/locality/${id}`;
	const response = await axios.get(url, { params: filters || {} });
	return response;
};

const fetchRandomVertex = async (label) => {
	const url = `${urlBase()}/random${label !== undefined ? `/${label}` : ""}`;
	const response = await axios.get(url);
	return response;
};

const search = async (query, label) => {
	const labels = ["artist", "company", "master", "release", "track"];
	const url = labels.includes(label)
		? `${urlBase()}/search/${label}`
		: `${urlBase()}/search`;
	const response = axios.get(url, { params: { q: query } });
	return response;
};

export {
	fetchLocalityByEntity,
	fetchLocalityByVertex,
	fetchRandomVertex,
	search,
};
