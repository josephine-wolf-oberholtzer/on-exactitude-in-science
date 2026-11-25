import Alert from "@mui/material/Alert";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import TextField from "@mui/material/TextField";
import { useDeferredValue, useState } from "react";
import { Link } from "react-router";
import { useSearchQuery } from "../../api/api";

// The backend returns nothing for fewer characters than this
const MINIMUM_NAME_LENGTH = 3;

export const Search = () => {
	const [name, setName] = useState("");
	const deferredName = useDeferredValue(name.trim());
	const { data, error } = useSearchQuery(
		{ name: deferredName },
		{ skip: deferredName.length < MINIMUM_NAME_LENGTH },
	);
	return (
		<>
			<TextField
				autoFocus
				fullWidth
				label="Search for an artist, company, release…"
				onChange={(event) => setName(event.target.value)}
				value={name}
			/>
			{error && (
				<Alert severity="error" sx={{ mt: 2 }}>
					The search failed.
				</Alert>
			)}
			<List>
				{data?.results.map((result) => (
					<ListItemButton
						component={Link}
						key={`${result.label}-${result.id}-${result.index}`}
						to={`/${result.label}/${result.id}${result.index ? `?index=${result.index}` : ""}`}
					>
						<ListItemText
							primary={result.name}
							secondary={
								result.release_name
									? `${result.label} on ${result.release_name}`
									: result.label
							}
						/>
					</ListItemButton>
				))}
			</List>
		</>
	);
};
