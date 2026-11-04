import chai from "chai";
import { Vector3 } from "three";
import ForceGraph from "../src/physics/ForceGraph";

const { expect } = chai;

const vertices = [
	{
		id: "vertex-1",
		label: "artist",
		name: "Foo",
		eid: 111,
	},
	{
		id: "vertex-2",
		label: "release",
		name: "Bar",
		eid: 222,
	},
	{
		id: "vertex-3",
		label: "company",
		name: "Baz",
		eid: 333,
	},
	{
		id: "vertex-4",
		label: "artist",
		name: "Quux",
		eid: 444,
	},
];

const edges = [
	{
		id: "edge-aaa",
		label: "credited_with",
		source: "vertex-1",
		target: "vertex-2",
		role: "Artwork By",
	},
	{
		id: "edge-bbb",
		label: "released_on",
		source: "vertex-2",
		target: "vertex-3",
	},
	{
		id: "edge-ccc",
		label: "alias_of",
		source: "vertex-1",
		target: "vertex-4",
	},
];

const filterObj = (obj, keys) =>
	keys.reduce(
		(newObj, key) =>
			obj[key] !== undefined ? { ...newObj, [key]: obj[key] } : newObj,
		{},
	);

const filterObjects = (objects, keys) =>
	objects.map((obj) => filterObj(obj, keys));

const setupEventMap = (graph) => {
	const eventMap = new Map([
		["vertexEnter", []],
		["vertexUpdate", []],
		["vertexTick", []],
		["vertexExit", []],
		["edgeEnter", []],
		["edgeUpdate", []],
		["edgeTick", []],
		["edgeExit", []],
	]);
	graph.on("graphRebuild", (data) => {
		eventMap
			.get("vertexEnter")
			.push(...data.vertices.entrances.map((x) => x.id));
		eventMap
			.get("vertexUpdate")
			.push(...data.vertices.updates.map((x) => x.id));
		eventMap.get("vertexExit").push(...data.vertices.exits.map((x) => x.id));
		eventMap.get("edgeEnter").push(...data.edges.entrances.map((x) => x.id));
		eventMap.get("edgeUpdate").push(...data.edges.updates.map((x) => x.id));
		eventMap.get("edgeExit").push(...data.edges.exits.map((x) => x.id));
	});
	graph.on("graphTick", (data) => {
		eventMap.get("vertexTick").push(...data.vertices.map((x) => x.id));
		eventMap.get("edgeTick").push(...data.edges.map((x) => x.id));
	});
	return eventMap;
};

const clearEventMap = (eventMap) => {
	eventMap.forEach((value) => {
		value.length = 0;
	});
};

