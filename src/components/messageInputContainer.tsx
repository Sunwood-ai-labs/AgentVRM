import { MessageInput } from "@/components/messageInput";
import { useState, useEffect, useCallback, useContext } from "react";
import { ViewerContext } from "@/features/vrmViewer/viewerContext";

type Props = {
  isChatProcessing: boolean;
  onChatProcessStart: (text: string) => void;
  onOpenSettings: () => void;
  showSubtitle: boolean;
  onToggleSubtitle: () => void;
  audioState: "suspended" | "running" | "closed" | "uninitialized";
};

/**
 * テキスト入力と音声入力を提供する
 *
 * 音声認識の完了時は自動で送信し、返答文の生成中は入力を無効化する
 *
 */
export const MessageInputContainer = ({
  isChatProcessing,
  onChatProcessStart,
  onOpenSettings,
  showSubtitle,
  onToggleSubtitle,
  audioState,
}: Props) => {
  const [userMessage, setUserMessage] = useState("");
  const [speechRecognition, setSpeechRecognition] =
    useState<SpeechRecognition>();
  const [isMicRecording, setIsMicRecording] = useState(false);
  const { viewer } = useContext(ViewerContext);

  // 音声認識の結果を処理する
  const handleRecognitionResult = useCallback(
    (event: SpeechRecognitionEvent) => {
      const text = event.results[0][0].transcript;
      setUserMessage(text);

      // 発言の終了時
      if (event.results[0].isFinal) {
        setUserMessage(text);
        // 返答文の生成を開始
        onChatProcessStart(text);
      }
    },
    [onChatProcessStart]
  );

  // 無音が続いた場合も終了する
  const handleRecognitionEnd = useCallback(() => {
    setIsMicRecording(false);
  }, []);

  const handleClickMicButton = useCallback(() => {
    if (isMicRecording) {
      speechRecognition?.abort();
      setIsMicRecording(false);

      return;
    }

    speechRecognition?.start();
    setIsMicRecording(true);
  }, [isMicRecording, speechRecognition]);

  const handleClickSendButton = useCallback(() => {
    onChatProcessStart(userMessage);
  }, [onChatProcessStart, userMessage]);

  // 音声ファイルがアップロードされた時の処理
  const handleAudioFileSelected = useCallback(async (file: File) => {
    if (!viewer.model) {
      console.error("VRMモデルが読み込まれていません");
      return;
    }

    try {
      // APIにバイナリPOST
      const res = await fetch("/api/speak_external_audio", {
        method: "POST",
        headers: {
          "Content-Type": file.type || "audio/wav",
        },
        body: file,
      });
      
      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }
      
      const buffer = await res.arrayBuffer();

      // ダミーScreenplay
      const dummyScreenplay = {
        expression: "neutral" as const,
        talk: { style: "talk" as const, speakerX: 0, speakerY: 0, message: "" },
      };

      await viewer.model.speak(buffer, dummyScreenplay);
      console.log("音声ファイルの再生が完了しました:", file.name);
    } catch (error) {
      console.error("音声ファイルの処理中にエラーが発生しました:", error);
    }
  }, [viewer.model]);

  useEffect(() => {
    const SpeechRecognition =
      window.webkitSpeechRecognition || window.SpeechRecognition;

    // FirefoxなどSpeechRecognition非対応環境対策
    if (!SpeechRecognition) {
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = "ja-JP";
    recognition.interimResults = true; // 認識の途中結果を返す
    recognition.continuous = false; // 発言の終了時に認識を終了する

    recognition.addEventListener("result", handleRecognitionResult);
    recognition.addEventListener("end", handleRecognitionEnd);

    setSpeechRecognition(recognition);
  }, [handleRecognitionResult, handleRecognitionEnd]);

  useEffect(() => {
    if (!isChatProcessing) {
      setUserMessage("");
    }
  }, [isChatProcessing]);

  return (
    <>
      <MessageInput
        userMessage={userMessage}
        isChatProcessing={isChatProcessing}
        isMicRecording={isMicRecording}
        onChangeUserMessage={(e) => setUserMessage(e.target.value)}
        onClickMicButton={handleClickMicButton}
        onClickSendButton={handleClickSendButton}
        onAudioFileSelected={handleAudioFileSelected}
        onOpenSettings={onOpenSettings}
        showSubtitle={showSubtitle}
        onToggleSubtitle={onToggleSubtitle}
        audioState={audioState}
      />
    </>
  );
};
