import * as THREE from 'three';
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader.js';
import { mixamoVRMRigMap, MixamoVRMRigMapIndex } from './mixamoVRMRigMap';
import { VRM, VRMHumanBoneName } from '@pixiv/three-vrm';

export function loadMixamoAnimation(url: string, vrm: VRM, initialVrmHipsHeight: number) {
	const loader = new FBXLoader();
	return loader.loadAsync(url).then((asset) => {
		const clip = THREE.AnimationClip.findByName(asset.animations, 'mixamo.com');
		const tracks: any[] = [];

		const restRotationInverse = new THREE.Quaternion();
		const parentRestWorldRotation = new THREE.Quaternion();
		const _quatA = new THREE.Quaternion();
		const _vec3 = new THREE.Vector3();

		const motionHipsHeight = asset.getObjectByName('mixamorigHips')?.position.y;
		// 保存しておいた初期の高さからスケールを計算する
		const hipsPositionScale = initialVrmHipsHeight / motionHipsHeight!;

		clip.tracks.forEach((track) => {
			const trackSplitted = track.name.split('.');
			const mixamoRigName: MixamoVRMRigMapIndex = trackSplitted[0] as MixamoVRMRigMapIndex;
			const vrmBoneName: VRMHumanBoneName = mixamoVRMRigMap[mixamoRigName] as VRMHumanBoneName;
			const vrmNodeName = vrm.humanoid?.getNormalizedBoneNode(vrmBoneName)?.name;
			const mixamoRigNode = asset.getObjectByName(mixamoRigName);

			if (vrmNodeName != null) {
				const propertyName = trackSplitted[1];
				mixamoRigNode?.getWorldQuaternion(restRotationInverse).invert();
				mixamoRigNode?.parent?.getWorldQuaternion(parentRestWorldRotation);

				if (track instanceof THREE.QuaternionKeyframeTrack) {
					for (let i = 0; i < track.values.length; i += 4) {
						const flatQuaternion = track.values.slice(i, i + 4);
						_quatA.fromArray(flatQuaternion);
						_quatA.premultiply(parentRestWorldRotation).multiply(restRotationInverse);
						_quatA.toArray(flatQuaternion);
						flatQuaternion.forEach((v, index) => {
							track.values[index + i] = v;
						});
					}
					tracks.push(
						new THREE.QuaternionKeyframeTrack(
							`${vrmNodeName}.${propertyName}`,
							track.times,
							track.values.map((v, i) => (vrm.meta?.metaVersion === '0' && i % 2 === 0 ? - v : v)),
						),
					);
				} else if (track instanceof THREE.VectorKeyframeTrack) {
					// Hipsボーンの位置トラックの場合、Y軸の移動を無効化して沈み込みを防ぐ
					if (vrmBoneName === 'hips' && propertyName === 'position') {
						const values = track.values.slice(); // 元の値をコピー
						const firstY = values[1]; // 最初のフレームのY値を取得

						// すべてのフレームのY値を最初のフレームの値で固定する
						for (let i = 1; i < values.length; i += 3) {
							values[i] = firstY;
						}
						const scaledValues = values.map((v, i) => (vrm.meta?.metaVersion === '0' && i % 3 !== 1 ? -v : v) * hipsPositionScale);
						tracks.push(new THREE.VectorKeyframeTrack(`${vrmNodeName}.${propertyName}`, track.times, scaledValues));
					} else {
						const value = track.values.map((v, i) => (vrm.meta?.metaVersion === '0' && i % 3 !== 1 ? - v : v) * hipsPositionScale);
						tracks.push(new THREE.VectorKeyframeTrack(`${vrmNodeName}.${propertyName}`, track.times, value));
					}
				}
			}
		});
		return new THREE.AnimationClip('vrmAnimation', clip.duration, tracks);
	});
}
