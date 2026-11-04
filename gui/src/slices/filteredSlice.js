import { createSlice } from "@reduxjs/toolkit";
import {
	CATEGORIES,
	EDGE_LIMIT_DEFAULT,
	EDGE_LIMIT_MAXIMUM,
	EDGE_LIMIT_MINIMUM,
} from "../constants";

const filteredSlice = createSlice({
	name: "filtered",
	initialState: {
		limit: 250,
		page: 1,
		showSecondaryReleases: false,
		countries: [],
		formats: [],
		formatsOp: "or",
		genres: [],
		labels: [],
		roles: [],
		styles: [],
		stylesOp: "or",
		years: [],
	},
	reducers: {
		setFiltered(state, action) {
			CATEGORIES.forEach((category) => {
				const names = new Set(action.payload[category] || []);
				state[category] = Array.from(names).sort();
			});
			state.formatsOp = action.payload.formatsOp || "or";
			state.stylesOp = action.payload.stylesOp || "or";
			state.page = parseInt(action.payload.page, 10) || 1;
			if (state.page < 1) {
				state.page = 1;
			}
			state.limit = parseInt(action.payload.limit, 10) || EDGE_LIMIT_DEFAULT;
			if (state.limit < EDGE_LIMIT_MINIMUM) {
				state.limit = EDGE_LIMIT_MINIMUM;
			}
			if (state.limit > EDGE_LIMIT_MAXIMUM) {
				state.limit = EDGE_LIMIT_MAXIMUM;
			}
			state.showSecondaryReleases = action.payload.secondary === "true";
		},
	},
});

const { setFiltered } = filteredSlice.actions;

export { setFiltered };

export default filteredSlice.reducer;
