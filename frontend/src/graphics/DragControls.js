import { dispatch } from "d3-dispatch";
import { Plane, Raycaster, Vector2, Vector3 } from "three";

class DragControls {
	constructor(objects, camera, canvas) {
		this.camera = camera;
		this.canvas = canvas;
		this.dispatcher = dispatch(
			"drag",
			"dragstart",
			"dragend",
			"mouseover",
			"mouseout",
			"select",
			"deselect",
		);
		this.dragged = null;
		this.enabled = true;
		this.hovered = null;
		this.intersection = new Vector3();
		this.intersections = [];
		this.mouse = new Vector2();
		this.objects = objects || [];
		this.plane = new Plane();
		this.raycaster = new Raycaster();
		this.raycaster.params.Line.threshold = 0.25;
		this.selected = null;
		this.worldPosition = new Vector3();
		this.activate();
	}

	activate() {
		this.canvas.addEventListener(
			"mousemove",
			this.onDocumentMouseMove.bind(this),
			false,
		);
		this.canvas.addEventListener(
			"mousedown",
			this.onDocumentMouseDown.bind(this),
			false,
		);
		this.canvas.addEventListener(
			"mouseup",
			this.onDocumentMouseCancel.bind(this),
			false,
		);
		this.canvas.addEventListener(
			"mouseleave",
			this.onDocumentMouseCancel.bind(this),
			false,
		);
		this.canvas.addEventListener(
			"touchmove",
			this.onDocumentTouchMove.bind(this),
			false,
		);
		this.canvas.addEventListener(
			"touchstart",
			this.onDocumentTouchStart.bind(this),
			false,
		);
		this.canvas.addEventListener(
			"touchend",
			this.onDocumentTouchEnd.bind(this),
			false,
		);
	}

	add(_) {
		this.objects.push(_);
	}

	deactivate() {
		this.canvas.removeEventListener(
			"mousemove",
			this.onDocumentMouseMove.bind(this),
			false,
		);
		this.canvas.removeEventListener(
			"mousedown",
			this.onDocumentMouseDown.bind(this),
			false,
		);
		this.canvas.removeEventListener(
			"mouseup",
			this.onDocumentMouseCancel.bind(this),
			false,
		);
		this.canvas.removeEventListener(
			"mouseleave",
			this.onDocumentMouseCancel.bind(this),
			false,
		);
		this.canvas.removeEventListener(
			"touchmove",
			this.onDocumentTouchMove.bind(this),
			false,
		);
		this.canvas.removeEventListener(
			"touchstart",
			this.onDocumentTouchStart.bind(this),
			false,
		);
		this.canvas.removeEventListener(
			"touchend",
			this.onDocumentTouchEnd.bind(this),
			false,
		);
		this.canvas.style.cursor = "";
	}

	dispose() {
		this.deactivate();
	}

	enabled(_) {
		if (arguments.length > 0) {
			this.enabled = _;
			return this;
		}
		return this.enabled;
	}

	on(name, _) {
		if (arguments.length > 1) {
			this.dispatcher.on(name, _);
			return this;
		}
		return this.dispatcher.on(name);
	}

	onDocumentMouseCancel(event) {
		event.preventDefault();
		if (this.dragged) {
			this.dispatcher.call("dragend", null, { event, object: this.dragged });
			this.dragged = null;
		}
		this.canvas.style.cursor = this.hovered ? "pointer" : "auto";
	}

	onDocumentMouseDown(event) {
		event.preventDefault();
		this.intersections.length = 0;
		this.raycaster.setFromCamera(this.mouse, this.camera);
		this.raycaster.intersectObjects(this.objects, true, this.intersections);
		if (this.intersections.length > 0) {
			this.dragged = this.intersections[0].object;
			/* eslint-disable-next-line no-restricted-syntax */
			for (const intersection of this.intersections) {
				if (intersection.object.parent.envelope.isVertex) {
					this.dragged = intersection.object;
					break;
				}
			}
			this.raycaster.ray.intersectPlane(this.plane, this.intersection);
			this.canvas.style.cursor = "move";
			if (this.dragged !== this.selected) {
				if (this.selected) {
					this.dispatcher.call("deselect", null, {
						event,
						object: this.selected,
						replaced: true,
					});
				}
				this.selected = this.dragged;
				this.dispatcher.call("select", null, { event, object: this.selected });
			}
			this.dispatcher.call("dragstart", null, { event, object: this.dragged });
		} else if (this.selected) {
			this.dispatcher.call("deselect", null, {
				event,
				object: this.selected,
				replaced: false,
			});
			this.selected = null;
		}
	}

