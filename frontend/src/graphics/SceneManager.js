import { dispatch } from "d3-dispatch";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer";
import { OutlinePass } from "three/examples/jsm/postprocessing/OutlinePass";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass";

class SceneManager {
	constructor(container) {
		this.scene = new THREE.Scene();
		this.camera = new THREE.PerspectiveCamera(
			45,
			window.innerWidth / window.innerHeight,
			1,
			5000,
		);
		this.renderer = new THREE.WebGLRenderer({
			alpha: false,
			antialias: true,
			stencil: false,
		});
		this.composer = new EffectComposer(this.renderer);
		this.renderPass = new RenderPass(this.scene, this.camera);
		this.outlinePass = new OutlinePass(
			new THREE.Vector2(window.innerWidth, window.innerHeight),
			this.scene,
			this.camera,
		);

		this.container = container;
		this.dispatcher = dispatch("beforeRender");
		this.canvas = this.renderer.domElement;
		this.controls = new OrbitControls(this.camera, this.canvas);
		this.ambientLight = new THREE.AmbientLight(0x606060); // soft white light
		this.hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x000000);

		this.outlinedObjects = [];
		this.outlinePass.selectedObjects = this.outlinedObjects;
		this.outlinePass.edgeStrength = 4.0;
		this.outlinePass.edgeGlow = 1.0;
		this.outlinePass.edgeThickness = 2.0;
		this.outlinePass.visibleEdgeColor.set("#ff00ff");
		this.outlinePass.hiddenEdgeColor.set("#880088");

		this.composer.addPass(this.renderPass);
		this.composer.addPass(this.outlinePass);

		// settings
		this.camera.position.z = 100;
		this.controls.dampingFactory = 0.01;
		this.controls.enableDamping = true;
		this.frameId = null;
		this.hemisphereLight.position.set(0, 1000, 0);
		this.renderer.setPixelRatio(window.devicePixelRatio);
		this.renderer.shadowMap.enabled = true;
		this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
		this.renderer.toneMapping = THREE.ReinhardToneMapping;
		this.renderer.toneMappingExposure = 2.0;
		this.scene.background = new THREE.Color(0x000000);
		this.scene.fog = new THREE.FogExp2(0x000000, 0.00666);

		// structure
		this.container.appendChild(this.canvas);
		this.scene.add(this.ambientLight);
		this.scene.add(this.hemisphereLight);
		this.update();
		window.addEventListener("resize", this.onWindowResize.bind(this), false);
	}

	animate() {
		this.dispatcher.call("beforeRender");
		this.update();
		this.render();
		this.frameId = requestAnimationFrame(this.animate.bind(this));
	}

	addToOutlines(mesh) {
		if (!mesh) {
			return;
		}
		const index = this.outlinedObjects.indexOf(mesh);
		if (index === -1) {
			this.outlinedObjects.push(mesh);
		}
	}

	removeFromOutlines(mesh) {
		if (!mesh) {
			return;
		}
		const index = this.outlinedObjects.indexOf(mesh);
		if (index !== -1) {
			this.outlinedObjects.splice(index, 1);
		}
	}

	on(name, _) {
		if (arguments.length > 1) {
			return this.dispatcher.on(name, _);
		}
		return this.dispatcher.on(name);
	}

	onWindowResize() {
		this.update();
	}

	render() {
		// this.renderer.render(this.scene, this.camera);
		this.composer.render();
	}

	resetCamera() {
		this.camera.position.set(0, 0, 100);
		this.camera.rotation.set(0, 0, 0);
		this.controls.target.set(0, 0, 0);
		this.controls.enableDamping = false;
		this.controls.update();
		this.controls.enableDamping = true;
	}

	start() {
		if (!this.frameId) {
			requestAnimationFrame(this.animate.bind(this));
		}
	}

	stop() {
		if (this.frameId) {
			cancelAnimationFrame(this.frameId);
		}
	}

	update() {
		this.camera.aspect = window.innerWidth / window.innerHeight;
		this.camera.updateProjectionMatrix();
		this.controls.update();
		this.renderer.setPixelRatio(window.devicePixelRatio);
		this.renderer.setSize(window.innerWidth, window.innerHeight);
		this.composer.setSize(window.innerWidth * 2, window.innerHeight * 2);
	}
}

export default SceneManager;
