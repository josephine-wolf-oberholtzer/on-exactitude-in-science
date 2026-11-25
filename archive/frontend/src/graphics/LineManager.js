import * as THREE from "three";
import { LineMaterial } from "three/examples/jsm/lines/LineMaterial";
import { LineSegments2 } from "three/examples/jsm/lines/LineSegments2";
import { LineSegmentsGeometry } from "three/examples/jsm/lines/LineSegmentsGeometry";

class LineManager {
	constructor(scene, parent) {
		this.scene = scene;
		this.parent = parent;
		this.edges = new Map();
		this.mesh = new LineSegments2(
			new LineSegmentsGeometry(),
			new LineMaterial({
				fog: this.scene.fog,
				linewidth: 2,
				vertexColors: true,
			}),
		);
		this.dirty = true;
		this.parent.add(this.mesh);
		this.colors = [];
		this.positions = [];
	}

	add(edge) {
		this.edges.set(edge, 0);
		this.dirty = true;
	}

	remove(edge) {
		this.edges.delete(edge);
		this.dirty = true;
	}

	frameTick() {
		this.mesh.material.resolution.set(window.innerWidth, window.innerHeight);
	}

	buildColorArray(startColor, endColor, length) {
		const colors = [];
		for (let i = 0; i < length; i++) {
			colors.push(new THREE.Color(startColor).lerp(endColor, i / (length - 1)));
		}
		return colors;
	}

	buildFlattenedColorSegment(startColor, endColor, length) {
		const segment = [];
		const colors = this.buildColorArray(startColor, endColor, length);
		for (let i = 1; i < length; i++) {
			segment.push(
				colors[i - 1].r,
				colors[i - 1].g,
				colors[i - 1].b,
				colors[i].r,
				colors[i].g,
				colors[i].b,
			);
		}
		return segment;
	}

	buildFlattenedPositionSegment(points) {
		const segment = [];
		const { length } = points;
		for (let i = 1; i < length; i++) {
			segment.push(
				points[i - 1].x,
				points[i - 1].y,
				points[i - 1].z,
				points[i].x,
				points[i].y,
				points[i].z,
			);
		}
		return segment;
	}

	graphTick() {
		let baseIndex = 0;
		if (this.dirty) {
			this.colors.length = 0;
			this.positions.length = 0;
			this.edges.forEach((_, edge) => {
				const { startColor, endColor } = edge.calculateColors();
				this.edges.set(edge, baseIndex);
				this.positions.push(...this.buildFlattenedPositionSegment(edge.points));
				this.colors.push(
					...this.buildFlattenedColorSegment(
						startColor,
						endColor,
						edge.points.length,
					),
				);
				baseIndex += edge.points.length - 1;
			});
			this.dirty = false;
			this.mesh.geometry = new LineSegmentsGeometry();
			this.mesh.geometry.setPositions(this.positions);
			this.mesh.geometry.setColors(this.colors);
		} else {
			this.edges.forEach((_, edge) => {
				this.setEdgePositions(edge);
			});
		}
	}

	setEdgeColors(edge) {
		const { instanceColorStart, instanceColorEnd } =
			this.mesh.geometry.attributes;
		const baseIndex = this.edges.get(edge);
		const { length } = edge.points;
		const { startColor, endColor } = edge.calculateColors();
		const colors = this.buildColorArray(startColor, endColor, length);
		for (let i = 0; i < length - 1; i++) {
			const start = colors[i];
			const end = colors[i + 1];
			instanceColorStart.setXYZ(baseIndex + i, start.r, start.g, start.b);
			instanceColorEnd.setXYZ(baseIndex + i, end.r, end.g, end.b);
		}
		instanceColorStart.data.needsUpdate = true;
	}

	setEdgePositions(edge) {
		const { instanceStart, instanceEnd } = this.mesh.geometry.attributes;
		const baseIndex = this.edges.get(edge);
		const { length } = edge.points;
		for (let i = 0; i < length - 1; i++) {
			const start = edge.points[i];
			const end = edge.points[i + 1];
			instanceStart.setXYZ(baseIndex + i, start.x, start.y, start.z);
			instanceEnd.setXYZ(baseIndex + i, end.x, end.y, end.z);
		}
		instanceStart.data.needsUpdate = true;
	}

	updateColor(edge) {
		this.setEdgeColors(edge);
	}
}

export default LineManager;
