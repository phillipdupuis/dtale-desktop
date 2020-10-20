import { DataNode, DataSource } from "./state";

export const ACTION_TYPES = [
  "ADD_SOURCES",
  "SET_SELECTED_SOURCE",
  "UPDATE_SOURCE",
  "UPDATE_NODE",
] as const;

export const addSources = (sources: DataSource[]) => ({
  type: "ADD_SOURCES" as "ADD_SOURCES",
  sources: sources,
});

export const setSelectedSource = (source: DataSource | null) => ({
  type: "SET_SELECTED_SOURCE" as "SET_SELECTED_SOURCE",
  source: source,
});

export const updateSource = (source: DataSource) => ({
  type: "UPDATE_SOURCE" as "UPDATE_SOURCE",
  source: source,
});

export const updateNode = (node: DataNode) => ({
  type: "UPDATE_NODE" as "UPDATE_NODE",
  node: node,
});

export type Action = ReturnType<
  | typeof addSources
  | typeof setSelectedSource
  | typeof updateSource
  | typeof updateNode
>;
