import ForceGraph from "./ForceGraph";

const forceGraph = new ForceGraph();

forceGraph.on("graphRebuild", (data) => {
	// eslint-disable-next-line no-restricted-globals
	self.postMessage(["graphRebuild", data]);
});

forceGraph.on("graphTick", (data) => {
	// eslint-disable-next-line no-restricted-globals
	self.postMessage(["graphTick", data]);
});

// eslint-disable-next-line no-restricted-globals
self.onmessage = (e) => {
	const [message, data] = e.data;
	switch (message) {
		case "pin":
			forceGraph.pin(data.nodeID, data.x, data.y, data.z);
			break;
		case "reheat":
			forceGraph.reheat();
			break;
		case "tick":
			// Only tick if request is less than 30 ms old
			if (Date.now() - data < 30) {
				forceGraph.tick();
			}
			break;
		case "unpin":
			forceGraph.unpin(data.nodeID);
			break;
		case "update":
			forceGraph.update(data.vertices, data.edges);
			break;
		default:
			break;
	}
};
