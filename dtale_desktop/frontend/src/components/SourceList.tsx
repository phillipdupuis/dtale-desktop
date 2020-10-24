import React, { Dispatch, useEffect } from "react";
import { DataSource, DataNode } from "../store/state";
import {
  Action,
  updateSource,
  setSelectedSource,
  updateNode,
} from "../store/actions";
import { httpRequest } from "../utils/requests";
import { List, Alert, Collapse, Tag, Popover, Space, Spin, Button } from "antd";
import {
  SettingOutlined,
} from "@ant-design/icons";
import {
  ViewTableButton,
  ViewChartsButton,
  ShutdownButton,
} from "./DataNodeActions";

type SourceListProps = {
  sources: DataSource[];
  dispatch: Dispatch<Action>;
};

const NumResultsTag: React.FC<{ source: DataSource }> = ({ source }) => (
  <Tag>
    {source.loading ? (
      <Spin size="small" />
    ) : (
      `${Object.keys(source.nodes || {}).length} results`
    )}
  </Tag>
);

const NumActiveTag: React.FC<{ source: DataSource }> = ({ source }) => {
  const numActive: number = Object.values(source.nodes || {}).filter(
    (node) => node.dtaleUrl
  ).length;
  return numActive === 0 ? null : (
    <Tag color="green">{`${numActive} active`}</Tag>
  );
};

const ErrorTag: React.FC<{ source: DataSource }> = ({ source }) =>
  source.error ? (
    <Tag color="error">
      <Popover content={source.error}>Error</Popover>
    </Tag>
  ) : null;

const LoadMoreButton: React.FC<{
  source: DataSource;
  loadMore: (source: DataSource) => void;
}> = ({ source, loadMore }) =>
  source.nodesFullyLoaded || source.loading || source.error ? null : (
    <Button
      size="small"
      onClick={(event) => {
        event.stopPropagation();
        loadMore(source);
      }}
    >
      Load more
    </Button>
  );

const NodeDescription: React.FC<{
  node: DataNode;
  dispatch: Dispatch<Action>;
}> = ({ node, dispatch }) => {
  if (node.error) {
    return (
      <Alert
        type="error"
        message={node.error}
        closable
        onClose={() => dispatch(updateNode({ ...node, error: undefined }))}
      />
    );
  } else if (node.dtaleUrl) {
    return (
      <a href={node.dtaleUrl} target="_blank" rel="noopener noreferrer">
        {node.dtaleUrl}
      </a>
    );
  } else {
    return null;
  }
};

const SourceList: React.FC<SourceListProps> = ({
  sources,
  dispatch,
}) => {
  const loadMoreNodes = (source: DataSource) => {
    dispatch(updateSource({ ...source, loading: true }));
    httpRequest({
      method: "POST",
      url: "/source/nodes/list/",
      body: source,
      resolve: (data) => dispatch(updateSource({ ...data, loading: false })),
      reject: (error) =>
        dispatch(updateSource({ ...source, loading: false, error: error })),
    });
  };

  const nodeIsVisible = (node: DataNode): boolean => node.visible;

  const sourceIsVisible = (source: DataSource): boolean => source.visible;

  useEffect(() => {
    sources.forEach((source) => {
      if (
        !source.loading &&
        !source.nodesFullyLoaded &&
        !source.error &&
        Object.keys(source.nodes || {}).length === 0
      ) {
        loadMoreNodes(source);
      }
    });
  });

  return (
    <Collapse defaultActiveKey={[]}>
      {sources.filter(sourceIsVisible).map((source) => (
        <Collapse.Panel
          key={source.id}
          style={source.visible ? {} : { color: "lightgray" }}
          disabled={source.loading}
          header={
            <Space>
              <span>{source.name}</span>
              <NumResultsTag source={source} />
              <NumActiveTag source={source} />
              <ErrorTag source={source} />
              <LoadMoreButton source={source} loadMore={loadMoreNodes} />
            </Space>
          }
          extra={
            <Space>
              <Button
                icon={<SettingOutlined />}
                onClick={(event) => {
                  event.stopPropagation();
                  dispatch(setSelectedSource(source));
                }}
              >
                Settings
              </Button>
            </Space>
          }
        >
          <List
            size="small"
            bordered
            dataSource={Object.values(source.nodes || {}).filter(nodeIsVisible)}
            renderItem={(node) => (
              <List.Item
                actions={[
                  <ShutdownButton dispatch={dispatch} node={node} />,
                  <ViewTableButton dispatch={dispatch} node={node} />,
                  <ViewChartsButton dispatch={dispatch} node={node} />,
                ]}
              >
                <List.Item.Meta
                  title={node.path}
                  description={
                    <NodeDescription node={node} dispatch={dispatch} />
                  }
                />
              </List.Item>
            )}
          />
        </Collapse.Panel>
      ))}
    </Collapse>
  );
};

export default SourceList;
