const forceManyBodyNaive = () => {
	function constant(x) {
		return () => x;
	}

	function jiggle() {
		return (Math.random() - 0.5) * 1e-6;
	}

	let distanceMax2 = Infinity,
		distanceMin2 = 1,
		nodes = [],
		strength = constant(-30),
		strengths = [];

	function force(_) {
		if (!nodes.length) {
			return;
		}
		const n = nodes.length;
		for (let i = 0; i < n; i++) {
			const thisNode = nodes[i];
			const thisX = thisNode.x;
			const thisY = thisNode.y;
			const thisZ = thisNode.z;
			let vx = 0.0,
				vy = 0.0,
				vz = 0.0;
			for (let j = 0; j < n; j++) {
				if (i === j) {
					continue;
				}
				const thatNode = nodes[j];
				const thatX = thatNode.x;
				const thatY = thatNode.y;
				const thatZ = thatNode.z;
				const thatStrength = strengths[j];
				let deltaX = thatX - thisX,
					deltaY = thatY - thisY,
					deltaZ = thatZ - thisZ,
					distance = deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ;
				if (distance >= distanceMax2) {
					continue;
				}
				if (deltaX === 0) {
					deltaX = jiggle();
					distance += deltaX * deltaX;
				}
				if (deltaY === 0) {
					deltaY = jiggle();
					distance += deltaY * deltaY;
				}
				if (deltaZ === 0) {
					deltaZ = jiggle();
					distance += deltaZ * deltaZ;
				}
				if (distance < distanceMin2) {
					distance = Math.sqrt(distanceMin2 * distance);
				}
				const weight = (thatStrength * _) / distance;
				vx += deltaX * weight;
				vy += deltaY * weight;
				vz += deltaZ * weight;
			}
			thisNode.vx += vx;
			thisNode.vy += vy;
			thisNode.vz += vz;
		}
	}

	function initialize() {
		if (!nodes.length) {
			return;
		}
		const n = nodes.length;
		strengths = new Array(nodes.length);
		for (let i = 0; i < n; i++) {
			strengths[nodes[i].index] = +strength(nodes[i], i, nodes);
		}
	}

	force.initialize = (initNodes) => {
		nodes = initNodes;
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

export default forceManyBodyNaive;
