import React, { useState, useEffect, SetStateAction, Dispatch } from "react";
import { cloneDeep } from "lodash";
import { Modal, Switch } from "antd";
import styled from "styled-components";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { httpRequest } from "../utils/requests";
import { updateSource, setOpenModal, ActionDispatch } from "../store/actions";
import { Source, RootState } from "../store/state";

type LayoutChange = Pick<Source, "id" | "visible" | "sortValue">;

const StyledList = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  margin-top: 5px;
  margin-bottom: 5px;
  border: 1px solid lightgray;
  div {
    border-bottom: 1px solid lightgray;
  }
  div:last-child {
    border-bottom: none;
  }
`;

const StyledListItem = styled.div`
  display: flex;
  padding: 10px;
  width: 100%;
  height: 100%;
  cursor: pointer;
  .visibility-toggle {
    margin-left: auto;
  }
`;

const Editor: React.FC<{
  state: RootState;
  clone: RootState;
  dispatch: ActionDispatch;
  updateClone: Dispatch<SetStateAction<RootState>>;
}> = ({ state, clone, dispatch, updateClone }) => {
  const reorder = (list: Source[], startIndex: number, endIndex: number) => {
    // cloneDeep is required because splice modifies arrays in-place.
    // We need 'list' to stay unchanged so we can use it to get the sortValues by position.
    const result = cloneDeep(list);
    const [removed] = result.splice(startIndex, 1);
    result.splice(endIndex, 0, removed);
    result.forEach((source, i) => {
      source.sortValue = list[i].sortValue;
    });
    updateClone({ ...clone, sources: result });
  };

  const toggleVisible = (source: Source) => {
    source.visible = !source.visible;
    // naming conventions are kinda falling apart with the following line...
    updateClone(cloneDeep(clone));
  };

  const saveChanges = () => {
    const changes: LayoutChange[] = clone
      .sources!.filter((after) => {
        const before = state.sources!.find((source) => source.id === after.id)!;
        return (
          after.sortValue !== before.sortValue ||
          after.visible !== before.visible
        );
      })
      .map((after) => ({
        id: after.id,
        visible: after.visible,
        sortValue: after.sortValue,
      }));
    if (changes.length > 0) {
      httpRequest({
        method: "POST",
        url: "/source/update-layout/",
        body: changes,
        resolve: (data) => {
          data.forEach((s: Source) => dispatch(updateSource(s)));
          dispatch(setOpenModal(null));
        },
        reject: (error) => null,
      });
    }
  };

  return (
    <Modal
      visible={state.openModal === "layoutEditor"}
      title="Edit Layout"
      onCancel={() => dispatch(setOpenModal(null))}
      destroyOnClose={true}
      width={"90%"}
      bodyStyle={{ height: "80vh", overflowY: "scroll" }}
      centered
      onOk={() => saveChanges()}
    >
      <DragDropContext
        onDragEnd={(result) => {
          if (result.destination) {
            reorder(
              clone.sources!,
              result.source.index,
              result.destination!.index
            );
          }
        }}
      >
        <Droppable droppableId="editLayoutSourceList">
          {(listProvided, listSnapshot) => (
            <StyledList
              id="editLayoutSourceList"
              {...listProvided.droppableProps}
              ref={listProvided.innerRef}
            >
              {clone.sources!.map((source, i) => (
                <Draggable key={source.id} draggableId={source.id} index={i}>
                  {(itemProvided, itemSnapshot) => (
                    <StyledListItem
                      ref={itemProvided.innerRef}
                      {...itemProvided.draggableProps}
                      {...itemProvided.dragHandleProps}
                      style={
                        !itemSnapshot.isDragging
                          ? itemProvided.draggableProps.style
                          : {
                              ...itemProvided.draggableProps.style,
                              background: "#bae7ff",
                            }
                      }
                    >
                      {source.name}
                      <Switch
                        className="visibility-toggle"
                        checked={source.visible}
                        onChange={() => toggleVisible(source)}
                        checkedChildren="visible"
                        unCheckedChildren="hidden"
                      />
                    </StyledListItem>
                  )}
                </Draggable>
              ))}
              {listProvided.placeholder}
            </StyledList>
          )}
        </Droppable>
      </DragDropContext>
    </Modal>
  );
};

export const LayoutEditor: React.FC<{
  state: RootState;
  dispatch: ActionDispatch;
}> = ({ state, dispatch }) => {
  const [clone, updateClone] = useState<RootState>(cloneDeep(state));

  // Whenever it opens, refresh clone to match the latest state
  useEffect(() => {
    if (state.openModal === "layoutEditor") {
      updateClone(cloneDeep(state));
    }
  }, [state.openModal]);

  if (state.sources === undefined || state.sources.length === 0) {
    return null;
  }

  return (
    <Editor
      state={state}
      clone={clone}
      dispatch={dispatch}
      updateClone={updateClone}
    />
  );
};
