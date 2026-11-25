import {
	AppBar,
	IconButton,
	makeStyles,
	Toolbar,
	Typography,
} from "@material-ui/core";
import MenuOpenRoundedIcon from "@material-ui/icons/MenuOpenRounded";
import MenuRoundedIcon from "@material-ui/icons/MenuRounded";
import { push } from "connected-react-router";
import React from "react";
import { connect } from "react-redux";
import EntitySearch from "../components/EntitySearch";
import { toggleSidebar } from "../slices/layoutSlice";

const useStyles = makeStyles((theme) => ({
	appBar: {
		backdropFilter: "blur(5px)",
		backgroundColor: "#00000080",
		borderBottomColor: "#ffffff20",
		borderBottomStyle: "solid",
		borderBottomWidth: "1px",
		zIndex: theme.zIndex.drawer + 1,
	},
	menuButton: {
		marginRight: theme.spacing(2),
	},
	title: {
		flexGrow: 1,
	},
}));

const mapDispatchToProps = (dispatch) => {
	return {
		push: (path) => dispatch(push(path)),
		toggleSidebar: () => dispatch(toggleSidebar()),
	};
};

const mapStateToProps = (state) => {
	return {
		open: state.layout.sidebar.open,
	};
};

const Header = (props) => {
	const classes = useStyles();
	return (
		<AppBar position="fixed" className={classes.appBar}>
			<Toolbar>
				<IconButton
					aria-label="menu"
					className={classes.menuButton}
					color="primary"
					edge="start"
					onClick={props.toggleSidebar}
				>
					{props.open ? <MenuOpenRoundedIcon /> : <MenuRoundedIcon />}
				</IconButton>
				<Typography
					className={classes.title}
					color="primary"
					onClick={() => props.push("/")}
					variant="h6"
				>
					On Exactitude In Science
				</Typography>
				<EntitySearch />
			</Toolbar>
		</AppBar>
	);
};

export default connect(mapStateToProps, mapDispatchToProps)(Header);
