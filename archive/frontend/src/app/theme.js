import { createMuiTheme } from "@material-ui/core";

const one = "#ffffff";
const two = "#223344";
const black = "#000";
const white = "#fff";

const theme = createMuiTheme({
	palette: {
		type: "dark",
		primary: {
			main: one,
			light: one,
			dark: one,
			contrastText: black,
		},
		secondary: {
			main: two,
			light: two,
			dark: two,
			contrastText: white,
		},
	},
});

export { theme };
