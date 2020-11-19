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

export const setSourceUpdating = (
  sourceId: Source["id"],
  updating: boolean
) => ({
  type: "SET_SOURCE_UPDATING" as const,
  sourceId: sourceId,
  updating: updating,
});

export const updateNode = (node: Node) => ({
  type: "UPDATE_NODE" as const,
  node: node,
});

export const setNodeUpdating = (dataId: Node["dataId"], updating: boolean) => ({
  type: "SET_NODE_UPDATING" as const,
  dataId: dataId,
  updating: updating,
});

export const setOpenModal = (modal: RootState["openModal"]) => ({
  type: "SET_OPEN_MODAL" as const,
  modal: modal,
});

export const updateSettings = (settings: Settings) => ({
  type: "UPDATE_SETTINGS" as const,
  settings: settings,
});

export type NodeAction = ReturnType<typeof updateNode | typeof setNodeUpdating>;

export type SourceAction =
  | ReturnType<
      typeof addSources | typeof updateSource | typeof setSourceUpdating
    >
  | NodeAction;

export type Action =
  | ReturnType<
      typeof setSelectedSource | typeof setOpenModal | typeof updateSettings
    >
  | SourceAction;

export type ActionDispatch = Dispatch<Action>;
