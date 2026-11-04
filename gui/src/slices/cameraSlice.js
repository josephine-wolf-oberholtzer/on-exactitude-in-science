import { createSlice } from "@reduxjs/toolkit";

const cameraSlice = createSlice({
	name: "camera",
	initialState: {
		nonce: Date.now(),
	},
	reducers: {
		refocusCamera(state) {
			state.nonce = Date.now();
		},
	},
});
const { refocusCamera } = cameraSlice.actions;

export { refocusCamera };

export default cameraSlice.reducer;
