import { dispatch } from "d3-dispatch";
import * as d3force3d from "d3-force-3d";
import { Vector3 } from "three";
import forceManyBodyNaive from "./forceManyBodyNaive";

// import forceManyBodyGPU from './forceManyBodyGPU';

class ForceGraph {
	constructor() {
		this.dispatcher = dispatch("graphRebuild", "graphTick");
		this.edgeMap = new Map();
		this.linkMap = new Map();
		this.nodeMap = new Map();
		this.vertexMap = new Map();
		this.simulation = d3force3d
			.forceSimulation()
			.stop()
			.alpha(1)
			.numDimensions(3)
			.alphaDecay(0.01)
			.velocityDecay(0.5)
			// .force('charge', d3force3d.forceManyBody()
			// .force('charge', forceManyBodyGPU()
			.force(
				"charge",
				forceManyBodyNaive()
					.distanceMax(250)
					.distanceMin(1)
					.strength((d) => {
						if (d.type === "edge") {
							return -0.5;
						}
						if (d.type === "rudder") {
							return -1.0;
						}
						return -3.0;
					}),
			)
			.force(
				"links",
				d3force3d
					.forceLink()
					.id((d) => d.id)
					.distance((d) => (d.source.radius || 1) + (d.target.radius || 1))
					.iterations(3),
			)
			.force(
				"x",
				d3force3d.forceX().strength((d) => (d.type === "rudder" ? 0.0 : 0.1)),
			)
			.force(
				"y",
				d3force3d.forceY().strength((d) => (d.type === "rudder" ? 0.0 : 0.1)),
			)
			.force(
				"z",
				d3force3d.forceZ().strength((d) => (d.type === "rudder" ? 0.0 : 0.1)),
			)
			.force("centering", d3force3d.forceCenter());
	}

	on(name, _) {
		if (arguments.length > 1) {
			this.dispatcher.on(name, _);
			return this;
		}
		return this.dispatcher.on(name);
	}

	pin(nodeID, x, y, z) {
		// console.log('pin', nodeID, x, y, z);
		const node = this.nodeMap.get(nodeID);
		if (node) {
			node.fx = x;
			node.fy = y;
			node.fz = z;
		}
	}

	reheat() {
		return this.simulation.alpha(1.0);
	}

	tick() {
		if (this.simulation.alpha() >= this.simulation.alphaMin()) {
			this.simulation.tick();
			ForceGraph.updateVertexAndEdgePositions(
				this.vertexMap,
				this.edgeMap,
				this.nodeMap,
			);
			const result = {
				vertices: Array.from(this.vertexMap.values()),
				edges: Array.from(this.edgeMap.values()),
			};
			this.dispatcher.call("graphTick", result, result);
		}
	}

	update(vertices, edges) {
		const { newVertexMap, newEdgeMap } = ForceGraph.buildVertexAndEdgeMaps(
			vertices,
			edges,
		);
		const { newNodeMap, newLinkMap } = ForceGraph.buildNewNodeAndLinkMaps(
			newVertexMap,
			newEdgeMap,
		);
		ForceGraph.updateOldNodeAndLinkMaps(
			newNodeMap,
			this.nodeMap,
			newLinkMap,
			this.linkMap,
		);
		ForceGraph.updateSimulation(this.simulation, this.nodeMap, this.linkMap);
		const result = ForceGraph.updateOldVertexAndEdgeMaps(
			newVertexMap,
			this.vertexMap,
			newEdgeMap,
			this.edgeMap,
		);
		ForceGraph.updateVertexAndEdgePositions(
			this.vertexMap,
			this.edgeMap,
			this.nodeMap,
		);
		this.dispatcher.call("graphRebuild", result, result);
	}

	unpin(nodeID) {
		// console.log('unpin', nodeID);
		const node = this.nodeMap.get(nodeID);
		if (node) {
			node.fx = null;
			node.fy = null;
			node.fz = null;
		}
	}

	static edgeRequiresBezier(edge) {
		return edge.label !== "alias_of";
	}

	static buildVertexAndEdgeMaps(newVertices, newEdges) {
		const newVertexMap = new Map(
			newVertices.map((vertex) => {
				const extra = {
					position: new Vector3(),
					radius: (vertex.child_count + 1) ** 0.5,
					rudderPosition: new Vector3(),
				};
				return [vertex.id, { ...vertex, ...extra }];
			}),
		);
		const newEdgeMap = new Map(
			newEdges.map((edge) => {
				const extra = {
					sourcePosition: new Vector3(),
					targetPosition: new Vector3(),
				};
				if (ForceGraph.edgeRequiresBezier(edge)) {
					extra.controlPosition = new Vector3();
				}
				return [edge.id, { ...edge, ...extra }];
			}),
		);
		return { newVertexMap, newEdgeMap };
	}

