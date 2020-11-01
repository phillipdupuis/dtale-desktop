import React, { useEffect } from "react";
import { Source } from "../store/state";
import {
  updateSource,
  setSelectedSource,
  ActionDispatch,
} from "../store/actions";
import { httpRequest } from "../utils/requests";
import { Collapse, Tag, Popover, Space, Button, Typography } from "antd";
import { SettingOutlined, ReloadOutlined } from "@ant-design/icons";
import { NodeList } from "./NodeList";
import styled from "styled-components";

const StyledTag = styled(Tag)`
  margin-right: 0;
`;

const SourceDescription: React.FC<{ source: Source }> = ({ source }) => {
  const nodes = Object.values(source.nodes || {});
  const numActive = nodes.filter((node) => node.dtaleUrl).length;
  return (
    <Space size="small">
      <Typography.Text ellipsis>{source.name}</Typography.Text>
      {source.loading ? null : (
        <StyledTag>{`${nodes.length} results`}</StyledTag>
      )}
      {source.loading || numActive === 0 ? null : (
        <StyledTag color="green">{`${numActive} active`}</StyledTag>
      )}
      {source.loading || !source.error ? null : (
        <Tag color="error">
          <Popover content={source.error}>Error</Popover>
        </Tag>
      )}
    </Space>
  );
};

export const SourceList: React.FC<{
  sources: Source[];
  dispatch: ActionDispatch;
}> = ({ sources, dispatch }) => {
  const loadMoreNodes = (source: Source) => {
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
      {sources
        .filter((source) => source.visible)
        .map((source) => (
          <Collapse.Panel
            id={source.id}
            key={source.id}
            disabled={source.loading}
            header={<SourceDescription source={source} />}
            extra={
              <Space>
                {source.nodesFullyLoaded || source.error ? null : (
                  <Button
                    size="small"
                    icon={<ReloadOutlined />}
                    loading={source.loading}
                    onClick={(event) => {
                      event.stopPropagation();
                      loadMoreNodes(source);
                    }}
                  >
                    Load more
                  </Button>
                )}
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
            <NodeList
              nodes={Object.values(source.nodes || {})}
              dispatch={dispatch}
            />
          </Collapse.Panel>
        ))}
    </Collapse>
  );
};
