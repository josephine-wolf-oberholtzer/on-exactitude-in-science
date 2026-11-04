import React from "react";
import { connect } from "react-redux";
import { YEARS } from "../constants";
import { getVerticesByYear } from "../selectors/graphSelector";
import SidebarSection from "./SidebarSection";

const mapStateToProps = (state) => {
	return {
		open: state.layout.sidebar.yearsOpen,
		highlightedNames: state.highlighted.years,
		names: getVerticesByYear(state),
		filteredNames: state.filtered.years,
	};
};

const Years = (props) => {
	return (
		<SidebarSection
			category={YEARS}
			highlightedNames={props.highlightedNames}
			names={props.names}
			open={props.open}
			filteredNames={props.filteredNames}
			title="Years"
		/>
	);
};

export default connect(mapStateToProps)(Years);
