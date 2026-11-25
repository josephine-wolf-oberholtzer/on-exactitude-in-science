import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider } from "@mui/material/styles";
import type { ReactNode } from "react";
import { Provider } from "react-redux";
import type { AppStore } from "./store";
import { theme } from "./theme";

export const Providers = ({
	children,
	store,
}: {
	children: ReactNode;
	store: AppStore;
}) => (
	<Provider store={store}>
		<ThemeProvider theme={theme}>
			<CssBaseline enableColorScheme />
			{children}
		</ThemeProvider>
	</Provider>
);
