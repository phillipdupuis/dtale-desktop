import React, { useState, useEffect, Dispatch } from "react";
import { Modal, Tree } from "antd";
import { httpRequest } from "../utils/requests";
import { updateSource, setOpenModal, Action } from "../store/actions";
import { DataSource, RootState, DataNode } from "../store/state";

type VisibilityChanges = {
  showSources: DataSource[];
  hideSources: DataSource[];
  showNodes: DataNode[];
  hideNodes: DataNode[];
};

const sourceKeyPrefix = "___source___";
const nodeKeyPrefix = "___node___";

const makeSourceKey = (source: DataSource): string =>
  `${sourceKeyPrefix}${source.id}`;

const makeNodeKey = (node: DataNode): string =>
  `${nodeKeyPrefix}${node.dataId}`;

const isSourceKey = (key: string): boolean => key.startsWith(sourceKeyPrefix);

const isNodeKey = (key: string): boolean => key.startsWith(nodeKeyPrefix);

const getSourceByKey = (state: RootState, key: string): DataSource => {
  const sourceId = key.slice(sourceKeyPrefix.length);
  return (state.sources || []).find((s) => s.id === sourceId)!;
};

const getNodeByKey = (state: RootState, key: string): DataNode => {
  const nodeDataId = key.slice(nodeKeyPrefix.length);
  return state.sources!.find((s) => nodeDataId in (s.nodes || {}))!.nodes![
    nodeDataId
  ];
};

const sourcesToHide = (
  state: RootState,
  defaultCheckedKeys: string[],
  checkedKeys: string[]
): DataSource[] =>
  defaultCheckedKeys
    .filter((k) => isSourceKey(k) && !checkedKeys.includes(k))
    .map((k) => getSourceByKey(state, k));

const sourcesToShow = (
  state: RootState,
  defaultCheckedKeys: string[],
  checkedKeys: string[]
): DataSource[] =>
  checkedKeys
    .filter((k) => isSourceKey(k) && !defaultCheckedKeys.includes(k))
    .map((k) => getSourceByKey(state, k));

const nodesToHide = (
  state: RootState,
  defaultCheckedKeys: string[],
  checkedKeys: string[]
): DataNode[] =>
  defaultCheckedKeys
    .filter((k) => isNodeKey(k) && !checkedKeys.includes(k))
    .map((k) => getNodeByKey(state, k));

const nodesToShow = (
  state: RootState,
  defaultCheckedKeys: string[],
  checkedKeys: string[]
): DataNode[] =>
  checkedKeys
    .filter((k) => isNodeKey(k) && !defaultCheckedKeys.includes(k))
    .map((k) => getNodeByKey(state, k));

const getVisibilityChanges = (
  state: RootState,
  initialKeys: string[],
  currentKeys: string[]
): VisibilityChanges => ({
  showSources: sourcesToShow(state, initialKeys, currentKeys),
  hideSources: sourcesToHide(state, initialKeys, currentKeys),
  showNodes: nodesToShow(state, initialKeys, currentKeys),
  hideNodes: nodesToHide(state, initialKeys, currentKeys),
});

const getDefaultCheckedKeys = (state: RootState): string[] => {
  const keys: string[] = [];
  (state.sources || [])
    .filter((source) => source.visible)
    .forEach((source) => {
      keys.push(makeSourceKey(source));
      Object.values(source.nodes || {})
        .filter((node) => node.visible)
        .forEach((node) => {
          keys.push(makeNodeKey(node));
        });
    });
  return keys;
};

const getTreeData = (state: RootState) =>
  (state.sources || []).map((source) => ({
    title: source.name,
    key: makeSourceKey(source),
    isLeaf: Object.keys(source.nodes || {}).length === 0 ? true : false,
    children: Object.values(source.nodes || {}).map((node) => ({
      title: node.path,
      key: makeNodeKey(node),
      isLeaf: true,
    })),
  }));

const splitIntoCheckedAndHalfChecked = (
  state: RootState,
  keys: string[]
): { checked: string[]; halfChecked: string[] } => {
  const checked: string[] = [];
  const halfChecked: string[] = [];
  keys.forEach((key) => {
    if (isNodeKey(key)) {
      checked.push(key);
    } else {
      const source = getSourceByKey(state, key);
      if (Object.values(source.nodes || {}).every((node) => node.visible)) {
        checked.push(key);
      } else {
        halfChecked.push(key);
      }
    }
  });
  return { checked: checked, halfChecked: halfChecked };
};

const Filters: React.FC<{ state: RootState; dispatch: Dispatch<Action> }> = ({
  state,
  dispatch,
}) => {
  const [defaultCheckedKeys, setDefaultCheckedKeys] = useState<string[]>([]);
  const [currentCheckedKeys, setCurrentCheckedKeys] = useState<string[]>([]);

  useEffect(() => {
    const keys = getDefaultCheckedKeys(state);
    setDefaultCheckedKeys(keys);
    setCurrentCheckedKeys(keys);
  }, [state.openModal]);

  const onClickOk = () => {
    const changes = getVisibilityChanges(
      state,
      defaultCheckedKeys,
      currentCheckedKeys
    );
    httpRequest({
      method: "POST",
      url: "/update-filters/",
      body: {
        showSources: changes.showSources.map((s) => s.id),
        hideSources: changes.hideSources.map((s) => s.id),
        showNodes: changes.showNodes.map((n) => n.dataId),
        hideNodes: changes.hideNodes.map((n) => n.dataId),
      },
      resolve: (sources: DataSource[]) => {
        sources.forEach((source) => {
          dispatch(updateSource(source));
        });
      },
      reject: (error) => null,
      onFinish: () => dispatch(setOpenModal(null)),
    });
  };

  return (
    <Modal
      visible={state.openModal === "filters"}
      title="Visible Sources"
      onCancel={() => dispatch(setOpenModal(null))}
      destroyOnClose={true}
      width={"90%"}
      bodyStyle={{ height: "80vh" }}
      centered
      onOk={() => onClickOk()}
    >
      <Tree
        treeData={getTreeData(state)}
        // @ts-ignore
        defaultCheckedKeys={splitIntoCheckedAndHalfChecked(
          state,
          defaultCheckedKeys
        )}
        blockNode={true}
        checkable={true}
        onCheck={(k, e) => {
          setCurrentCheckedKeys([
            ...(k as string[]),
            ...(e.halfCheckedKeys || []),
          ] as string[]);
        }}
      />
    </Modal>
  );
};

export default Filters;
