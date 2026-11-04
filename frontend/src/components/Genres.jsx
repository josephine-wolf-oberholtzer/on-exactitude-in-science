import React from "react";
import { connect } from "react-redux";
import { GENRES } from "../constants";
import { getVerticesByGenre } from "../selectors/graphSelector";
import SidebarSection from "./SidebarSection";

const mapStateToProps = (state) => {
	return {
		open: state.layout.sidebar.genresOpen,
		highlightedNames: state.highlighted.genres,
		names: getVerticesByGenre(state),
		filteredNames: state.filtered.genres,
	};
};

const Genres = (props) => {
	return (
		<SidebarSection
			category={GENRES}
			highlightedNames={props.highlightedNames}
			names={props.names}
			open={props.open}
			filteredNames={props.filteredNames}
			title="Genres"
		/>
	);
};

export default connect(mapStateToProps)(Genres);
