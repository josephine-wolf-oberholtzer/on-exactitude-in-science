import React from "react";
import { connect } from "react-redux";
import { COUNTRIES } from "../constants";
import { getVerticesByCountry } from "../selectors/graphSelector";
import SidebarSection from "./SidebarSection";

const mapStateToProps = (state) => {
	return {
		open: state.layout.sidebar.countriesOpen,
		highlightedNames: state.highlighted.countries,
		names: getVerticesByCountry(state),
		filteredNames: state.filtered.countries,
	};
};

const Countries = (props) => {
	return (
		<SidebarSection
			category={COUNTRIES}
			highlightedNames={props.highlightedNames}
			names={props.names}
			open={props.open}
			filteredNames={props.filteredNames}
			title="Countries"
		/>
	);
};

export default connect(mapStateToProps)(Countries);
