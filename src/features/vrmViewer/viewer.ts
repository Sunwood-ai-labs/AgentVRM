import * as THREE from "three";
import { Model } from "./model";
import { loadVRMAnimation } from "@/lib/VRMAnimation/loadVRMAnimation";
import { buildUrl } from "@/utils/buildUrl";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import { loadMixamoAnimation } from "@/lib/fbxAnimation/loadMixamoAnimation";

/**
 * three.jsを使った3Dビューワー
 *
 * setup()でcanvasを渡してから使う
 */
export class Viewer {
  public isReady: boolean;
  public model?: Model;

  private _renderer?: THREE.WebGLRenderer;
  private _clock: THREE.Clock;
  private _scene: THREE.Scene;
  private _camera?: THREE.PerspectiveCamera;
  private _cameraControls?: OrbitControls;
  private _initialHipsHeight: number = 0; // VRMモデルの初期の腰の高さを保存するプロパティ

  constructor() {
    this.isReady = false;

    // scene
    const scene = new THREE.Scene();
    this._scene = scene;

    // light
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
    directionalLight.position.set(1.0, 1.0, 1.0).normalize();
    scene.add(directionalLight);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    // animate
    this._clock = new THREE.Clock();
    this._clock.start();
  }

  public async loadVrm(url: string) {
    if (this.model?.vrm) {
      this.unloadVRM();
    }

    // gltf and vrm
    this.model = new Model(this._camera || new THREE.Object3D());
    await this.model.loadVRM(url);
    if (!this.model?.vrm) return;

    // アニメーションを適用する前に、初期の腰の高さを計算して保存する
    const vrm = this.model.vrm;
    // updateMatrixWorldを呼ばないと正しいワールド座標が取れない
    vrm.scene.updateMatrixWorld(true);
    const vrmHipsNode = vrm.humanoid?.getNormalizedBoneNode('hips');
    if (vrmHipsNode) {
      const _vec3 = new THREE.Vector3();
      const vrmHipsY = vrmHipsNode.getWorldPosition(_vec3).y;
      const vrmRootY = vrm.scene.getWorldPosition(_vec3).y;
      this._initialHipsHeight = Math.abs(vrmHipsY - vrmRootY);
    } else {
        // Hipsが見つからない場合は警告を出す
        console.warn("Could not find Hips bone. Falling back to default height.");
        this._initialHipsHeight = 1.0; // 仮のデフォルト値
    }

    // Disable frustum culling
    this.model.vrm.scene.traverse((obj) => {
      obj.frustumCulled = false;
    });

    this._scene.add(this.model.vrm.scene);

    // 環境変数から初期モーションを読み込む
    const motionFileName =
      process.env.NEXT_PUBLIC_MOTION_FILENAME || "/idle_loop.vrma";
    const motionUrl = buildUrl(motionFileName);
    const fileType = motionFileName.split(".").pop()?.toLowerCase();

    if (fileType === "vrma") {
      const vrma = await loadVRMAnimation(motionUrl);
      if (vrma) this.model.loadAnimation(vrma);
    } else if (fileType === "fbx") {
      try {
        const clip = await loadMixamoAnimation(motionUrl, this.model.vrm, this._initialHipsHeight);
        if (clip) {
          await this.model.loadFbxAnimation(clip);
        }
      } catch (error) {
        console.error(
          `Failed to load initial FBX animation: ${motionFileName}`,
          error
        );
        // フォールバックとしてidle_loopを試す
        const fallbackVrma = await loadVRMAnimation(
          buildUrl("/idle_loop.vrma")
        );
        if (fallbackVrma) this.model.loadAnimation(fallbackVrma);
      }
    } else {
      // デフォルトのアイドルモーションを読み込む
      const defaultVrma = await loadVRMAnimation(
        buildUrl("/idle_loop.vrma")
      );
      if (defaultVrma) this.model.loadAnimation(defaultVrma);
    }

    // HACK: アニメーションの原点がずれているので再生後にカメラ位置を調整する
    requestAnimationFrame(() => {
      this.resetCamera();
    });
  }

  public unloadVRM(): void {
    if (this.model?.vrm) {
      this._scene.remove(this.model.vrm.scene);
      this.model?.unLoadVrm();
    }
  }

  /**
   * VRMAアニメーションを再生する (新規追加)
   * @param url vrmaファイルのURL
   */
  public async playVrma(url: string) {
    if (!this.model?.vrm) return;

    const vrma = await loadVRMAnimation(url);
    if (vrma) {
      await this.model.loadAnimation(vrma);
    }
  }

  /**
   * FBXアニメーションを再生する (新規追加)
   * @param url fbxファイルのURL
   */
  public async playFbx(url: string) {
    if (!this.model?.vrm) return;

    try {
      const clip = await loadMixamoAnimation(url, this.model.vrm, this._initialHipsHeight);
      if (clip) {
        await this.model.loadFbxAnimation(clip);
      }
    } catch (error) {
      console.error("Failed to load FBX animation:", error);
    }
  }

  // ▼▼▼ ここから追加 ▼▼▼
  public resumeAudio(): void {
    this.model?.resumeAudio();
  }
  // ▲▲▲ ここまで追加 ▲▲▲

  /**
   * Reactで管理しているCanvasを後から設定する
   */
  public setup(canvas: HTMLCanvasElement) {
    const parentElement = canvas.parentElement;
    const width = parentElement?.clientWidth || canvas.width;
    const height = parentElement?.clientHeight || canvas.height;
    // renderer
    this._renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      alpha: true,
      antialias: true,
    });
    this._renderer.outputEncoding = THREE.sRGBEncoding;
    this._renderer.setSize(width, height);
    this._renderer.setPixelRatio(window.devicePixelRatio);

    // camera
    this._camera = new THREE.PerspectiveCamera(20.0, width / height, 0.1, 20.0);
    this._camera.position.set(0, 1.3, 1.5);
    this._cameraControls?.target.set(0, 1.3, 0);
    this._cameraControls?.update();
    // camera controls
    this._cameraControls = new OrbitControls(
      this._camera,
      this._renderer.domElement
    );
    this._cameraControls.screenSpacePanning = true;
    this._cameraControls.update();

    window.addEventListener("resize", () => {
      this.resize();
    });
    this.isReady = true;
    this.update();
  }

  /**
   * canvasの親要素を参照してサイズを変更する
   */
  public resize() {
    if (!this._renderer) return;

    const parentElement = this._renderer.domElement.parentElement;
    if (!parentElement) return;

    this._renderer.setPixelRatio(window.devicePixelRatio);
    this._renderer.setSize(
      parentElement.clientWidth,
      parentElement.clientHeight
    );

    if (!this._camera) return;
    this._camera.aspect =
      parentElement.clientWidth / parentElement.clientHeight;
    this._camera.updateProjectionMatrix();
  }

  /**
   * VRMのheadノードを参照してカメラ位置を調整する
   */
  public resetCamera() {
    const headNode = this.model?.vrm?.humanoid.getNormalizedBoneNode("head");

    if (headNode) {
      const headWPos = headNode.getWorldPosition(new THREE.Vector3());
      this._camera?.position.set(
        this._camera.position.x,
        headWPos.y,
        this._camera.position.z
      );
      this._cameraControls?.target.set(headWPos.x, headWPos.y, headWPos.z);
      this._cameraControls?.update();
    }
  }

  public update = () => {
    requestAnimationFrame(this.update);
    const delta = this._clock.getDelta();
    // update vrm components
    if (this.model) {
      this.model.update(delta);
    }

    if (this._renderer && this._camera) {
      this._renderer.render(this._scene, this._camera);
    }
  };
}
