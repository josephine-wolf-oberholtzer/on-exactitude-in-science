if (!window.OffscreenCanvas) {
	// Called with `new`; returning an object from a function constructor yields
	// that object, so callers receive a real <canvas> element.
	window.OffscreenCanvas = function OffscreenCanvas(width, height) {
		const canvas = document.createElement("canvas");
		canvas.width = width;
		canvas.height = height;
		canvas.convertToBlob = () =>
			new Promise((resolve) => {
				canvas.toBlob(resolve);
			});
		return canvas;
	};
}
