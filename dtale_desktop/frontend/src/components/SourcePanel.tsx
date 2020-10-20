import React, { Dispatch, useEffect } from "react";
import { DataSource, DataNode } from "../store/state";
import { Action, updateSource, setSelectedSource } from "../store/actions";
import { httpRequest } from "../utils/requests";
import { List, Alert, Collapse, Tag, Popover, Space, Spin, Button } from "antd";
import { SettingOutlined } from "@ant-design/icons";
import {
  ViewTableButton,
  ViewChartsButton,
  ShutdownButton,
} from "./DataNodeActions";

type SourcePanelProps = {
  source: DataSource;
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
      <Popover content={source.error}>
        Error
      </Popover>
    </Tag>
  ) : null;

const LoadMoreButton: React.FC<{
  source: DataSource;
  loadMore: () => void;
}> = ({ source, loadMore }) =>
  source.nodesFullyLoaded || source.loading || source.error ? null : (
    <Button
      size="small"
      onClick={(event) => {
        event.stopPropagation();
        loadMore();
      }}
    >
      Load more
    </Button>
  );

const NodeDescription: React.FC<DataNode> = ({ error, dtaleUrl }) => {
  if (error) {
    return <Alert type="error" message={error} closable />;
  } else if (dtaleUrl) {
    return (
      <a href={dtaleUrl} target="_blank" rel="noopener noreferrer">
        {dtaleUrl}
      </a>
    );
  } else {
    return null;
  }
};

const SourcePanel: React.FC<SourcePanelProps> = ({ source, dispatch }) => {
  const loadMoreNodes = () => {
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

  useEffect(() => {
    if (
      !source.loading &&
      !source.nodesFullyLoaded &&
      !source.error &&
      Object.keys(source.nodes || {}).length === 0
    ) {
      loadMoreNodes();
    }
  });

  return (
    <Collapse.Panel
      key={source.id}
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
        <Button
          icon={<SettingOutlined />}
          onClick={(event) => {
            event.stopPropagation();
            dispatch(setSelectedSource(source));
          }}
        >
          Settings
        </Button>
      }
    >
      <List
        size="small"
        bordered
        dataSource={Object.values(source.nodes || {})}
        renderItem={(node) => (
          <List.Item
            actions={[
              <ViewTableButton dispatch={dispatch} node={node} />,
              <ViewChartsButton dispatch={dispatch} node={node} />,
              <ShutdownButton dispatch={dispatch} node={node} />,
            ]}
          >
            <List.Item.Meta
              title={node.path}
              description={<NodeDescription {...node} />}
            />
          </List.Item>
        )}
      />
    </Collapse.Panel>
  );
};

export default SourcePanel;
