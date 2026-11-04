import {
	Badge,
	Button,
	Chip,
	Collapse,
	Divider,
	IconButton,
	ListItem,
	ListItemIcon,
	ListItemText,
	makeStyles,
} from "@material-ui/core";
import CancelIcon from "@material-ui/icons/Cancel";
import ExpandLess from "@material-ui/icons/ExpandLess";
import ExpandMore from "@material-ui/icons/ExpandMore";
import FilterListIcon from "@material-ui/icons/FilterList";
import MoreIcon from "@material-ui/icons/More";
import StarRateIcon from "@material-ui/icons/StarRate";
import { push } from "connected-react-router";
import React from "react";
import { connect } from "react-redux";
import { useLocation } from "react-router-dom";
import { highlight, unhighlight } from "../slices/highlightedSlice";
import { toggleSidebarSection } from "../slices/layoutSlice";
import { queryObjectToString, queryStringToObject } from "../utils";

const useStyles = makeStyles((theme) => ({
	chips: {
		display: "flex",
		justifyContent: "left",
		flexWrap: "wrap",
		"& > *": {
			margin: theme.spacing(1),
		},
		marginTop: theme.spacing(2),
		marginBottom: theme.spacing(2),
		marginLeft: theme.spacing(1),
		marginRight: theme.spacing(1),
	},
}));

const mapDispatchToProps = (dispatch) => {
	return {
		clear: (location, category) => {
			dispatch(push(clearQuery(location, category)));
		},
		pushPin: (location, category, name) => {
			dispatch(push(pinQuery(location, category, name)));
		},
		pushUnpin: (location, category, name) => {
			dispatch(push(unpinQuery(location, category, name)));
		},
		toggleOpen: (category) => {
			dispatch(toggleSidebarSection({ category }));
		},
		toggleHighlight: (category, name, highlightedNames) => {
			if (highlightedNames.has(name)) {
				dispatch(unhighlight({ category, name }));
			} else {
				dispatch(highlight({ category, name }));
			}
		},
	};
};

const pinQuery = (location, category, name) => {
	const parsedQuery = queryStringToObject(location.search);
	const names = new Set(parsedQuery[category]);
	names.add(name);
	delete parsedQuery.page;
	parsedQuery[category] = Array.from(names).sort();
	return location.pathname + queryObjectToString(parsedQuery);
};

const unpinQuery = (location, category, name) => {
	const parsedQuery = queryStringToObject(location.search);
	const names = new Set(parsedQuery[category]);
	names.delete(name);
	delete parsedQuery.page;
	parsedQuery[category] = Array.from(names).sort();
	return location.pathname + queryObjectToString(parsedQuery);
};

const clearQuery = (location, category) => {
	const parsedQuery = queryStringToObject(location.search);
	parsedQuery[category] = [];
	delete parsedQuery.page;
	return location.pathname + queryObjectToString(parsedQuery);
};

const SidebarSection = (props) => {
	const { category, names, open, filteredNames, title } = props;
	const sortedNames = Array.from(Object.entries(props.names || {}));
	const highlightedNames = new Set(props.highlightedNames || []);
	const suggestedNames = new Set(props.suggestedNames || []);
	const location = useLocation();
	const classes = useStyles();
	const filteredChips = [];
	const unfilteredChips = [];
	const suggestionChips = [];
	if ((names || []).length > 0) {
		names.sort();
	}
	(filteredNames || []).forEach((name) => {
		const ids = names[name] || [];
		const chip = (
			<Badge badgeContent={ids.length} key={name}>
				<Chip
					color="primary"
					deleteIcon={<CancelIcon />}
					icon={suggestedNames.has(name) ? <StarRateIcon /> : null}
					label={name}
					onClick={() => {
						props.toggleHighlight(category, name, highlightedNames);
					}}
					onDelete={() => {
						props.pushUnpin(location, category, name);
					}}
					style={{
						boxShadow: highlightedNames.has(name)
							? "0px 0px 20px magenta"
							: null,
					}}
				/>
			</Badge>
		);
		filteredChips.push(chip);
	});
	(sortedNames || []).forEach((entry) => {
		const [name, ids] = entry;
		if (!filteredNames.includes(name)) {
			const chip = (
				<Badge badgeContent={ids.length > 0 ? ids.length : "?"} key={name}>
					<Chip
						deleteIcon={<FilterListIcon />}
						icon={suggestedNames.has(name) ? <StarRateIcon /> : null}
						label={name}
						onClick={() => {
							props.toggleHighlight(category, name, highlightedNames);
						}}
						onDelete={() => {
							props.pushPin(location, category, name);
						}}
						style={{
							boxShadow: highlightedNames.has(name)
								? "0px 0px 20px magenta"
								: null,
						}}
						variant="outlined"
					/>
				</Badge>
			);
			if (ids.length) {
				unfilteredChips.push(chip);
			} else {
				suggestionChips.push(chip);
			}
		}
	});
	return (
		<React.Fragment>
			<ListItem
				button
				key={title}
				onClick={() => {
					props.toggleOpen(category);
				}}
				style={{
					textDecoration:
						filteredChips.length > 0 ||
						unfilteredChips.length > 0 ||
						props.children
							? "none"
							: "line-through",
				}}
			>
				{(filteredChips.length > 0 || highlightedNames.size > 0) && (
					<ListItemIcon>
						<MoreIcon />
					</ListItemIcon>
				)}
				<ListItemText primary={title} />
				{open ? <ExpandLess /> : <ExpandMore />}
			</ListItem>
			<Collapse in={open} timeout="auto">
				{filteredChips.length > 0 && (
					<React.Fragment>
						<Divider />
						<div className={classes.chips}>
							{filteredChips}
							<Chip
								label="Clear Filters"
								onClick={() => {
									props.clear(location, category);
								}}
								variant="outlined"
							/>
						</div>
					</React.Fragment>
				)}
				{unfilteredChips.length > 0 && (
					<React.Fragment>
						<Divider />
						<div className={classes.chips}>{unfilteredChips}</div>
					</React.Fragment>
				)}
				{suggestionChips.length > 0 && (
					<React.Fragment>
						<Divider />
						<div className={classes.chips}>{suggestionChips}</div>
					</React.Fragment>
				)}
				{props.children && (
					<React.Fragment>
						<Divider />
						<div className={classes.chips}>{props.children}</div>
					</React.Fragment>
				)}
				<Divider />
			</Collapse>
		</React.Fragment>
	);
};

export default connect(null, mapDispatchToProps)(SidebarSection);
