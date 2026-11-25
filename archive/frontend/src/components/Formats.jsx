import React from "react";
import { connect } from "react-redux";
import { FORMATS } from "../constants";
import { getVerticesByFormat } from "../selectors/graphSelector";
import Operator from "./Operator";
import SidebarSection from "./SidebarSection";

const mapStateToProps = (state) => {
	return {
		open: state.layout.sidebar.formatsOpen,
		highlightedNames: state.highlighted.formats,
		names: getVerticesByFormat(state),
		filteredNames: state.filtered.formats,
		formatsOp: state.filtered.formatsOp,
	};
};

const Formats = (props) => {
	return (
		<SidebarSection
			category={FORMATS}
			highlightedNames={props.highlightedNames}
			names={props.names}
			open={props.open}
			filteredNames={props.filteredNames}
			title="Formats"
		>
			<Operator name="formatsOp" value={props.formatsOp} />
		</SidebarSection>
	);
};

export default connect(mapStateToProps)(Formats);
