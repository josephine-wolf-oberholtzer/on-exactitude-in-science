import Backdrop from "@material-ui/core/Backdrop";
import CircularProgress from "@material-ui/core/CircularProgress";
import { makeStyles } from "@material-ui/core/styles";
import React from "react";
import { connect } from "react-redux";

const useStyles = makeStyles((theme) => ({
	backdrop: {
		zIndex: theme.zIndex.drawer + 1,
		color: "#fff",
	},
}));

const mapStateToProps = (state) => ({ loading: state.graph.loading });

const Loading = (props) => {
	const classes = useStyles();
	return (
		<div>
			<Backdrop className={classes.backdrop} open={props.loading}>
				<CircularProgress color="inherit" size={120} variant="indeterminate" />
			</Backdrop>
		</div>
	);
};

export default connect(mapStateToProps)(Loading);
