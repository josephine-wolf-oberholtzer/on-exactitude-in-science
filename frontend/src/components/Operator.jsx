import FormControl from "@material-ui/core/FormControl";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import Radio from "@material-ui/core/Radio";
import RadioGroup from "@material-ui/core/RadioGroup";
import { push } from "connected-react-router";
import React from "react";
import { connect } from "react-redux";
import { useLocation } from "react-router-dom";
import { queryObjectToString, queryStringToObject } from "../utils";

const setQuery = (location, name, value, defaultValue) => {
	const parsedQuery = queryStringToObject(location.search);
	parsedQuery[name] = value;
	return location.pathname + queryObjectToString(parsedQuery);
};

const mapDispatchToProps = (dispatch) => {
	return {
		set: (location, name, value, defaultValue) => {
			dispatch(push(setQuery(location, name, value, defaultValue)));
		},
	};
};

const Operator = (props) => {
	const { name, set, value } = props;
	const location = useLocation();
	const handleChange = (event) => {
		set(location, name, event.target.value, "or");
	};
	return (
		<FormControl component="fieldset">
			<RadioGroup row name={name} value={value || "or"} onChange={handleChange}>
				<FormControlLabel value="or" control={<Radio />} label="or" />
				<FormControlLabel value="and" control={<Radio />} label="and" />
			</RadioGroup>
		</FormControl>
	);
};

export default connect(null, mapDispatchToProps)(Operator);
