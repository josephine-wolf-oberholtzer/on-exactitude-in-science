import { Divider, Drawer, List, makeStyles, Toolbar } from "@material-ui/core";
import React from "react";
import { connect } from "react-redux";
import Countries from "./Countries";
import Formats from "./Formats";
import Genres from "./Genres";
import GraphSize from "./GraphSize";
import Labels from "./Labels";
import Pagination from "./Pagination";
import Primacy from "./Primacy";
import Roles from "./Roles";
import Styles from "./Styles";
import Years from "./Years";

const drawerWidth = "420px";

const useStyles = makeStyles((theme) => ({
	drawer: {
		flexShrink: 0,
		width: drawerWidth,
	},
	drawerPaper: {
		backdropFilter: "blur(5px)",
		backgroundColor: "#00000080",
		width: drawerWidth,
	},
	drawerContainer: {
		overflow: "auto",
	},
}));

const mapStateToProps = (state) => {
	return {
		open: state.layout.sidebar.open,
	};
};

const Sidebar = (props) => {
	const classes = useStyles();
	return (
		<Drawer
			anchor="left"
			className={classes.drawer}
			classes={{ paper: classes.drawerPaper }}
			open={props.open}
			variant="persistent"
		>
			<Toolbar />
			<div className={classes.drawerContainer}>
				<List>
					<Countries />
					<Formats />
					<Genres />
					<Labels />
					<Roles />
					<Styles />
					<Years />
					<GraphSize />
					<Primacy />
					<Divider />
					<Pagination />
				</List>
			</div>
		</Drawer>
	);
};

export default connect(mapStateToProps)(Sidebar);
