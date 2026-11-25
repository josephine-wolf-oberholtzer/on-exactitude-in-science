import Alert from "@mui/material/Alert";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Pagination from "@mui/material/Pagination";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useParams, useSearchParams } from "react-router";
import {
	useGetLocalityQuery,
	VERTEX_LABEL_NAMES,
	type VertexLabelName,
} from "../../api/api";

const isLabel = (value: string | undefined): value is VertexLabelName =>
	VERTEX_LABEL_NAMES.includes(value as VertexLabelName);

export const Locality = () => {
	const { eid, label } = useParams();
	const [searchParams, setSearchParams] = useSearchParams();
	const page = Number(searchParams.get("page") ?? 1) || 1;
	const index = Number(searchParams.get("index") ?? 0) || 0;
	const valid = isLabel(label) && Number.isInteger(Number(eid));
	const { data, error, isFetching } = useGetLocalityQuery(
		{ eid: Number(eid), index, label: label as VertexLabelName, page },
		{ skip: !valid },
	);
	if (!valid) {
		return <Alert severity="error">Not a valid entity.</Alert>;
	}
	if (error) {
		return <Alert severity="error">Could not load this entity.</Alert>;
	}
	if (!data) {
		return <CircularProgress aria-label="Loading" />;
	}
	const center = data.vertices.find((vertex) => vertex.id === data.id);
	const { page_count, total } = data.pagination;
	return (
		<Stack spacing={2}>
			<Typography component="h1" variant="h4">
				{center?.name}
			</Typography>
			<Typography color="text.secondary">
				{total} neighbors · {data.vertices.length} vertices ·{" "}
				{data.edges.length} edges
				{isFetching && " · loading…"}
			</Typography>
			{page_count > 1 && (
				<Pagination
					count={page_count}
					onChange={(_, value) =>
						setSearchParams((previous) => {
							previous.set("page", String(value));
							return previous;
						})
					}
					page={page}
				/>
			)}
			<List>
				{data.vertices.map((vertex) => (
					<ListItem key={vertex.id}>
						<ListItemText primary={vertex.name} secondary={vertex.label} />
						{vertex.child_count ? (
							<Chip label={`${vertex.child_count} children`} size="small" />
						) : null}
					</ListItem>
				))}
			</List>
		</Stack>
	);
};
