import React, { useEffect } from "react";
import { Source, Settings } from "../store/state";
import { setSelectedSource, ActionDispatch } from "../store/actions";
import { Collapse, Tag, Popover, Space, Button, Typography } from "antd";
import { SettingOutlined, ReloadOutlined } from "@ant-design/icons";
import { NodeList } from "./NodeList";
import styled from "styled-components";
import { backend } from "../utils/interface";

const StyledTag = styled(Tag)`
  margin-right: 0;
`;

const SourceDescription: React.FC<{ source: Source }> = ({ source }) => {
  const nodes = Object.values(source.nodes || {});
  const numActive = nodes.filter((node) => node.dtaleUrl).length;
  return (
    <Space size="small">
      <Typography.Text ellipsis>{source.name}</Typography.Text>
      {source.updating ? null : (
        <StyledTag>{`${nodes.length} results`}</StyledTag>
      )}
      {source.updating || numActive === 0 ? null : (
        <StyledTag color="green">{`${numActive} active`}</StyledTag>
      )}
      {source.updating || !source.error ? null : (
        <Tag color="error">
          <Popover content={source.error}>Error</Popover>
        </Tag>
      )}
    </Space>
  );
};

export const SourceList: React.FC<{
  sources: Source[];
  settings: Settings;
  dispatch: ActionDispatch;
}> = ({ sources, settings, dispatch }) => {
  const loadMoreNodes = (source: Source) => {
    backend.get.sourceNodes({ dispatch, sourceId: source.id, limit: 50 });
  };

  useEffect(() => {
    sources.forEach((source) => {
      if (
        !source.updating &&
        !source.nodesFullyLoaded &&
        !source.error &&
        Object.keys(source.nodes || {}).length === 0
      ) {
        loadMoreNodes(source);
      }
    });
  });

  return (
    <Collapse defaultActiveKey={[]} accordion>
      {sources
        .filter((source) => source.visible)
        .map((source) => (
          <Collapse.Panel
            id={source.id}
            key={source.id}
            disabled={source.updating}
            header={<SourceDescription source={source} />}
            extra={
              <Space>
                {source.nodesFullyLoaded || source.error ? null : (
                  <Button
                    size="small"
                    icon={<ReloadOutlined />}
                    loading={source.updating}
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
              settings={settings}
              nodes={Object.values(source.nodes || {})}
              dispatch={dispatch}
            />
          </Collapse.Panel>
        ))}
    </Collapse>
  );
};
