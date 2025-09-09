import { useCallback, useContext, useEffect, useState } from "react";
import VrmViewer from "@/components/vrmViewer";
import { ViewerContext } from "@/features/vrmViewer/viewerContext";
import {
  Message,
  textsToScreenplay,
  Screenplay,
} from "@/features/messages/messages";
import { speakCharacterWithVoicevox } from "@/features/messages/speakCharacter";
import { MessageInputContainer } from "@/components/messageInputContainer";
import { SYSTEM_PROMPT } from "@/features/constants/systemPromptConstants";
import { KoeiroParam, DEFAULT_PARAM } from "@/features/constants/koeiroParam";
import { getChatResponseStream } from "@/features/chat/openAiChat";
import { Meta } from "@/components/meta";
import { Settings } from "@/components/settings";
import { ChatLog } from "@/components/chatLog";

import { Subtitle } from "@/components/subtitle";
export default function Home() {
  const { viewer } = useContext(ViewerContext);

  const [systemPrompt, setSystemPrompt] = useState(SYSTEM_PROMPT);
  const [openAiKey, setOpenAiKey] = useState("");
  const [koeiromapKey, setKoeiromapKey] = useState("");
  const [koeiroParam, setKoeiroParam] = useState<KoeiroParam>(DEFAULT_PARAM);
  const [chatProcessing, setChatProcessing] = useState(false);
  const [chatLog, setChatLog] = useState<Message[]>([]);
  const [assistantMessage, setAssistantMessage] = useState("");
  const [isFirstInteraction, setIsFirstInteraction] = useState(true);

  // ★ 字幕state追加
  const [subtitle, setSubtitle] = useState("");

  // ▼▼▼ 追加: 設定・会話ログモーダルの状態管理 ▼▼▼
  const [showSettings, setShowSettings] = useState(false);
  const [showChatLog, setShowChatLog] = useState(false);
  // ▲▲▲

  // ▼▼▼ AudioContext状態監視用 ▼▼▼
  const [audioState, setAudioState] = useState<"suspended" | "running" | "closed" | "uninitialized">("uninitialized");

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    interval = setInterval(() => {
      const state =
        viewer.model && (viewer.model as any)._lipSync && (viewer.model as any)._lipSync.audio
          ? (viewer.model as any)._lipSync.audio.state
          : "uninitialized";
      setAudioState(state);
    }, 500);
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [viewer]);
  // ▲▲▲ AudioContext状態監視用 ▲▲▲

  // ★ WebSocket処理追加
  useEffect(() => {
    if (!viewer.model) return;
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8080";
    const ws = new WebSocket(wsUrl);
    ws.binaryType = "arraybuffer";
    ws.onopen = () => console.log("WebSocket接続");
    ws.onclose = () => console.log("WebSocket切断");

    ws.onmessage = async (event) => {
      if (typeof event.data === 'string') {
        // JSON形式のメッセージ（テキストと音声データ）を処理
        try {
          const messageData = JSON.parse(event.data);
          if (messageData.type === 'speak' && messageData.audio && messageData.text) {
            setSubtitle(messageData.text);

            const base64 = messageData.audio.split(",")[1];
            const binary = atob(base64);
            const len = binary.length;
            const buffer = new Uint8Array(len);
            for (let i = 0; i < len; i++) buffer[i] = binary.charCodeAt(i);

            const dummyScreenplay = {
              expression: "neutral" as const,
              talk: { style: "talk" as const, speakerX: 0, speakerY: 0, message: messageData.text },
            };
            await viewer.model!.speak(buffer.buffer, dummyScreenplay);

            setSubtitle(""); // 再生完了後に字幕を消す
          } else if (messageData.type === 'play_animation' && messageData.name) {
            // アニメーション再生メッセージを処理
            const animation = messageData.name;
            const fileType = animation.split('.').pop()?.toLowerCase();
            if (fileType === 'vrma') {
              viewer.playVrma(animation);
            } else if (fileType === 'fbx') {
              viewer.playFbx(animation);
            }
          }
        } catch (error) {
          console.error("WebSocketメッセージの解析に失敗:", error);
        }
      } else if (event.data instanceof ArrayBuffer) {
        // バイナリデータ（音声のみ）を処理
        const buffer = event.data;
        const dummyScreenplay = {
          expression: "neutral" as const,
          talk: { style: "talk" as const, speakerX: 0, speakerY: 0, message: "" },
        };
        await viewer.model!.speak(buffer, dummyScreenplay);
      }
    };

    return () => ws.close();
  }, [viewer, viewer.model]);

  useEffect(() => {
    if (window.localStorage.getItem("chatVRMParams")) {
      const params = JSON.parse(
        window.localStorage.getItem("chatVRMParams") as string
      );
      setSystemPrompt(params.systemPrompt ?? SYSTEM_PROMPT);
      setKoeiroParam(params.koeiroParam ?? DEFAULT_PARAM);
      setChatLog(params.chatLog ?? []);
    }
  }, []);

  useEffect(() => {
    process.nextTick(() =>
      window.localStorage.setItem(
        "chatVRMParams",
        JSON.stringify({ systemPrompt, koeiroParam, chatLog })
      )
    );
  }, [systemPrompt, koeiroParam, chatLog]);

  const handleChangeChatLog = useCallback(
    (targetIndex: number, text: string) => {
      const newChatLog = chatLog.map((v: Message, i) => {
        return i === targetIndex ? { role: v.role, content: text } : v;
      });

      setChatLog(newChatLog);
    },
    [chatLog]
  );

  /**
   * 文ごとに音声を直列でリクエストしながら再生する
   */
  const handleSpeakAi = useCallback(
    async (
      screenplay: Screenplay,
      onStart?: () => void,
      onEnd?: () => void
    ) => {
      console.log("[DEBUG] handleSpeakAi called", screenplay);
      // VOICEVOXで喋らせる
      speakCharacterWithVoicevox(screenplay, viewer, { speakerId: 1, speedScale: 1.0 }, onStart, onEnd);
    },
    [viewer, koeiromapKey]
  );

  /**
   * アシスタントとの会話を行う
   */
  const handleSendChat = useCallback(
    async (text: string) => {

      // 最初のインタラクションでAudioContextを再開する
      if (isFirstInteraction) {
        viewer.resumeAudio();
        setIsFirstInteraction(false);
      }

      if (!openAiKey) {
        setAssistantMessage("APIキーが入力されていません");
        return;
      }
      const newMessage = text;
      if (newMessage == null) return;

      setChatProcessing(true);
      const messageLog: Message[] = [
        ...chatLog,
        { role: "user", content: newMessage },
      ];
      setChatLog(messageLog);

      const messages: Message[] = [
        {
          role: "system",
          content: systemPrompt,
        },
        ...messageLog,
      ];

      const stream = await getChatResponseStream(messages, openAiKey).catch(
        (e) => {
          console.error(e);
          return null;
        }
      );
      if (stream == null) {
        setChatProcessing(false);
        return;
      }

      const reader = stream.getReader();
      let receivedMessage = "";
      let aiTextLog = "";
      let tag = "";
      const sentences = new Array<string>();
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          receivedMessage += value;

          const tagMatch = receivedMessage.match(/^\[(.*?)\]/);
          if (tagMatch && tagMatch[0]) {
            tag = tagMatch[0];
            receivedMessage = receivedMessage.slice(tag.length);
          }

          const sentenceMatch = receivedMessage.match(
            /^(.+[。．！？\n]|.{10,}[、,])/
          );
          if (sentenceMatch && sentenceMatch[0]) {
            const sentence = sentenceMatch[0];
            sentences.push(sentence);
            receivedMessage = receivedMessage
              .slice(sentence.length)
              .trimStart();

            if (
              !sentence.replace(
                /^[\s\[\(\{「［（【『〈《〔｛«‹〘〚〛〙›»〕》〉』】）］」\}\)\]]+$/g,
                ""
              )
            ) {
              continue;
            }

            const aiText = `${tag} ${sentence}`;
            const aiTalks = textsToScreenplay([aiText], koeiroParam);
            aiTextLog += aiText;

            const currentAssistantMessage = sentences.join(" ");
            // ★ 字幕表示: 再生開始時にsetSubtitle、awaitで消去
            await speakCharacterWithVoicevox(
              aiTalks[0],
              viewer,
              { speakerId: 1, speedScale: 1.0 },
              () => {
                setAssistantMessage(currentAssistantMessage);
                setSubtitle(aiTalks[0].talk.message);
              }
            );
          }
        }
      } catch (e) {
        setChatProcessing(false);
        console.error(e);
      } finally {
        reader.releaseLock();
        setSubtitle(""); // 全ての発話が終わったら字幕を消す
      }

      const messageLogAssistant: Message[] = [
        ...messageLog,
        { role: "assistant", content: aiTextLog },
      ];

      setChatLog(messageLogAssistant);
      setChatProcessing(false);
    },
    [systemPrompt, chatLog, openAiKey, koeiroParam, viewer, isFirstInteraction]
  );

  return (
    <div
      className={"font-kaisei"}
      onClick={() => {
        if (isFirstInteraction) {
          viewer.resumeAudio();
          setIsFirstInteraction(false);
        }
      }}
    >
      <Meta />
      <VrmViewer />
      {/* ★ 字幕コンポーネント追加 */}
      <Subtitle text={subtitle} />
      <MessageInputContainer
        isChatProcessing={chatProcessing}
        onChatProcessStart={handleSendChat}
        onOpenSettings={() => setShowSettings(true)}
        onOpenChatLog={() => setShowChatLog((v) => !v)}
        isChatLogOpen={showChatLog}
        chatLogCount={chatLog.length}
        audioState={audioState}
      />
      {showSettings && (
        <Settings
          openAiKey={openAiKey}
          chatLog={chatLog}
          systemPrompt={systemPrompt}
          koeiroParam={koeiroParam}
          koeiromapKey={koeiromapKey}
          onClickClose={() => setShowSettings(false)}
          onChangeAiKey={(e) => setOpenAiKey(e.target.value)}
          onChangeSystemPrompt={(e) => setSystemPrompt(e.target.value)}
          onChangeChatLog={handleChangeChatLog}
          onChangeKoeiroParam={(x, y) => setKoeiroParam({ speakerX: x, speakerY: y })}
          onClickOpenVrmFile={() => {}} // 必要に応じて実装
          onClickResetChatLog={() => setChatLog([])}
          onClickResetSystemPrompt={() => setSystemPrompt(SYSTEM_PROMPT)}
          onChangeKoeiromapKey={(e) => setKoeiromapKey(e.target.value)}
        />
      )}
      {showChatLog && <ChatLog messages={chatLog} />}
    </div>
  );
}
