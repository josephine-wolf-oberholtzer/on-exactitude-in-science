import React from "react";
import { connect } from "react-redux";
import { LABELS } from "../constants";
import { getVerticesByLabel } from "../selectors/graphSelector";
import SidebarSection from "./SidebarSection";

const mapStateToProps = (state) => {
	return {
		open: state.layout.sidebar.labelsOpen,
		highlightedNames: state.highlighted.labels,
		names: getVerticesByLabel(state),
		filteredNames: state.filtered.labels,
	};
};

const Labels = (props) => {
	return (
		<SidebarSection
			category={LABELS}
			highlightedNames={props.highlightedNames}
			names={props.names}
			open={props.open}
			filteredNames={props.filteredNames}
			title="Labels"
		/>
	);
};

export default connect(mapStateToProps)(Labels);
