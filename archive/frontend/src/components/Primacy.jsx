import { ListItem, ListItemText } from "@material-ui/core";
import CheckBoxIcon from "@material-ui/icons/CheckBox";
import CheckBoxOutlineBlankIcon from "@material-ui/icons/CheckBoxOutlineBlank";
import { push } from "connected-react-router";
import React from "react";
import { connect } from "react-redux";
import { useLocation } from "react-router-dom";
import { queryObjectToString, queryStringToObject } from "../utils";

const mapStateToProps = (state) => {
	return {
		checked: state.filtered.showSecondaryReleases,
	};
};

const mapDispatchToProps = (dispatch) => {
	return {
		pushChecked: (location, checked) => {
			const parsedQuery = queryStringToObject(location.search);
			if (checked) {
				parsedQuery.secondary = true;
			} else {
				delete parsedQuery.secondary;
			}
			dispatch(push(location.pathname + queryObjectToString(parsedQuery)));
		},
	};
};

const Primacy = (props) => {
	const location = useLocation();
	return (
		<ListItem
			button
			onClick={() => {
				props.pushChecked(location, !props.checked);
			}}
		>
			<ListItemText primary="Show Secondary Releases" />
			{props.checked ? <CheckBoxIcon /> : <CheckBoxOutlineBlankIcon />}
		</ListItem>
	);
};

export default connect(mapStateToProps, mapDispatchToProps)(Primacy);
