import Typography from "@mui/material/Typography";
import type { RouteObject } from "react-router";
import { Locality } from "../features/locality/Locality";
import { Search } from "../features/search/Search";
import { Layout } from "./Layout";

export const routes: RouteObject[] = [
	{
		children: [
			{ element: <Search />, index: true },
			{ element: <Locality />, path: ":label/:eid" },
			{
				element: <Typography variant="h5">Page not found</Typography>,
				path: "*",
			},
		],
		element: <Layout />,
		path: "/",
	},
];
