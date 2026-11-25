import { createSlice } from "@reduxjs/toolkit";

interface UiState {
	sidebarOpen: boolean;
}

const initialState: UiState = { sidebarOpen: false };

export const uiSlice = createSlice({
	initialState,
	name: "ui",
	reducers: {
		toggleSidebar: (state) => {
			state.sidebarOpen = !state.sidebarOpen;
		},
	},
});

export const { toggleSidebar } = uiSlice.actions;
