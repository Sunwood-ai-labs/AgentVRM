import React, { useContext, useRef } from "react";
import { IconButton } from "./iconButton";
import { ViewerContext } from "@/features/vrmViewer/viewerContext";
import { AssistantText } from "./assistantText";

type Props = {
  assistantMessage: string;
};

export const Menu = ({ assistantMessage }: Props) => {
  return <>{assistantMessage && <AssistantText message={assistantMessage} />}</>;
};
