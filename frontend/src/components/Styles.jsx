import React from "react";
import { connect } from "react-redux";
import { STYLES } from "../constants";
import { getVerticesByStyle } from "../selectors/graphSelector";
import Operator from "./Operator";
import SidebarSection from "./SidebarSection";

const mapStateToProps = (state) => {
	return {
		open: state.layout.sidebar.stylesOpen,
		highlightedNames: state.highlighted.styles,
		names: getVerticesByStyle(state),
		filteredNames: state.filtered.styles,
		stylesOp: state.filtered.stylesOp,
	};
};

const Styles = (props) => {
	return (
		<SidebarSection
			category={STYLES}
			highlightedNames={props.highlightedNames}
			names={props.names}
			open={props.open}
			filteredNames={props.filteredNames}
			title="Styles"
		>
			<Operator name="stylesOp" value={props.stylesOp} />
		</SidebarSection>
	);
};

export default connect(mapStateToProps)(Styles);
