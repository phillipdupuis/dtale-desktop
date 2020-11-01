import { Dispatch } from "react";
import { Node, Source, RootState, Settings } from "./state";

export const addSources = (sources: Source[]) => ({
  type: "ADD_SOURCES" as const,
  sources: sources,
});

export const setSelectedSource = (source: Source | null) => ({
  type: "SET_SELECTED_SOURCE" as const,
  source: source,
});

export const updateSource = (source: Source) => ({
  type: "UPDATE_SOURCE" as const,
  source: source,
});

export const updateNode = (node: Node) => ({
  type: "UPDATE_NODE" as const,
  node: node,
});

export const setOpenModal = (modal: RootState["openModal"]) => ({
  type: "SET_OPEN_MODAL" as const,
  modal: modal,
});

export const updateSettings = (settings: Settings) => ({
  type: "UPDATE_SETTINGS" as const,
  settings: settings,
});

export type Action = ReturnType<
  | typeof addSources
  | typeof setSelectedSource
  | typeof updateSource
  | typeof updateNode
  | typeof setOpenModal
  | typeof updateSettings
>;

export type ActionDispatch = Dispatch<Action>;
