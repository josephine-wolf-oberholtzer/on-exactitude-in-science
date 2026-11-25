import * as THREE from "three";

class TextLoader {
	constructor() {
		this.mainCanvas = new OffscreenCanvas(1, 1);
		this.mainContext = this.mainCanvas.getContext("2d");
		this.font = "128px sans-serif";
		this.fillStyle = "#fff";
		this.borderWidth = 8;
		this.mainContext.font = this.font;
	}

	loadCanvas(text) {
		const textMetrics = this.mainContext.measureText(text);
		const { width } = textMetrics;
		const height =
			textMetrics.actualBoundingBoxAscent +
			textMetrics.actualBoundingBoxDescent;
		const canvas = new OffscreenCanvas(
			width + this.borderWidth * 2,
			height + this.borderWidth * 2,
		);
		const context = canvas.getContext("2d");
		context.lineWidth = this.borderWidth;
		context.font = this.font;
		context.fillStyle = this.fillStyle;
		context.fillText(text, 0, textMetrics.actualBoundingBoxAscent);
		return canvas;
	}

	loadTexture(canvas) {
		const texture = new THREE.CanvasTexture(canvas);
		texture.minFilter = THREE.LinearFilter;
		return texture;
	}

	loadMesh(text) {
		const canvas = this.loadCanvas(text);
		const scale = 1 / 128;
		const width = canvas.width * scale;
		const height = canvas.height * scale;
		const texture = this.loadTexture(canvas);
		const material = new THREE.MeshLambertMaterial({
			map: texture,
			transparent: true,
		});
		const geometry = new THREE.PlaneBufferGeometry(width, height);
		const mesh = new THREE.Mesh(geometry, material);
		return mesh;
	}
}

export default TextLoader;