	onDocumentMouseMove(event) {
		event.preventDefault();
		const rect = this.canvas.getBoundingClientRect();
		this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
		this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
		this.raycaster.setFromCamera(this.mouse, this.camera);
		if (this.dragged && this.enabled) {
			this.raycaster.ray.intersectPlane(this.plane, this.intersection);
			this.dispatcher.call("drag", null, {
				event,
				object: this.dragged,
				position: this.intersection,
			});
			return;
		}
		this.intersections.length = 0;
		this.raycaster.setFromCamera(this.mouse, this.camera);
		this.raycaster.intersectObjects(this.objects, true, this.intersections);
		if (this.intersections.length > 0) {
			let { object } = this.intersections[0];
			/* eslint-disable-next-line no-restricted-syntax */
			for (const intersection of this.intersections) {
				if (intersection.object.parent.envelope.isVertex) {
					object = intersection.object;
					break;
				}
			}
			this.plane.setFromNormalAndCoplanarPoint(
				this.camera.getWorldDirection(this.plane.normal),
				this.worldPosition.setFromMatrixPosition(object.matrixWorld),
			);
			if (this.hovered !== object) {
				if (this.hovered !== null) {
					this.dispatcher.call("mouseout", null, {
						event,
						object: this.hovered,
					});
				}
				this.dispatcher.call("mouseover", null, { event, object });
				this.canvas.style.cursor = "pointer";
				this.hovered = object;
			}
		} else if (this.hovered !== null) {
			this.dispatcher.call("mouseout", null, { event, object: this.hovered });
			this.canvas.style.cursor = "auto";
			this.hovered = null;
		}
	}

	onDocumentTouchEnd(event) {
		event.preventDefault();
		if (this.dragged) {
			this.dispatcher.call("dragend", null, { event, object: this.dragged });
			this.dragged = null;
		}
		this.canvas.style.cursor = "auto";
	}

	onDocumentTouchMove(event) {
		event.preventDefault();
		const rect = this.canvas.getBoundingClientRect();
		const touch = event.changedTouches[0];
		this.mouse.x = ((touch.clientX - rect.left) / rect.width) * 2 - 1;
		this.mouse.y = -((touch.clientY - rect.top) / rect.height) * 2 + 1;
		this.raycaster.setFromCamera(this.mouse, this.camera);
		if (this.dragged && this.enabled) {
			this.raycaster.ray.intersectPlane(this.plane, this.intersection);
			this.dispatcher.call("drag", null, {
				event,
				object: this.dragged,
				position: this.intersection,
			});
		}
	}

	onDocumentTouchStart(event) {
		event.preventDefault();
		const rect = this.canvas.getBoundingClientRect();
		const touch = event.changedTouches[0];
		this.mouse.x = ((touch.clientX - rect.left) / rect.width) * 2 - 1;
		this.mouse.y = -((touch.clientY - rect.top) / rect.height) * 2 + 1;
		this.intersections.length = 0;
		this.raycaster.setFromCamera(this.mouse, this.camera);
		this.raycaster.intersectObjects(this.objects, true, this.intersections);
		if (this.intersections.length > 0) {
			this.dragged = this.intersections[0].object;
			/* eslint-disable-next-line no-restricted-syntax */
			for (const intersection of this.intersections) {
				if (intersection.object.parent.envelope.isVertex) {
					this.dragged = intersection.object;
					break;
				}
			}
			this.plane.setFromNormalAndCoplanarPoint(
				this.camera.getWorldDirection(this.plane.normal),
				this.worldPosition.setFromMatrixPosition(this.dragged.matrixWorld),
			);
			this.raycaster.ray.intersectPlane(this.plane, this.intersection);
			this.canvas.style.cursor = "move";
			if (this.dragged !== this.selected) {
				if (this.selected) {
					this.dispatcher.call("deselect", null, {
						event,
						object: this.selected,
						replaced: true,
					});
				}
				this.selected = this.dragged;
				this.dispatcher.call("select", null, { event, object: this.selected });
			}
			this.dispatcher.call("dragstart", null, { event, object: this.dragged });
		} else if (this.selected) {
			this.dispatcher.call("deselect", null, {
				event,
				object: this.selected,
				replaced: false,
			});
			this.selected = null;
		}
	}

	remove(_) {
		const index = this.objects.indexOf(_);
		if (index > -1) {
			this.objects.splice(index, 1);
			if (_ === this.selected) {
				this.selected = null;
			}
			if (_ === this.hovered) {
				this.hovered = null;
			}
			if (_ === this.dragged) {
				this.dragged = null;
			}
		}
	}
}

export default DragControls;
