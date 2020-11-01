import { Node, Source, RootState } from "./state";
import { Action } from "./actions";

const updateSourceNode = (source: Source, updatedNode: Node): Source => {
  return {
    ...source,
    nodes: Object.fromEntries(
      Object.entries(source.nodes || {}).map(([k, node]) =>
        node.dataId === updatedNode.dataId ? [k, updatedNode] : [k, node]
      )
    ),
  };
};

// sortSources is needed b/c array.sort sorts in-place, so react components don't know if it changes.
const sortedSources = (sources: Source[]): Source[] =>
  [...sources].sort((s1: Source, s2: Source) => s1.sortValue! - s2.sortValue!);

export const reducer = (state: RootState, action: Action): RootState => {
  switch (action.type) {
    case "ADD_SOURCES":
      return {
        ...state,
        sources: sortedSources(action.sources.concat(state.sources || [])),
      };
    case "SET_SELECTED_SOURCE":
      return {
        ...state,
        selectedSource: action.source,
      };
    case "UPDATE_SOURCE":
      return {
        ...state,
        sources: sortedSources(
          state.sources!.map((s) =>
            s.id === action.source.id ? action.source : s
          )
        ),
      };
    case "UPDATE_NODE":
      return {
        ...state,
        sources: state.sources!.map((s) =>
          s.id === action.node.sourceId ? updateSourceNode(s, action.node) : s
        ),
      };
    case "SET_OPEN_MODAL":
      return {
        ...state,
        openModal: action.modal,
      };
    case "UPDATE_SETTINGS":
      return {
        ...state,
        settings: action.settings,
      };
    default:
      return { ...state, sources: state.sources || [] };
  }
};
