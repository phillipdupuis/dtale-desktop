import { DataNode, DataSource, RootState } from "./state";
import { Action } from "./actions";

const updateSourceNode = (
  source: DataSource,
  updatedNode: DataNode
): DataSource => {
  return {
    ...source,
    nodes: Object.fromEntries(
      Object.entries(source.nodes || {}).map(([k, node]) =>
        node.dataId === updatedNode.dataId ? [k, updatedNode] : [k, node]
      )
    ),
  };
};

export function reducer(state: RootState, action: Action): RootState {
  switch (action.type) {
    case "ADD_SOURCES":
      return {
        ...state,
        sources: [...action.sources, ...(state.sources || [])],
      };
    case "SET_SELECTED_SOURCE":
      return {
        ...state,
        selectedSource: action.source,
      };
    case "UPDATE_SOURCE":
      return {
        ...state,
        sources: state.sources!.map((s) =>
          s.id === action.source.id ? action.source : s
        ),
      };
    case "UPDATE_NODE":
      return {
        ...state,
        sources: state.sources!.map((s) =>
          s.id === action.node.sourceId ? updateSourceNode(s, action.node) : s
        ),
      };
    default:
      return { ...state, sources: state.sources || [] };
  }
}
