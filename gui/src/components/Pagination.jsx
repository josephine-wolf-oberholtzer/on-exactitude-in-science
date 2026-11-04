import { Box, ListItem } from "@material-ui/core";
import MUIPagination from "@material-ui/lab/Pagination";
import { push } from "connected-react-router";
import * as QueryString from "query-string";
import React from "react";
import { connect } from "react-redux";
import { useLocation } from "react-router-dom";
import { getPageCount } from "../selectors/graphSelector";
import { queryObjectToString, queryStringToObject } from "../utils";

const mapStateToProps = (state) => {
	return {
		page: state.filtered.page,
		pageCount: getPageCount(state),
	};
};

const mapDispatchToProps = (dispatch) => {
	return {
		pushPage: (location, page) => {
			const parsedQuery = queryStringToObject(location.search);
			if (page === 1) {
				delete parsedQuery.page;
			} else {
				parsedQuery.page = page;
			}
			dispatch(push(location.pathname + queryObjectToString(parsedQuery)));
		},
	};
};

const Pagination = (props) => {
	const location = useLocation();
	return (
		<React.Fragment>
			<ListItem>
				<Box
					display="flex"
					width="100%"
					alignItems="center"
					justifyContent="center"
					pt={1}
				>
					<MUIPagination
						count={props.pageCount}
						disabled={props.pageCount === 1}
						onChange={(event, value) => {
							props.pushPage(location, value);
						}}
						page={props.page <= props.pageCount ? props.page : props.pageCount}
					/>
				</Box>
			</ListItem>
		</React.Fragment>
	);
};

export default connect(mapStateToProps, mapDispatchToProps)(Pagination);
