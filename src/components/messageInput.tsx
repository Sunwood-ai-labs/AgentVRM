import { IconButton } from "./iconButton";
import { useRef } from "react";

// 音声状態に対応するアイコンとツールチップを定義
const audioStateMap = {
  uninitialized: { icon: "24/Time", label: "音声未初期化" },
  suspended: { icon: "24/Lock", label: "音声ロック中（画面クリックで有効化）" },
  running: { icon: "24/VolumeUp", label: "音声有効" },
  closed: { icon: "24/VolumeOff", label: "音声エラー" },
};

type Props = {
  userMessage: string;
  isMicRecording: boolean;
  isChatProcessing: boolean;
  onChangeUserMessage: (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => void;
  onClickSendButton: (event: React.MouseEvent<HTMLButtonElement>) => void;
  onClickMicButton: (event: React.MouseEvent<HTMLButtonElement>) => void;
  onAudioFileSelected?: (file: File) => void;
  onOpenSettings: () => void;
  showSubtitle: boolean;
  onToggleSubtitle: () => void;
  audioState: "suspended" | "running" | "closed" | "uninitialized";
};

export const MessageInput = ({
  userMessage,
  isMicRecording,
  isChatProcessing,
  onChangeUserMessage,
  onClickMicButton,
  onClickSendButton,
  onAudioFileSelected,
  onOpenSettings,
  showSubtitle,
  onToggleSubtitle,
  audioState,
}: Props) => {
  const audioFileInputRef = useRef<HTMLInputElement>(null);
  const audioStateObj = audioStateMap[audioState] ?? audioStateMap["uninitialized"];
  const { icon: audioIcon, label: audioLabel } = audioStateObj;

  const handleAudioUploadClick = () => {
    audioFileInputRef.current?.click();
  };

  const handleAudioFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onAudioFileSelected) {
      onAudioFileSelected(file);
    }
    e.target.value = "";
  };

  return (
    <div className="absolute bottom-0 z-20 w-screen">
      <div className="bg-bg-dark/80 backdrop-blur-sm text-text-main">
        <div className="mx-auto max-w-4xl p-4">
          <div className="grid grid-cols-[auto_1fr_auto] gap-4 items-center">
            {/* 左側にアイコン群 */}
            <div className="flex items-center gap-2">
              <IconButton
                iconName="24/Settings"
                isProcessing={false}
                onClick={onOpenSettings}
                title="設定"
              />
              <IconButton
                iconName={showSubtitle ? "24/CommentFill" : "24/CommentOutline"}
                isProcessing={false}
                onClick={onToggleSubtitle}
                title="字幕"
              />
              <span
                title="GitHubリポジトリ"
                className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-gray-800 text-white shadow border-2 border-gray-900"
              >
                <a
                  href="https://github.com/Sunwood-ai-labs/AgentVRM"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center"
                  tabIndex={-1}
                  aria-label="GitHubリポジトリ"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                    <path d="M12 2C6.477 2 2 6.484 2 12.021c0 4.428 2.865 8.184 6.839 9.504.5.092.682-.217.682-.483 0-.237-.009-.868-.014-1.703-2.782.605-3.369-1.342-3.369-1.342-.454-1.154-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.004.07 1.532 1.032 1.532 1.032.892 1.53 2.341 1.088 2.91.832.091-.647.35-1.088.636-1.339-2.221-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.025A9.564 9.564 0 0 1 12 6.844c.85.004 1.705.115 2.504.337 1.909-1.295 2.748-1.025 2.748-1.025.546 1.378.202 2.397.1 2.65.64.7 1.028 1.595 1.028 2.688 0 3.847-2.337 4.695-4.566 4.944.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.749 0 .268.18.579.688.481C19.138 20.2 22 16.447 22 12.021 22 6.484 17.523 2 12 2z"/>
                  </svg>
                </a>
              </span>
              <span className="inline-flex items-center justify-center w-8 h-8 rounded-full">
                {audioState === "uninitialized" ? (
                  <span
                    title={audioLabel}
                    className="inline-flex items-center justify-center w-8 h-8 rounded-full text-yellow-900 font-bold text-2xl shadow border-2"
                    style={{ backgroundColor: "#facc15", borderColor: "#ca8a04" }}
                  >
                    ?
                  </span>
                ) : audioState === "suspended" ? (
                  <span
                    title={audioLabel}
                    className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-amber-500 text-white shadow border-2 border-amber-700"
                  >
                    {/* lock icon */}
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <rect x="4" y="9" width="12" height="7" rx="2" fill="currentColor"/>
                      <rect x="7" y="6" width="6" height="5" rx="3" fill="none" stroke="currentColor" strokeWidth="2"/>
                    </svg>
                  </span>
                ) : audioState === "running" ? (
                  <span
                    title={audioLabel}
                    className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-green-500 text-white shadow border-2 border-green-700"
                  >
                    {/* speaker icon */}
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <path d="M3 8v4h4l5 5V3l-5 5H3z" fill="currentColor"/>
                      <path d="M14.5 7.5a4 4 0 010 5" stroke="currentColor" strokeWidth="2" fill="none"/>
                    </svg>
                  </span>
                ) : audioState === "closed" ? (
                  <span
                    title={audioLabel}
                    className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-gray-500 text-white shadow border-2 border-gray-700"
                  >
                    {/* mute icon */}
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <path d="M3 8v4h4l5 5V3l-5 5H3z" fill="currentColor"/>
                      <line x1="15" y1="7" x2="19" y2="13" stroke="white" strokeWidth="2"/>
                      <line x1="19" y1="7" x2="15" y2="13" stroke="white" strokeWidth="2"/>
                    </svg>
                  </span>
                ) : null}
              </span>
            </div>

            {/* 中央：マイク＋テキスト入力 */}
            <div className="flex-grow flex gap-2">
              <IconButton
                iconName="24/Microphone"
                className="bg-secondary text-text-on-secondary"
                isProcessing={isMicRecording}
                disabled={isChatProcessing}
                onClick={onClickMicButton}
              />
              <input
                type="text"
                placeholder="聞きたいことをいれてね"
                onChange={onChangeUserMessage}
                disabled={isChatProcessing}
                className="bg-bg-light focus:outline-accent disabled:opacity-50 rounded-lg w-full px-4 text-text-main font-bold font-kaisei"
                value={userMessage}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.nativeEvent.isComposing && userMessage) {
                    onClickSendButton(e as any);
                  }
                }}
              />
            </div>

            {/* 右側：送信・アップロード */}
            <div className="flex items-center gap-2">
              <input
                ref={audioFileInputRef}
                type="file"
                accept="audio/*"
                style={{ display: "none" }}
                disabled={isChatProcessing}
                onChange={handleAudioFileChange}
              />
              <IconButton
                iconName="24/Upload"
                className="bg-secondary text-text-on-secondary"
                isProcessing={false}
                disabled={isChatProcessing}
                onClick={handleAudioUploadClick}
                title="音声ファイルアップロード"
              />
              <IconButton
                iconName="24/Send"
                className="bg-secondary text-text-on-secondary"
                isProcessing={isChatProcessing}
                disabled={isChatProcessing || !userMessage}
                onClick={onClickSendButton}
              />
            </div>
          </div>
        </div>
        <div className="py-1 bg-secondary text-center text-text-on-secondary text-xs font-kaisei">
          powered by VRoid, VOICEVOX, ChatGPT API
        </div>
      </div>
    </div>
  );
};
