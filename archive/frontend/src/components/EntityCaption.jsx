import { Box, Grid, Link, makeStyles, Typography } from "@material-ui/core";
import ArrowForwardIosIcon from "@material-ui/icons/ArrowForwardIos";
import SwapHorizIcon from "@material-ui/icons/SwapHoriz";
import React from "react";
import { connect } from "react-redux";
import { buildDiscogsURL } from "../utils";

const useStyles = makeStyles((theme) => ({
	caption: {
		position: "fixed",
		bottom: theme.spacing(2),
		right: theme.spacing(12),
	},
}));

const mapStateToProps = (state) => {
	return {
		selected: state.graph.selected,
	};
};

const roleCaptions = {
	credited_with: "credited with",
	member_of: "is a",
	subsidiary_of: "is a",
	subrelease_of: "is a",
};

const VertexCaption = (props) => {
	const { vertex } = props;
	const href = buildDiscogsURL(vertex.label, vertex.eid);
	return (
		<Grid item>
			<Typography variant="overline" display="block">
				{vertex.label}
				{vertex.year !== undefined ? ` (${vertex.year})` : ""}
			</Typography>
			<Typography variant="h5" display="block">
				<Link href={href} rel="noopener" target="_blank">
					{vertex.name}
				</Link>
			</Typography>
		</Grid>
	);
};

const EdgeCaption = (props) => {
	const { edge } = props;
	return (
		<Grid item>
			{roleCaptions[edge.label] !== undefined ? (
				<Typography variant="overline" display="block">
					{roleCaptions[edge.label]}
				</Typography>
			) : (
				<Typography variant="overline" display="block">
					&nbsp;
				</Typography>
			)}
			<Typography variant="h5" display="block">
				{edge.name}
			</Typography>
		</Grid>
	);
};

const EdgeIcon = (props) => {
	const { edge } = props;
	return (
		<Grid item>
			<Box px={1}>
				<Typography variant="overline" display="block">
					&nbsp;
				</Typography>
				{edge.name === "Alias Of" ? <SwapHorizIcon /> : <ArrowForwardIosIcon />}
			</Box>
		</Grid>
	);
};

const EntityCaption = (props) => {
	const classes = useStyles();
	const { selected } = props;
	if (selected === null) {
		return null;
	}
	switch (selected.kind) {
		case "vertex": {
			const { vertex } = selected;
			return (
				<div className={classes.caption}>
					<Grid container>
						<VertexCaption vertex={vertex} />
					</Grid>
				</div>
			);
		}
		case "edge": {
			const { edge, source, target } = selected;
			return (
				<div className={classes.caption}>
					<Grid container>
						<VertexCaption vertex={source} />
						<EdgeIcon edge={edge} />
						<EdgeCaption edge={edge} />
						<EdgeIcon edge={edge} />
						<VertexCaption vertex={target} />
					</Grid>
				</div>
			);
		}
		default:
			return null;
	}
};

export default connect(mapStateToProps, null)(EntityCaption);
