import { createSlice } from "@reduxjs/toolkit";

const layoutSlice = createSlice({
	name: "layout",
	initialState: {
		sidebar: {
			countriesOpen: false,
			formatsOpen: false,
			genresOpen: false,
			labelsOpen: false,
			open: false,
			rolesOpen: false,
			stylesOpen: false,
			yearsOpen: false,
		},
	},
	reducers: {
		toggleSidebar(state) {
			state.sidebar.open = !state.sidebar.open;
		},
		toggleSidebarSection(state, action) {
			const { category } = action.payload;
			state.sidebar[`${category}Open`] = !state.sidebar[`${category}Open`];
		},
	},
});

const { toggleSidebar, toggleSidebarSection } = layoutSlice.actions;

export { toggleSidebar, toggleSidebarSection };

export default layoutSlice.reducer;
