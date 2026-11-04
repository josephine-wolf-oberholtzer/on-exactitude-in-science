import {
	Button,
	FormControl,
	Grid,
	InputLabel,
	MenuItem,
	makeStyles,
	Select,
	TextField,
	Typography,
} from "@material-ui/core";
import CircularProgress from "@material-ui/core/CircularProgress";
import ShuffleRoundedIcon from "@material-ui/icons/ShuffleRounded";
import Autocomplete from "@material-ui/lab/Autocomplete";
import { push } from "connected-react-router";
import React from "react";
import { connect } from "react-redux";
import * as graphAPI from "../api/graphAPI";
import { queryObjectToString, queryStringToObject } from "../utils";

const useDebounce = (value, delay) => {
	const [debouncedValue, setDebouncedValue] = React.useState(value);
	React.useEffect(() => {
		const handler = setTimeout(() => {
			setDebouncedValue(value);
		}, delay);
		return () => {
			clearTimeout(handler);
		};
	}, [value, delay]);
	return debouncedValue;
};

const useStyles = makeStyles((theme) => ({
	autocomplete: { marginRight: theme.spacing(2) },
	menuButton: { marginRight: theme.spacing(2) },
}));

const mapDispatchToProps = (dispatch) => {
	return {
		pushEntity: (label, id) => {
			const parsedQuery = queryStringToObject(location.search);
			const baseUrl = `/${label}/${id}`;
			delete parsedQuery.page;
			dispatch(push(baseUrl + queryObjectToString(parsedQuery)));
		},
		pushRandom: (label) => {
			const parsedQuery = queryStringToObject(location.search);
			const baseUrl = label === "any" ? "/random" : `/random/${label}`;
			delete parsedQuery.page;
			dispatch(push(baseUrl + queryObjectToString(parsedQuery)));
		},
	};
};

const EntitySearch = (props) => {
	const classes = useStyles();
	const [value, setValue] = React.useState(null);
	const [inputValue, setInputValue] = React.useState("");
	const [options, setOptions] = React.useState([]);
	const [entityType, setEntityType] = React.useState("any");
	const [loading, setLoading] = React.useState(false);
	const debouncedInputValue = useDebounce(inputValue, 200);

	React.useEffect(() => {
		if (debouncedInputValue.length >= 3) {
			const historicInputValue = debouncedInputValue;
			setLoading(true);
			graphAPI
				.search(debouncedInputValue, entityType)
				.then((response) => {
					if (debouncedInputValue === historicInputValue) {
						const newOptions = [];
						if (response.data.result) {
							newOptions.push(...newOptions, ...response.data.result);
						}
						setLoading(false);
						setOptions(newOptions);
					}
				})
				.catch((error) => {
					if (debouncedInputValue === historicInputValue) {
						setLoading(false);
					}
				});
		} else {
			setOptions([]);
		}
	}, [debouncedInputValue, entityType]);

	return (
		<React.Fragment>
			<Button
				className={classes.menuButton}
				onClick={() => props.pushRandom(entityType)}
				startIcon={<ShuffleRoundedIcon />}
			>
				Random
			</Button>
			<Autocomplete
				blurOnSelect
				className={classes.autocomplete}
				clearOnBlur
				clearOnEscape
				clearText=""
				selectOnFocus
				filterSelectedOptions
				filterOptions={(x) => x}
				getOptionLabel={(option) => option.name}
				getOptionSelected={(option, value) => option.id === value.id}
				noOptionsText='Start searching... e.g. "bjork"'
				onInputChange={(event, newInputValue) => {
					setInputValue(newInputValue);
				}}
				onChange={(event, newValue) => {
					if (newValue !== null) {
						props.pushEntity(newValue.label, newValue.eid);
					}
					setOptions([]);
					setValue(null);
					setInputValue("");
				}}
				options={options}
				renderInput={(params) => (
					<TextField
						{...params}
						label="Search"
						size="small"
						variant="outlined"
						fullWidth
						InputProps={{
							...params.InputProps,
							endAdornment: (
								<React.Fragment>
									{params.InputProps.endAdornment}
									{loading ? (
										<CircularProgress color="inherit" size={20} />
									) : null}
								</React.Fragment>
							),
						}}
					/>
				)}
				renderOption={(option) => (
					<Grid container>
						<Grid container item justify="space-between">
							<Grid item>{option.name}</Grid>
							<Grid item>
								<Typography variant="body2" color="textSecondary">
									{option.label}
								</Typography>
							</Grid>
						</Grid>
						{option.label === "release" && (
							<Grid container item justify="space-between">
								<Grid item>
									<Typography variant="body2" color="textSecondary">
										({option.year !== undefined ? option.year : "unknown"})
									</Typography>
								</Grid>
							</Grid>
						)}
						{option.label === "track" && (
							<Grid container item justify="space-between">
								<Grid item>
									<Typography variant="body2" color="textSecondary">
										({option.year !== undefined ? option.year : "unknown"}){" "}
										{option.release_name}
									</Typography>
								</Grid>
							</Grid>
						)}
					</Grid>
				)}
				style={{ width: 400 }}
				value={value}
			/>
			<TextField
				id="entity-search-select"
				label="Type"
				onChange={(event, newValue) => {
					setEntityType(event.target.value);
					setOptions([]);
					setValue(null);
					setInputValue("");
				}}
				select
				size="small"
				style={{ width: 120 }}
				value={entityType}
				variant="outlined"
			>
				<MenuItem value={"any"}>Any</MenuItem>
				<MenuItem value={"artist"}>Artist</MenuItem>
				<MenuItem value={"company"}>Company</MenuItem>
				<MenuItem value={"master"}>Master</MenuItem>
				<MenuItem value={"release"}>Release</MenuItem>
				<MenuItem value={"track"}>Track</MenuItem>
			</TextField>
		</React.Fragment>
	);
};

export default connect(null, mapDispatchToProps)(EntitySearch);
