import React, { Dispatch, useState } from "react";
import { DataNode } from "../store/state";
import { updateNode } from "../store/actions";
import { Button } from "antd";
import { httpRequest, openNewTab } from "../utils/requests";
import {
  LineChartOutlined,
  TableOutlined,
  PoweroffOutlined,
} from "@ant-design/icons";

const ViewButton: React.FC<{
  dispatch: Dispatch<any>;
  node: DataNode;
  page: "table" | "charts";
}> = ({ dispatch, node, page = "table" }) => {
  const [loading, setLoading] = useState<boolean>(false);
  return (
    <Button
      onClick={() => {
        httpRequest({
          method: "POST",
          url: "/node/view/",
          body: node,
          resolve: (data: DataNode) => {
            openNewTab(
              page === "charts" ? data.dtaleChartsUrl! : data.dtaleUrl!
            );
            dispatch(updateNode(data));
          },
          reject: (error: string) =>
            dispatch(updateNode({ ...node, error: error })),
          onStart: () => setLoading(true),
          onFinish: () => setLoading(false),
        });
      }}
      loading={loading}
      icon={page === "charts" ? <LineChartOutlined /> : <TableOutlined />}
    >
      {`${page === "charts" ? "Charts" : "Table"}`}
    </Button>
  );
};

export const ViewTableButton: React.FC<{
  dispatch: Dispatch<any>;
  node: DataNode;
}> = ({ dispatch, node }) => (
  <ViewButton dispatch={dispatch} node={node} page="table" />
);

export const ViewChartsButton: React.FC<{
  dispatch: Dispatch<any>;
  node: DataNode;
}> = ({ dispatch, node }) => (
  <ViewButton dispatch={dispatch} node={node} page="charts" />
);

export const ShutdownButton: React.FC<{
  dispatch: Dispatch<any>;
  node: DataNode;
}> = ({ dispatch, node }) => {
  const [loading, setLoading] = useState<boolean>(false);
  return (
    <Button
      title="shut down"
      onClick={() => {
        setLoading(true);
        httpRequest({
          method: "POST",
          url: "node/kill/",
          body: node,
          resolve: (data: DataNode) => {
            dispatch(updateNode(data));
            setLoading(false);
          },
          reject: (error) => {
            const newNode = { ...node, error: error };
            dispatch(updateNode(newNode));
            setLoading(false);
          },
        });
      }}
      disabled={!node.dtaleUrl}
      loading={loading}
      icon={<PoweroffOutlined />}
    ></Button>
  );
};
