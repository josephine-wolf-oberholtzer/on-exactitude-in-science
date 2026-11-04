import { useSnackbar } from "notistack";
import React from "react";
import { connect } from "react-redux";

const mapStateToProps = (state) => {
	return {
		error: state.graph.error,
	};
};

const ErrorMessage = (props) => {
	const { enqueueSnackbar } = useSnackbar();
	React.useEffect(() => {
		if (props.error !== null) {
			enqueueSnackbar(
				`Something went wrong / ${props.error.status} / ${props.error.reason}`,
				{
					anchorOrigin: {
						vertical: "bottom",
						horizontal: "center",
					},
					persist: true,
					variant: "error",
				},
			);
		}
	});
	return null;
};

export default connect(mapStateToProps)(ErrorMessage);
