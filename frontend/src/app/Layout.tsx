import MenuIcon from "@mui/icons-material/Menu";
import AppBar from "@mui/material/AppBar";
import Container from "@mui/material/Container";
import Drawer from "@mui/material/Drawer";
import IconButton from "@mui/material/IconButton";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import { Link, Outlet } from "react-router";
import { toggleSidebar } from "../features/ui/uiSlice";
import { useAppDispatch, useAppSelector } from "./hooks";

export const Layout = () => {
	const dispatch = useAppDispatch();
	const sidebarOpen = useAppSelector((state) => state.ui.sidebarOpen);
	return (
		<>
			<AppBar position="static">
				<Toolbar>
					<IconButton
						aria-label="Toggle filters"
						color="inherit"
						edge="start"
						onClick={() => dispatch(toggleSidebar())}
					>
						<MenuIcon />
					</IconButton>
					<Typography
						color="inherit"
						component={Link}
						sx={{ ml: 1, textDecoration: "none" }}
						to="/"
						variant="h6"
					>
						On Exactitude in Science
					</Typography>
				</Toolbar>
			</AppBar>
			<Drawer
				onClose={() => dispatch(toggleSidebar())}
				open={sidebarOpen}
				slotProps={{ paper: { sx: { p: 2, width: 280 } } }}
			>
				<Typography variant="h6">Filters</Typography>
			</Drawer>
			<Container component="main" sx={{ py: 3 }}>
				<Outlet />
			</Container>
		</>
	);
};
