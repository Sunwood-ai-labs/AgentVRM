import * as THREE from "three";
import { VRM, VRMLoaderPlugin, VRMUtils } from "@pixiv/three-vrm";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import { VRMAnimation } from "../../lib/VRMAnimation/VRMAnimation";
import { VRMLookAtSmootherLoaderPlugin } from "@/lib/VRMLookAtSmootherLoaderPlugin/VRMLookAtSmootherLoaderPlugin";
import { LipSync } from "../lipSync/lipSync";
import { EmoteController } from "../emoteController/emoteController";
import { Screenplay } from "../messages/messages";

/**
 * 3Dキャラクターを管理するクラス
 */
export class Model {
  public vrm?: VRM | null;
  public mixer?: THREE.AnimationMixer;
  public emoteController?: EmoteController;

  private _currentAction?: THREE.AnimationAction;
  private _lookAtTargetParent: THREE.Object3D;
  private _lipSync?: LipSync;

  constructor(lookAtTargetParent: THREE.Object3D) {
    this._lookAtTargetParent = lookAtTargetParent;
    // AudioContext/LipSyncはユーザー操作後に生成する
    this._lipSync = undefined;
  }

  public async loadVRM(url: string): Promise<void> {
    const loader = new GLTFLoader();
    loader.register(
      (parser) =>
        new VRMLoaderPlugin(parser, {
          lookAtPlugin: new VRMLookAtSmootherLoaderPlugin(parser),
        })
    );

    const gltf = await loader.loadAsync(url);

    const vrm = (this.vrm = gltf.userData.vrm);
    vrm.scene.name = "VRMRoot";

    VRMUtils.rotateVRM0(vrm);
    this.mixer = new THREE.AnimationMixer(vrm.scene);

    this.emoteController = new EmoteController(vrm, this._lookAtTargetParent);
  }

  public unLoadVrm() {
    if (this.vrm) {
      VRMUtils.deepDispose(this.vrm.scene);
      this.vrm = null;
    }
  }

  /**
   * VRMアニメーションを読み込む
   *
   * https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_vrm_animation-1.0/README.ja.md
   */
  public async loadAnimation(vrmAnimation: VRMAnimation): Promise<void> {
    const { vrm, mixer } = this;
    if (vrm == null || mixer == null) {
      throw new Error("You have to load VRM first");
    }

    const clip = vrmAnimation.createAnimationClip(vrm);
    const newAction = mixer.clipAction(clip);

    // 前のアニメーションがあれば、0.5秒かけてスムーズに切り替える
    if (this._currentAction) {
      this._currentAction.fadeOut(0.5);
    }

    // 新しいアニメーションを0.5秒かけて再生開始
    newAction.reset().setLoop(THREE.LoopRepeat, Infinity).fadeIn(0.5).play();

    this._currentAction = newAction;
  }

  /**
   * FBXアニメーションクリップを読み込む (新規追加)
   */
  public async loadFbxAnimation(clip: THREE.AnimationClip): Promise<void> {
    const { vrm, mixer } = this;
    if (vrm == null || mixer == null) {
      throw new Error("You have to load VRM first");
    }

    const newAction = mixer.clipAction(clip);

    // 前のアニメーションがあれば、0.5秒かけてスムーズに切り替える
    if (this._currentAction) {
      this._currentAction.fadeOut(0.5);
    }

    // 新しいアニメーションを0.5秒かけて再生開始
    newAction.reset().setLoop(THREE.LoopRepeat, Infinity).fadeIn(0.5).play();

    this._currentAction = newAction;
  }

  /**
   * 音声を再生し、リップシンクを行う
   */
  public async speak(buffer: ArrayBuffer, screenplay: Screenplay) {
    this.emoteController?.playEmotion(screenplay.expression);
    await new Promise((resolve) => {
      this._lipSync?.playFromArrayBuffer(buffer, () => {
        resolve(true);
      });
    });
  }

  // ▼▼▼ ここから追加 ▼▼▼
  public resumeAudio(): void {
    // まだ生成されていなければここで初めてAudioContext/LipSyncを生成
    if (!this._lipSync) {
      this._lipSync = new LipSync(new AudioContext());
    }
    this._lipSync.resume();
  }
  // ▲▲▲ ここまで追加 ▲▲▲

  public update(delta: number): void {
    if (this._lipSync) {
      const { volume } = this._lipSync.update();
      this.emoteController?.lipSync("aa", volume);
    }

    this.emoteController?.update(delta);
    this.mixer?.update(delta);
    this.vrm?.update(delta);
  }
}
