import { createSlice } from "@reduxjs/toolkit";

const youtubeSlice = createSlice({
	name: "youtube",
	initialState: {
		index: 0,
		open: false,
		videos: [],
	},
	reducers: {
		selectYouTubeIndex(state, action) {
			state.index = action.payload;
		},
		closeYouTubeModal(state) {
			state.open = false;
		},
		openYouTubeModal(state, action) {
			state.index = 0;
			state.open = true;
			state.videos = action.payload || [];
		},
	},
});

const { selectYouTubeIndex, openYouTubeModal, closeYouTubeModal } =
	youtubeSlice.actions;

export { closeYouTubeModal, openYouTubeModal, selectYouTubeIndex };

export default youtubeSlice.reducer;
