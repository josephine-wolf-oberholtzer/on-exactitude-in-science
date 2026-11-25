import { createSlice } from "@reduxjs/toolkit";

const highlightedSlice = createSlice({
	name: "highlighted",
	initialState: {
		countries: [],
		formats: [],
		genres: [],
		labels: [],
		roles: [],
		styles: [],
		years: [],
	},
	reducers: {
		highlight(state, action) {
			const { category, name } = action.payload;
			const names = state[category];
			if (names !== undefined) {
				const index = names.indexOf(name);
				if (index === -1) {
					names.push(name);
					names.sort();
				}
			} else {
				throw new Error(`Bad category ${category}`);
			}
		},
		unhighlight(state, action) {
			const { category, name } = action.payload;
			const names = state[category];
			if (names !== undefined) {
				const index = names.indexOf(name);
				if (index !== -1) {
					names.splice(index, 1);
				}
			} else {
				throw new Error(`Bad category ${category}`);
			}
		},
	},
});

const { highlight, unhighlight } = highlightedSlice.actions;

export { highlight, unhighlight };

export default highlightedSlice.reducer;
