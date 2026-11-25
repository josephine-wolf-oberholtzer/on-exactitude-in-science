import Dialog from "@material-ui/core/Dialog";
import DialogContent from "@material-ui/core/DialogContent";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import { makeStyles } from "@material-ui/core/styles";
import React from "react";
import { connect } from "react-redux";
import { closeYouTubeModal, selectYouTubeIndex } from "../slices/youtubeSlice";

const useStyles = makeStyles((theme) => ({
	list: {
		height: 150,
	},
	video: {
		height: 315 + theme.spacing(5),
		width: 560 + theme.spacing(5),
	},
}));

const mapStateToProps = (state) => {
	return {
		selectedIndex: state.youtube.index,
		open: state.youtube.open,
		videos: state.youtube.videos || [],
	};
};

const mapDispatchToProps = (dispatch) => {
	return {
		closeYouTubeModal: () => dispatch(closeYouTubeModal()),
		selectYouTubeIndex: (index) => dispatch(selectYouTubeIndex(index)),
	};
};

function getId(url) {
	const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
	const match = url.match(regExp);
	return match && match[2].length === 11 ? match[2] : null;
}

const YouTubeModal = (props) => {
	const classes = useStyles();
	const { selectedIndex, open, videos } = props;
	return (
		<Dialog
			onClose={() => {
				props.closeYouTubeModal();
			}}
			open={props.open}
		>
			<DialogContent className={classes.video}>
				{videos.length > 0 && (
					<iframe
						allowFullScreen
						title={videos[selectedIndex].title}
						frameBorder={0}
						height={315}
						width={560}
						src={"//www.youtube.com/embed/" + getId(videos[selectedIndex].url)}
					/>
				)}
			</DialogContent>
			<DialogContent className={classes.list}>
				<List>
					{videos.map((video, index) => (
						<ListItem
							button
							onClick={() => props.selectYouTubeIndex(index)}
							key={video.url}
							selected={index === selectedIndex}
						>
							{video.title}
						</ListItem>
					))}
				</List>
			</DialogContent>
		</Dialog>
	);
};

export default connect(mapStateToProps, mapDispatchToProps)(YouTubeModal);
