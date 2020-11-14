import { Source, RootState } from "./state";
import { Action, SourceAction, NodeAction } from "./actions";
import { getSourceById, getSourceByNodeId } from "./selectors";

const nodesReducer = (
  nodes: Source["nodes"],
  action: NodeAction
): Source["nodes"] => {
  switch (action.type) {
    case "UPDATE_NODE":
      return Object.fromEntries(
        Object.entries(nodes!).map(([k, node]) => [
          k,
          node.dataId === action.node.dataId ? action.node : node,
        ])
      );
    case "SET_NODE_UPDATING":
      return Object.fromEntries(
        Object.entries(nodes!).map(([k, node]) => [
          k,
          node.dataId === action.dataId
            ? { ...node, updating: action.updating }
            : node,
        ])
      );
    default:
      return nodes;
  }
};

// sortSources is needed b/c array.sort sorts in-place, so react components don't know if it changes.
const sortedSources = (sources: Source[]): Source[] =>
  [...sources].sort((s1: Source, s2: Source) => s1.sortValue! - s2.sortValue!);

const sourceListReducer = (
  sources: RootState["sources"],
  action: SourceAction
): RootState["sources"] => {
  switch (action.type) {
    case "ADD_SOURCES":
      return sortedSources(action.sources.concat(sources || []));
    case "UPDATE_SOURCE":
      return sortedSources(
        sources!.map((s) => (s.id === action.source.id ? action.source : s))
      );
    case "SET_SOURCE_UPDATING":
      const updatedSource = {
        ...getSourceById(sources!, action.sourceId),
        updating: action.updating,
      };
      return sources!.map((s) =>
        s.id === action.sourceId ? updatedSource : s
      );
    case "UPDATE_NODE":
      return sources!.map((s) =>
        s.id === action.node.sourceId
          ? { ...s, nodes: nodesReducer(s.nodes, action) }
          : s
      );
    case "SET_NODE_UPDATING":
      const sourceId = getSourceByNodeId(sources!, action.dataId).id;
      return sources!.map((s) =>
        s.id === sourceId ? { ...s, nodes: nodesReducer(s.nodes, action) } : s
      );
    default:
      return sources;
  }
};

export const reducer = (state: RootState, action: Action): RootState => {
  switch (action.type) {
    case "UPDATE_SETTINGS":
      return { ...state, settings: action.settings };
    case "SET_OPEN_MODAL":
      return { ...state, openModal: action.modal };
    case "SET_SELECTED_SOURCE":
      return { ...state, selectedSource: action.source };
    default:
      return { ...state, sources: sourceListReducer(state.sources, action) };
  }
};
