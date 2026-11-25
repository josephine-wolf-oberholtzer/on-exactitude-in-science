import * as QueryString from "query-string";
import React from "react";
import { connect } from "react-redux";
import { setFiltered } from "../slices/filteredSlice";
import { fetchByEntity, fetchRandom } from "../slices/graphSlice";
import { queryStringToObject } from "../utils";

const mapDispatchToProps = (dispatch) => {
	return {
		fetchByEntity: (label, id, filters) =>
			dispatch(fetchByEntity({ label, id, filters })),
		fetchRandom: (location, label) =>
			dispatch(fetchRandom({ label, location })),
		setFiltered: (pins) => dispatch(setFiltered(pins)),
	};
};

class Fetcher extends React.Component {
	match() {
		const { label, id } = this.props.match.params;
		const { location } = this.props;
		const filters = queryStringToObject(location.search);
		this.props.setFiltered(filters);
		switch (this.props.match.path) {
			case "/":
				document.title = "Home | On Exactitude In Science";
				break;
			case "/random/:label(artist|company|master|release|track)":
				document.title = "Random | On Exactitude In Science";
				this.props.fetchRandom(location, label);
				break;
			case "/random":
				document.title = "Random | On Exactitude In Science";
				this.props.fetchRandom(location);
				break;
			case "/:label(artist|company|master|release|track)/:id":
				this.props.fetchByEntity(label, id, filters);
				break;
			default:
				document.title = "404 | On Exactitude In Science";
				break;
		}
	}

	componentDidMount() {
		this.match();
	}

	componentDidUpdate() {
		this.match();
	}

	render() {
		return null;
	}
}

export default connect(null, mapDispatchToProps)(Fetcher);