	static buildNewNodeAndLinkMaps(newVertexMap, newEdgeMap) {
		const newNodeMap = new Map();
		const newLinkMap = new Map();
		newVertexMap.forEach((vertex) => {
			const rudderId = `${vertex.id}-rudder`;
			const node = {
				...vertex,
				radius: Math.sqrt(vertex.child_count + 1),
				type: "vertex",
			};
			const rudderNode = { ...vertex, id: rudderId, type: "rudder" };
			const rudderLink = { id: rudderId, source: vertex.id, target: rudderId };
			newNodeMap.set(vertex.id, node);
			newNodeMap.set(rudderId, rudderNode);
			newLinkMap.set(rudderId, rudderLink);
		});
		newEdgeMap.forEach((edge) => {
			if (ForceGraph.edgeRequiresBezier(edge)) {
				const sourceLinkId = `${edge.source}-to-${edge.id}`;
				const targetLinkId = `${edge.id}-to-${edge.target}`;
				const sourceLink = {
					id: sourceLinkId,
					source: edge.source,
					target: edge.id,
				};
				const targetLink = {
					id: targetLinkId,
					source: edge.id,
					target: edge.target,
				};
				const edgeNode = { ...edge, type: "edge" };
				newNodeMap.set(edge.id, edgeNode);
				newLinkMap.set(sourceLinkId, sourceLink);
				newLinkMap.set(targetLinkId, targetLink);
			} else {
				const link = { ...edge };
				newLinkMap.set(edge.id, link);
			}
		});
		return { newNodeMap, newLinkMap };
	}

	static updateOldNodeAndLinkMaps(
		newNodeMap,
		oldNodeMap,
		newLinkMap,
		oldLinkMap,
	) {
		Array.from(oldLinkMap.keys()).forEach((linkId) => {
			if (!newLinkMap.has(linkId)) {
				oldLinkMap.delete(linkId);
			}
		});
		newLinkMap.forEach((newLink, linkId) => {
			oldLinkMap.set(
				linkId,
				Object.assign(oldLinkMap.get(linkId) || {}, newLink),
			);
		});
		Array.from(oldNodeMap.keys()).forEach((nodeId) => {
			if (!newNodeMap.has(nodeId)) {
				oldNodeMap.delete(nodeId);
			}
		});
		newNodeMap.forEach((newNode, nodeId) => {
			oldNodeMap.set(
				nodeId,
				Object.assign(oldNodeMap.get(nodeId) || {}, newNode),
			);
		});
	}

	static updateSimulation(simulation, nodeMap, linkMap) {
		simulation.nodes(Array.from(nodeMap.values()));
		simulation.force("links").links(Array.from(linkMap.values()));
	}

	static nodeToVector3(node, vector) {
		vector.x = node.x;
		vector.y = node.y;
		vector.z = node.z;
	}

	static updateOldVertexAndEdgeMaps(
		newVertexMap,
		oldVertexMap,
		newEdgeMap,
		oldEdgeMap,
	) {
		const result = {
			vertices: { entrances: [], exits: [], updates: [] },
			edges: { entrances: [], exits: [], updates: [] },
		};
		Array.from(oldEdgeMap.keys()).forEach((edgeId) => {
			if (!newEdgeMap.has(edgeId)) {
				const edge = oldEdgeMap.get(edgeId);
				oldEdgeMap.delete(edgeId);
				result.edges.exits.push(edge);
			}
		});
		newEdgeMap.forEach((newEdge, edgeId) => {
			const edge = { ...(oldEdgeMap.get(edgeId) || {}), ...newEdge };
			if (oldEdgeMap.has(edgeId)) {
				// update
				result.edges.updates.push(edge);
			} else {
				// entrance
				result.edges.entrances.push(edge);
			}
			oldEdgeMap.set(edgeId, edge);
		});
		Array.from(oldVertexMap.keys()).forEach((vertexId) => {
			if (!newVertexMap.has(vertexId)) {
				const vertex = oldVertexMap.get(vertexId);
				oldVertexMap.delete(vertexId);
				result.vertices.exits.push(vertex);
			}
		});
		newVertexMap.forEach((newVertex, vertexId) => {
			const vertex = { ...(oldVertexMap.get(vertexId) || {}), ...newVertex };
			if (oldVertexMap.has(vertexId)) {
				// update
				result.vertices.updates.push(vertex);
			} else {
				// entrance
				result.vertices.entrances.push(vertex);
			}
			oldVertexMap.set(vertexId, vertex);
		});
		return result;
	}

	static updateVertexAndEdgePositions(vertexMap, edgeMap, nodeMap) {
		edgeMap.forEach((edge, edgeId) => {
			const source = nodeMap.get(edge.source);
			const target = nodeMap.get(edge.target);
			ForceGraph.nodeToVector3(source, edge.sourcePosition);
			ForceGraph.nodeToVector3(target, edge.targetPosition);
			if (ForceGraph.edgeRequiresBezier(edge)) {
				const control = nodeMap.get(edgeId);
				ForceGraph.nodeToVector3(control, edge.controlPosition);
			}
		});
		vertexMap.forEach((vertex, vertexId) => {
			const rudderId = `${vertex.id}-rudder`;
			const node = nodeMap.get(vertexId);
			const rudder = nodeMap.get(rudderId);
			ForceGraph.nodeToVector3(node, vertex.position);
			ForceGraph.nodeToVector3(rudder, vertex.rudderPosition);
		});
	}
}

export default ForceGraph;
