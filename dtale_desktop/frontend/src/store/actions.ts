import { DataNode, DataSource, RootState } from "./state";

export const ACTION_TYPES = [
  "ADD_SOURCES",
  "SET_SELECTED_SOURCE",
  "UPDATE_SOURCE",
  "UPDATE_NODE",
  "SET_OPEN_MODAL",
] as const;

export const addSources = (sources: DataSource[]) => ({
  type: "ADD_SOURCES" as const,
  sources: sources,
});

export const setSelectedSource = (source: DataSource | null) => ({
  type: "SET_SELECTED_SOURCE" as const,
  source: source,
});

export const updateSource = (source: DataSource) => ({
  type: "UPDATE_SOURCE" as const,
  source: source,
});

export const updateNode = (node: DataNode) => ({
  type: "UPDATE_NODE" as const,
  node: node,
});

export const setOpenModal = (modal: RootState["openModal"]) => ({
  type: "SET_OPEN_MODAL" as const,
  modal: modal, 
});

export type Action = ReturnType<
  | typeof addSources
  | typeof setSelectedSource
  | typeof updateSource
  | typeof updateNode
  | typeof setOpenModal
>;
