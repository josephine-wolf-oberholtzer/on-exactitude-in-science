import { GPU } from "gpu.js";

const forceGPU = () => {
	const constant = (x) => () => x;
	const gpu = new GPU();

	let distanceMax2 = 10000000000.0,
		distanceMin2 = 1,
		kernel,
		nDim = 2,
		nodes = [],
		positions = [],
		radii = [],
		radius = constant(0),
		strength = constant(-30),
		strengths;

	function kernel3d(positionsArray, radiiArray, strengthsArray) {
		const thisX = positionsArray[this.thread.x][0];
		const thisY = positionsArray[this.thread.x][1];
		const thisZ = positionsArray[this.thread.x][2];
		const thisRadius = radiiArray[this.thread.x];
		let vx = 0.0,
			vy = 0.0,
			vz = 0.0,
			weight = 0.0;
		for (let i = 0; i < this.constants.size; i++) {
			const thatX = positionsArray[i][0];
			const thatY = positionsArray[i][1];
			const thatZ = positionsArray[i][2];
			const thatRadius = radiiArray[i];
			const thatStrength = strengthsArray[i];
			const deltaX = thatX - thisX;
			const deltaY = thatY - thisY;
			const deltaZ = thatZ - thisZ;
			const distance = deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ;
			const cumRadius = thatRadius + thisRadius;
			if (i !== this.thread.x) {
				if (distance < cumRadius * cumRadius) {
					const otherDistance =
						(cumRadius - Math.sqrt(distance)) / (Math.sqrt(distance) * 1.0);
					weight =
						this.constants.alpha *
						otherDistance *
						((thisRadius * thisRadius) /
							(thisRadius * thisRadius + thatRadius));
					vx -= deltaX * weight;
					vy -= deltaY * weight;
					vz -= deltaZ * weight;
				}
				if (distance < this.constants.distanceMax2) {
					let otherDistance = distance;
					if (distance < this.constants.distanceMin2) {
						otherDistance = Math.sqrt(this.constants.distanceMin2 * distance);
					}
					weight = (thatStrength * this.constants.alpha) / otherDistance;
					vx += deltaX * weight;
					vy += deltaY * weight;
					vz += deltaZ * weight;
				}
			}
		}
		return [vx, vy, vz];
	}

	function collectPositions() {
		const n = nodes.length;
		for (let i = 0; i < n; i++) {
			positions[nodes[i].index][0] = nodes[i].x;
			if (nDim > 1) {
				positions[nodes[i].index][1] = nodes[i].y;
			}
			if (nDim > 2) {
				positions[nodes[i].index][2] = nodes[i].z;
			}
		}
		return positions;
	}

	function force(_) {
		if (!nodes.length) {
			return;
		}
		positions = collectPositions();
		const n = nodes.length;
		const velocities =
			(kernel.setConstants({
				alpha: _,
				distanceMax2,
				distanceMin2,
				size: n,
			}),
			kernel(positions, radii, strengths));
		for (let i = 0; i < n; i++) {
			const node = nodes[i];
			const [vx, vy, vz] = velocities[i];
			node.vx += vx;
			if (nDim > 1) {
				node.vy += vy;
			}
			if (nDim > 2) {
				node.vz += vz;
			}
		}
	}

	function initialize() {
		if (!nodes.length) {
			return;
		}
		const n = nodes.length;
		const settings = {
			loopMaxIterations: n,
			output: [n],
		};
		positions = new Array(nodes.length);
		radii = new Array(nodes.length);
		strengths = new Array(nodes.length);
		for (let i = 0; i < n; i++) {
			radii[nodes[i].index] = +radius(nodes[i], i, nodes);
			strengths[nodes[i].index] = +strength(nodes[i], i, nodes);
			positions[nodes[i].index] = [0.0, 0.0, 0.0];
		}
		if (nDim === 3) {
			kernel = gpu.createKernel(kernel3d, settings);
		}
	}

	force.initialize = (initNodes, numDimensions) => {
		nodes = initNodes;
		nDim = numDimensions;
		initialize();
	};

	force.distanceMax = function (_) {
		if (arguments.length) {
			distanceMax2 = _ * _;
			return force;
		}
		return Math.sqrt(distanceMax2);
	};

	force.distanceMin = function (_) {
		if (arguments.length) {
			distanceMin2 = _ * _;
			return force;
		}
		return Math.sqrt(distanceMin2);
	};

	force.radius = function (_) {
		if (arguments.length) {
			if (typeof _ === "function") {
				radius = _;
			} else {
				radius = constant(+_);
			}
			initialize();
			return force;
		}
		return radius;
	};

	force.strength = function (_) {
		if (arguments.length) {
			if (typeof _ === "function") {
				strength = _;
			} else {
				strength = constant(+_);
			}
			initialize();
			return force;
		}
		return strength;
	};

	return force;
};

export default forceGPU;
