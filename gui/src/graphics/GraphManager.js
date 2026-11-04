import { dispatch } from "d3-dispatch";
import * as THREE from "three";
import DragControls from "./DragControls";
import Edge from "./Edge";
import LineManager from "./LineManager";
import TextLoader from "./TextLoader";
import Vertex from "./Vertex";

class GraphManager {
	constructor(forceGraph, sceneManager) {
		this.forceGraph = forceGraph;
		this.sceneManager = sceneManager;
		this.textLoader = new TextLoader();
		this.group = new THREE.Group();
		this.lineManager = new LineManager(this.sceneManager.scene, this.group);
		this.controls = new DragControls(
			[],
			this.sceneManager.camera,
			this.sceneManager.canvas,
		);
		this.envelopes = new Map();
		this.dispatcher = dispatch(
			"deselect",
			"doubleclick",
			"selectEdge",
			"selectVertex",
		);
		this.previousClickObject = null;
		this.previousClickTime = Date.now();
		this.sceneManager.scene.add(this.group);
		this.controls.on("deselect", this.onDeselect.bind(this));
		this.controls.on("drag", this.onDrag.bind(this));
		this.controls.on("dragend", this.onDragEnd.bind(this));
		this.controls.on("dragstart", this.onDragStart.bind(this));
		this.controls.on("mouseout", this.onMouseOut.bind(this));
		this.controls.on("mouseover", this.onMouseOver.bind(this));
		this.controls.on("select", this.onSelect.bind(this));
		this.forceGraph.on("graphRebuild", this.onGraphRebuild.bind(this));
		this.forceGraph.on("graphTick", this.onGraphTick.bind(this));
		this.sceneManager.on("beforeRender", this.onBeforeRender.bind(this));
	}

	on(name, _) {
		if (arguments.length > 1) {
			this.dispatcher.on(name, _);
		} else {
			this.dispatcher.on(name);
		}
	}

	onDeselect(event) {
		// console.log('deselect', event);
		const { replaced } = event;
		const { envelope } = event.object.parent;
		const graphObject = envelope.data;
		envelope.deselect();
		if (envelope.isVertex) {
			this.forceGraph.unpin(graphObject.id);
		}
		if (!replaced) {
			this.dispatcher.call("deselect", graphObject, graphObject);
		}
	}

	onDrag(event) {
		// console.log('drag', event);
		const { envelope } = event.object.parent;
		if (envelope.isVertex) {
			const vertex = envelope.data;
			const { position } = event;
			this.forceGraph.pin(vertex.id, position.x, position.y, position.z);
			this.forceGraph.reheat();
		}
	}

	onDragEnd() {
		// console.log('dragend', event);
		this.sceneManager.controls.enabled = true;
	}

	onDragStart(event) {
		// console.log('dragstart', event);
		this.sceneManager.controls.enabled = false;
		const { envelope } = event.object.parent;
		if (envelope.isVertex) {
			const vertex = envelope.data;
			const currentClickObject = envelope;
			const currentClickTime = Date.now();
			if (
				currentClickObject === this.previousClickObject &&
				currentClickTime - this.previousClickTime < 250
			) {
				// console.log('doubleclick');
				this.dispatcher.call("doubleclick", vertex, vertex);
			}
			this.previousClickObject = currentClickObject;
			this.previousClickTime = currentClickTime;
		}
	}

	onEdgeEnter(data) {
		const threeEdge = new Edge();
		threeEdge.enter(this, data, this.lineManager);
		this.envelopes.set(data.id, threeEdge);
	}

	onEdgeUpdate(data) {
		this.envelopes.get(data.id).update(data);
	}

	onEdgeGraphTick(data) {
		this.envelopes.get(data.id).graphTick(data);
	}

	onEdgeExit(data) {
		this.envelopes.get(data.id).exit();
	}

	onFrameTick(envelope) {
		envelope.frameTick();
	}

	onGraphRebuild(data) {
		data.vertices.entrances.forEach(this.onVertexEnter.bind(this));
		data.vertices.updates.forEach(this.onVertexUpdate.bind(this));
		data.vertices.exits.forEach(this.onVertexExit.bind(this));
		data.edges.entrances.forEach(this.onEdgeEnter.bind(this));
		data.edges.updates.forEach(this.onEdgeUpdate.bind(this));
		data.edges.exits.forEach(this.onEdgeExit.bind(this));
		this.lineManager.graphTick();
	}

	onGraphTick(data) {
		data.vertices.forEach(this.onVertexGraphTick.bind(this));
		data.edges.forEach(this.onEdgeGraphTick.bind(this));
		this.lineManager.graphTick();
	}

	onMouseOut(event) {
		// console.log('mouseout', event);
		const { envelope } = event.object.parent;
		envelope.mouseout();
	}

	onMouseOver(event) {
		// console.log('mouseover', event);
		const { envelope } = event.object.parent;
		envelope.mouseover();
	}

	onBeforeRender() {
		this.forceGraph.tick();
		this.envelopes.forEach(this.onFrameTick.bind(this));
		this.lineManager.frameTick();
	}

	onSelect(event) {
		// console.log('select', event);
		const { envelope } = event.object.parent;
		envelope.select();
		if (envelope.isVertex) {
			const vertex = envelope.data;
			this.forceGraph.reheat();
			this.forceGraph.pin(
				vertex.id,
				vertex.position.x,
				vertex.position.y,
				vertex.position.z,
			);
			this.dispatcher.call("selectVertex", vertex, vertex);
		} else if (envelope.isEdge) {
			const edge = envelope.data;
			const source = this.envelopes.get(edge.source).data;
			const target = this.envelopes.get(edge.target).data;
			this.dispatcher.call("selectEdge", edge, { edge, source, target });
		}
	}

	onVertexEnter(data) {
		const threeVertex = new Vertex();
		threeVertex.enter(this, data, this.textLoader);
		this.envelopes.set(data.id, threeVertex);
	}

	onVertexUpdate(data) {
		this.envelopes.get(data.id).update(data);
	}

	onVertexGraphTick(data) {
		this.envelopes.get(data.id).graphTick(data);
	}

	onVertexExit(data) {
		this.envelopes.get(data.id).exit();
		this.envelopes.delete(data.id);
	}

	addToControls(mesh) {
		this.controls.add(mesh);
	}

	addToLineManager(edge) {
		this.lineManager.add(edge);
	}

	addMesh(mesh) {
		this.group.add(mesh);
	}

	addToOutlines(mesh) {
		this.sceneManager.addToOutlines(mesh);
	}

	refreshEdgeColor(edge) {
		this.lineManager.updateColor(edge);
	}

	removeFromControls(mesh) {
		this.controls.remove(mesh);
	}

	removeFromLineManager(edge) {
		this.lineManager.remove(edge);
	}

	removeFromOutlines(mesh) {
		this.sceneManager.removeFromOutlines(mesh);
	}

	removeMesh(mesh) {
		this.group.remove(mesh);
	}
}

export default GraphManager;
