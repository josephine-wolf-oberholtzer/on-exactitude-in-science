import GoogleAnalytics, {
	trackEvent,
	trackPageView,
} from "@redux-beacon/google-analytics";
import logger from "@redux-beacon/logger";
import { configureStore, getDefaultMiddleware } from "@reduxjs/toolkit";
import {
	connectRouter,
	LOCATION_CHANGE,
	routerMiddleware,
} from "connected-react-router";
import { createBrowserHistory } from "history";
import { combineReducers } from "redux";
import { createMiddleware } from "redux-beacon";
import {
	FLUSH,
	PAUSE,
	PERSIST,
	PURGE,
	persistReducer,
	persistStore,
	REGISTER,
	REHYDRATE,
} from "redux-persist";

import storage from "redux-persist/lib/storage";

import cameraReducer from "../slices/cameraSlice";
import filteredReducer from "../slices/filteredSlice";
import graphReducer from "../slices/graphSlice";
import highlightedReducer from "../slices/highlightedSlice";
import layoutReducer from "../slices/layoutSlice";
import youtubeReducer from "../slices/youtubeSlice";

const history = createBrowserHistory();

const rootReducer = combineReducers({
	camera: cameraReducer,
	graph: graphReducer,
	highlighted: highlightedReducer,
	layout: layoutReducer,
	filtered: filteredReducer,
	youtube: youtubeReducer,
	router: connectRouter(history),
});

const persistConfig = {
	key: "root",
	whitelist: ["layout"],
	storage,
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

const gaMiddleware = createMiddleware(
	{
		[LOCATION_CHANGE]: trackPageView((action) => ({
			page: action.payload.location.pathname,
		})),
		"graph/selectEntity": trackEvent((action) => ({
			category: "interaction",
			action: "selected",
			label: action.payload.label,
			value: action.payload.eid,
		})),
		"graph/deselectEntity": trackEvent(() => ({
			category: "interaction",
			action: "deselected",
		})),
	},
	GoogleAnalytics(),
	{ logger },
);

const store = configureStore({
	reducer: persistedReducer,
	middleware: getDefaultMiddleware({
		serializableCheck: {
			ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
		},
	})
		.concat(routerMiddleware(history))
		.concat(gaMiddleware),
	devTools: process.env.NODE_ENV !== "production",
});

const persistor = persistStore(store);

export { history, persistor };

export default store;