describe("ForceGraph", () => {
	describe("Initially", () => {
		const graph = new ForceGraph();

		it("will have empty maps", () => {
			expect(graph.edgeMap.size).to.equal(0);
			expect(graph.linkMap.size).to.equal(0);
			expect(graph.nodeMap.size).to.equal(0);
			expect(graph.vertexMap.size).to.equal(0);
		});
	});

	describe("After one update", () => {
		const graph = new ForceGraph();
		const eventMap = setupEventMap(graph);
		graph.update([vertices[0], vertices[1]], [edges[0]]);

		it("will have these nodes", () => {
			const nodes = filterObjects(Array.from(graph.nodeMap.values()), [
				"eid",
				"id",
				"label",
				"name",
				"type",
				"role",
				"x",
				"y",
				"z",
			]);
			expect(nodes).to.deep.equal([
				{
					eid: 111,
					id: "vertex-1",
					label: "artist",
					name: "Foo",
					type: "vertex",
					x: 0,
					y: 0,
					z: 0,
				},
				{
					eid: 111,
					id: "vertex-1-rudder",
					label: "artist",
					name: "Foo",
					type: "rudder",
					x: -5.8989046725688885,
					y: -7.373688780783198,
					z: 3.2911453064392258,
				},
				{
					eid: 222,
					id: "vertex-2",
					label: "release",
					name: "Bar",
					type: "vertex",
					x: -6.592109382174828,
					y: 1.1014951087321225,
					z: 10.680398289188552,
				},
				{
					eid: 222,
					id: "vertex-2-rudder",
					label: "release",
					name: "Bar",
					type: "rudder",
					x: -0.5043044434857212,
					y: 8.775206858050936,
					z: 11.434588052566072,
				},
				{
					id: "edge-aaa",
					label: "credited_with",
					role: "Artwork By",
					type: "edge",
					x: 1.2394593758651264,
					y: -15.631352224769836,
					z: 2.4715942344441864,
				},
			]);
		});

		it("will have these links", () => {
			expect(Array.from(graph.linkMap.keys())).to.deep.equal([
				"vertex-1-rudder",
				"vertex-2-rudder",
				"vertex-1-to-edge-aaa",
				"edge-aaa-to-vertex-2",
			]);
		});

		it("will have these vertices", () => {
			const vertexSummaries = filterObjects(
				Array.from(graph.vertexMap.values()),
				["eid", "id", "label", "name", "position", "rudderPosition"],
			);
			expect(vertexSummaries).to.deep.equal([
				{
					eid: 111,
					id: "vertex-1",
					label: "artist",
					name: "Foo",
					position: new Vector3(0, 0, 0),
					rudderPosition: new Vector3(
						-5.8989046725688885,
						-7.373688780783198,
						3.2911453064392258,
					),
				},
				{
					eid: 222,
					id: "vertex-2",
					label: "release",
					name: "Bar",
					position: new Vector3(
						-6.592109382174828,
						1.1014951087321225,
						10.680398289188552,
					),
					rudderPosition: new Vector3(
						-0.5043044434857212,
						8.775206858050936,
						11.434588052566072,
					),
				},
			]);
		});

		it("will have these edges", () => {
			const edgeSummaries = filterObjects(Array.from(graph.edgeMap.values()), [
				"id",
				"label",
				"name",
				"role",
				"sourcePosition",
				"targetPosition",
				"controlPosition",
			]);
			expect(edgeSummaries).to.deep.equal([
				{
					controlPosition: new Vector3(
						1.2394593758651264,
						-15.631352224769836,
						2.4715942344441864,
					),
					id: "edge-aaa",
					label: "credited_with",
					role: "Artwork By",
					sourcePosition: new Vector3(0, 0, 0),
					targetPosition: new Vector3(
						-6.592109382174828,
						1.1014951087321225,
						10.680398289188552,
					),
				},
			]);
		});

		it("will have dispatched mutation events", () => {
			expect(Array.from(eventMap.entries())).to.deep.equal([
				["vertexEnter", ["vertex-1", "vertex-2"]],
				["vertexUpdate", []],
				["vertexTick", []],
				["vertexExit", []],
				["edgeEnter", ["edge-aaa"]],
				["edgeUpdate", []],
				["edgeTick", []],
				["edgeExit", []],
			]);
		});
	});

	describe("After two updates", () => {
		const graph = new ForceGraph();
		const eventMap = setupEventMap(graph);
		graph.update([vertices[0], vertices[1]], [edges[0]]);
		clearEventMap(eventMap);
		graph.update([vertices[1], vertices[2]], [edges[1]]);

		it("will have these nodes", () => {
			const nodes = filterObjects(Array.from(graph.nodeMap.values()), [
				"eid",
				"id",
				"label",
				"name",
				"type",
				"role",
				"x",
				"y",
				"z",
			]);
			expect(nodes).to.deep.equal([
				{
					eid: 222,
					id: "vertex-2",
					label: "release",
					name: "Bar",
					type: "vertex",
					x: -6.592109382174828,
					y: 1.1014951087321225,
					z: 10.680398289188552,
				},
				{
					eid: 222,
					id: "vertex-2-rudder",
					label: "release",
					name: "Bar",
					type: "rudder",
					x: -0.5043044434857212,
					y: 8.775206858050936,
					z: 11.434588052566072,
				},
				{
					eid: 333,
					id: "vertex-3",
					label: "company",
					name: "Baz",
					type: "vertex",
					x: -6.592109382174828,
					y: 1.1014951087321225,
					z: 10.680398289188552,
				},
				{
					eid: 333,
					id: "vertex-3-rudder",
					label: "company",
					name: "Baz",
					type: "rudder",
					x: -0.5043044434857212,
					y: 8.775206858050936,
					z: 11.434588052566072,
				},
				{
					id: "edge-bbb",
					label: "released_on",
					type: "edge",
					x: 1.2394593758651264,
					y: -15.631352224769836,
					z: 2.4715942344441864,
				},
			]);
		});

		it("will have these links", () => {
			expect(Array.from(graph.linkMap.keys())).to.deep.equal([
				"vertex-2-rudder",
				"vertex-3-rudder",
				"vertex-2-to-edge-bbb",
				"edge-bbb-to-vertex-3",
			]);
		});

		it("will have these vertices", () => {
			const vertexSummaries = filterObjects(
				Array.from(graph.vertexMap.values()),
				["eid", "id", "label", "name", "position", "rudderPosition"],
			);
			expect(vertexSummaries).to.deep.equal([
				{
					eid: 222,
					id: "vertex-2",
					label: "release",
					name: "Bar",
					position: new Vector3(
						-6.592109382174828,
						1.1014951087321225,
						10.680398289188552,
					),
					rudderPosition: new Vector3(
						-0.5043044434857212,
						8.775206858050936,
						11.434588052566072,
					),
				},
				{
					eid: 333,
					id: "vertex-3",
					label: "company",
					name: "Baz",
					position: new Vector3(
						-6.592109382174828,
						1.1014951087321225,
						10.680398289188552,
					),
					rudderPosition: new Vector3(
						-0.5043044434857212,
						8.775206858050936,
						11.434588052566072,
					),
				},
			]);
		});

		it("will have these edges", () => {
			const edgeSummaries = filterObjects(Array.from(graph.edgeMap.values()), [
				"id",
				"label",
				"name",
				"role",
				"sourcePosition",
				"targetPosition",
				"controlPosition",
			]);
			expect(edgeSummaries).to.deep.equal([
				{
					controlPosition: new Vector3(
						1.2394593758651264,
						-15.631352224769836,
						2.4715942344441864,
					),
					id: "edge-bbb",
					label: "released_on",
					sourcePosition: new Vector3(
						-6.592109382174828,
						1.1014951087321225,
						10.680398289188552,
					),
					targetPosition: new Vector3(
						-6.592109382174828,
						1.1014951087321225,
						10.680398289188552,
					),
				},
			]);
		});

		it("will have dispatched mutation events", () => {
			expect(Array.from(eventMap.entries())).to.deep.equal([
				["vertexEnter", ["vertex-3"]],
				["vertexUpdate", ["vertex-2"]],
				["vertexTick", []],
				["vertexExit", ["vertex-1"]],
				["edgeEnter", ["edge-bbb"]],
				["edgeUpdate", []],
				["edgeTick", []],
				["edgeExit", ["edge-aaa"]],
			]);
		});
	});

	describe("After three updates", () => {
		const graph = new ForceGraph();
		const eventMap = setupEventMap(graph);
		graph.update([vertices[0], vertices[1]], [edges[0]]);
		graph.update([vertices[1], vertices[2]], [edges[1]]);
		clearEventMap(eventMap);
		graph.update([vertices[0], vertices[3]], [edges[2]]);

		it("will have these nodes", () => {
			const nodes = filterObjects(Array.from(graph.nodeMap.values()), [
				"eid",
				"id",
				"label",
				"name",
				"type",
				"role",
				"x",
				"y",
				"z",
			]);
			expect(nodes).to.deep.equal([
				{
					eid: 111,
					id: "vertex-1",
					label: "artist",
					name: "Foo",
					type: "vertex",
					x: 0,
					y: 0,
					z: 0,
				},
				{
					eid: 111,
					id: "vertex-1-rudder",
					label: "artist",
					name: "Foo",
					type: "rudder",
					x: -5.8989046725688885,
					y: -7.373688780783198,
					z: 3.2911453064392258,
				},
				{
					eid: 444,
					id: "vertex-4",
					label: "artist",
					name: "Quux",
					type: "vertex",
					x: -6.592109382174828,
					y: 1.1014951087321225,
					z: 10.680398289188552,
				},
				{
					eid: 444,
					id: "vertex-4-rudder",
					label: "artist",
					name: "Quux",
					type: "rudder",
					x: -0.5043044434857212,
					y: 8.775206858050936,
					z: 11.434588052566072,
				},
			]);
		});

		it("will have these links", () => {
			expect(Array.from(graph.linkMap.keys())).to.deep.equal([
				"vertex-1-rudder",
				"vertex-4-rudder",
				"edge-ccc",
			]);
		});

		it("will have these vertices", () => {
			const vertexSummaries = filterObjects(
				Array.from(graph.vertexMap.values()),
				["eid", "id", "label", "name", "position", "rudderPosition"],
			);
			expect(vertexSummaries).to.deep.equal([
				{
					eid: 111,
					id: "vertex-1",
					label: "artist",
					name: "Foo",
					position: new Vector3(0, 0, 0),
					rudderPosition: new Vector3(
						-5.8989046725688885,
						-7.373688780783198,
						3.2911453064392258,
					),
				},
				{
					eid: 444,
					id: "vertex-4",
					label: "artist",
					name: "Quux",
					position: new Vector3(
						-6.592109382174828,
						1.1014951087321225,
						10.680398289188552,
					),
					rudderPosition: new Vector3(
						-0.5043044434857212,
						8.775206858050936,
						11.434588052566072,
					),
				},
			]);
		});

		it("will have these edges", () => {
			const edgeSummaries = filterObjects(Array.from(graph.edgeMap.values()), [
				"id",
				"label",
				"name",
				"role",
				"sourcePosition",
				"targetPosition",
				"controlPosition",
			]);
			expect(edgeSummaries).to.deep.equal([
				{
					id: "edge-ccc",
					label: "alias_of",
					sourcePosition: new Vector3(0, 0, 0),
					targetPosition: new Vector3(
						-6.592109382174828,
						1.1014951087321225,
						10.680398289188552,
					),
				},
			]);
		});

		it("will have dispatched mutation events", () => {
			expect(Array.from(eventMap.entries())).to.deep.equal([
				["vertexEnter", ["vertex-1", "vertex-4"]],
				["vertexUpdate", []],
				["vertexTick", []],
				["vertexExit", ["vertex-2", "vertex-3"]],
				["edgeEnter", ["edge-ccc"]],
				["edgeUpdate", []],
				["edgeTick", []],
				["edgeExit", ["edge-bbb"]],
			]);
		});
	});

	describe("After one tick", () => {
		const graph = new ForceGraph();
		const eventMap = setupEventMap(graph);
		graph.update(vertices, edges);
		clearEventMap(eventMap);
		graph.tick();

		it("will have dispatched mutation events", () => {
			expect(Array.from(eventMap.entries())).to.deep.equal([
				["vertexEnter", []],
				["vertexUpdate", []],
				["vertexTick", ["vertex-1", "vertex-2", "vertex-3", "vertex-4"]],
				["vertexExit", []],
				["edgeEnter", []],
				["edgeUpdate", []],
				["edgeTick", ["edge-aaa", "edge-bbb", "edge-ccc"]],
				["edgeExit", []],
			]);
		});
	});

	describe("After two ticks", () => {
		const graph = new ForceGraph();
		const eventMap = setupEventMap(graph);
		graph.update(vertices, edges);
		graph.tick();
		clearEventMap(eventMap);
		graph.tick();

		it("will have dispatched mutation events", () => {
			expect(Array.from(eventMap.entries())).to.deep.equal([
				["vertexEnter", []],
				["vertexUpdate", []],
				["vertexTick", ["vertex-1", "vertex-2", "vertex-3", "vertex-4"]],
				["vertexExit", []],
				["edgeEnter", []],
				["edgeUpdate", []],
				["edgeTick", ["edge-aaa", "edge-bbb", "edge-ccc"]],
				["edgeExit", []],
			]);
		});
	});
});
