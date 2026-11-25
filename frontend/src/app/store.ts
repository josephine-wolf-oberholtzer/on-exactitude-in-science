import { combineReducers, configureStore } from "@reduxjs/toolkit";
import { api } from "../api/api";
import { uiSlice } from "../features/ui/uiSlice";

const rootReducer = combineReducers({
	[api.reducerPath]: api.reducer,
	[uiSlice.name]: uiSlice.reducer,
});

export type RootState = ReturnType<typeof rootReducer>;

/**
 * Build a store. A factory, rather than a singleton, so that tests can have
 * a fresh one each.
 */
export const setupStore = (preloadedState?: Partial<RootState>) =>
	configureStore({
		middleware: (getDefaultMiddleware) =>
			getDefaultMiddleware().concat(api.middleware),
		preloadedState,
		reducer: rootReducer,
	});

export type AppStore = ReturnType<typeof setupStore>;
export type AppDispatch = AppStore["dispatch"];
