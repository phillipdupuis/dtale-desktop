import { RootState, Source, Node } from "./state";

export const getVisibleSources = (state: RootState): Source[] =>
  (state.sources || []).filter((source) => source.visible);

export const getSourceByNode = (state: RootState, node: Node): Source =>
  state.sources!.find((source) => node.dataId in (source.nodes || {}))!;

export const getSourceById = (sources: Source[], id: Source["id"]): Source =>
  sources.find((s) => s.id === id)!;

export const getSourceByNodeId = (
  sources: Source[],
  nodeId: Node["dataId"]
): Source => sources.find((s) => nodeId in (s.nodes || {}))!;

export const getNodeById = (sources: Source[], id: Node["dataId"]): Node =>
  getSourceByNodeId(sources, id).nodes![id];
