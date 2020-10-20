import React, { Dispatch } from "react";
import { DataSource, DataNode } from "../store/state";
import { Action } from "../store/actions";
import { List, Alert } from "antd";
import {
  ViewTableButton,
  ViewChartsButton,
  ShutdownButton,
} from "./DataNodeActions";

type Props = {
  dispatch: Dispatch<Action>;
  source: DataSource;
};

const NodeDescription: React.FC<DataNode> = ({ error, dtaleUrl }) => {
  if (error) {
    return <Alert type="error" message={error} closable />;
  } else if (dtaleUrl) {
    return <a href={dtaleUrl} target="_blank" rel="noopener noreferrer">{dtaleUrl}</a>;
  } else {
    return null;
  }
};

const DataSourceViewer: React.FC<Props> = ({ dispatch, source }) => (
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
);

export default DataSourceViewer;
