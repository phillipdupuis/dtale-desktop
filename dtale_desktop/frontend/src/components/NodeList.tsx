import React, { useState } from "react";
import { List, Input, Typography } from "antd";
import { Node, Settings } from "../store/state";
import { ActionDispatch } from "../store/actions";
import { DataViewerButtons, CacheButtons } from "./NodeWidgets";

export const NodeList: React.FC<{
  nodes: Node[];
  settings: Settings;
  dispatch: ActionDispatch;
}> = ({ nodes, settings, dispatch }) => {
  const [filter, setFilter] = useState<string>("");

  const isVisible = (node: Node): boolean =>
    node.visible && (filter === "" || node.path.includes(filter));

  return (
    <List
      size="small"
      header={
        nodes.length < 10 ? null : (
          <Input.Search
            style={{ marginTop: "10px", marginBottom: "10px" }}
            placeholder="filter"
            allowClear
            onSearch={(e) => setFilter(e)}
          />
        )
      }
      bordered
      dataSource={nodes.filter(isVisible)}
      renderItem={(node) => (
        <List.Item
          actions={[
            <DataViewerButtons
              settings={settings}
              dispatch={dispatch}
              node={node}
            />,
          ]}
        >
          <List.Item.Meta
            title={
              <Typography.Text ellipsis style={{ maxWidth: "100%" }}>
                {node.path}
              </Typography.Text>
            }
            description={
              node.error ? (
                <Typography.Text
                  type="danger"
                  strong
                  ellipsis
                  style={{ maxWidth: "100%" }}
                >
                  {node.error}
                </Typography.Text>
              ) : (
                <CacheButtons node={node} dispatch={dispatch} />
              )
            }
          />
        </List.Item>
      )}
    />
  );
};
