import { dispatch } from "d3-dispatch";
import Worker from "./ForceGraph.worker";

class ForceGraphProxy {
	constructor() {
		this.dispatcher = dispatch("graphRebuild", "graphTick");
		this.worker = new Worker();
		this.worker.onmessage = (e) => {
			const [message, data] = e.data;
			switch (message) {
				case "graphRebuild":
					this.dispatcher.call("graphRebuild", data, data);
					break;
				case "graphTick":
					this.dispatcher.call("graphTick", data, data);
					break;
				default:
					break;
			}
		};
	}

	on(name, _) {
		if (arguments.length > 1) {
			this.dispatcher.on(name, _);
			return this;
		}
		return this.dispatcher.on(name);
	}

	pin(nodeID, x, y, z) {
		this.worker.postMessage([
			"pin",
			{
				nodeID,
				x,
				y,
				z,
			},
		]);
	}

	reheat() {
		this.worker.postMessage(["reheat"]);
	}

	tick() {
		this.worker.postMessage(["tick", Date.now()]);
	}

	update(vertices, edges) {
		this.worker.postMessage(["update", { vertices, edges }]);
	}

	unpin(nodeID) {
		this.worker.postMessage(["unpin", { nodeID }]);
	}
}

export default ForceGraphProxy;
