import { RootState, DataSource, DataNode } from "./state";


export const getVisibleSources = (state: RootState): DataSource[] => (
  (state.sources || []).filter((source) => source.visible)
);

export const getSourceByNode = (state: RootState, node: DataNode): DataSource => (
  state.sources!.find((source) => node.dataId in (source.nodes || {}))!
);

export const getSourceByNodeDataId = (state: RootState, dataId: DataNode["dataId"]): DataSource => (
  state.sources!.find((source) => dataId in (source.nodes || {}))!
);


