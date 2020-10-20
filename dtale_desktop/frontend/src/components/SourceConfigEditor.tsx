import React, { useState, Dispatch } from "react";
import { Drawer, Button, Input, Alert } from "antd";
import { httpRequest } from "../utils/requests";
import { addSources, updateSource, setSelectedSource } from "../store/actions";
import { DataSource } from "../store/state";
import { PythonEditor } from "./PythonEditor";

type Props = {
  source: DataSource;
  dispatch: Dispatch<any>;
};

const Label: React.FC<{ text: string }> = ({ text }) => (
  <div style={{ marginTop: 5, marginBottom: 5 }}>{text}</div>
);

const Editor: React.FC<Props> = ({ source, dispatch }) => {
  const [error, setError] = useState<string | null>(null);

  // Determine if new source or existing
  const mode: "edit" | "new" = source.name !== "" ? "edit" : "new";

  // Make a copy of the source object and edit that.
  const clone: DataSource = { ...source };

  const checkRequired = (): boolean => {
    const requiredFields = ["name", "listPaths", "getData"] as const;
    const missing = requiredFields.filter((f) => !clone[f]);
    if (missing.length > 0) {
      setError(`Fill out the required fields: ${missing.join(", ")}`);
      return false;
    } else if (
      mode === "edit" &&
      requiredFields.every((f) => clone[f] === source[f])
    ) {
      setError("No changes were made");
      return false;
    } else {
      return true;
    }
  };

  const submitCreate = () => {
    if (checkRequired()) {
      const { nodes, ...updatedSource } = clone;
      httpRequest({
        method: "POST",
        url: "/source/create/",
        body: updatedSource,
        resolve: (data: DataSource) => {
          dispatch(addSources([data]));
          dispatch(setSelectedSource(null));
        },
        reject: (error) => setError(error),
      });
    }
  };

  const submitUpdate = () => {
    if (checkRequired()) {
      const { nodes, ...updatedSource } = clone;
      httpRequest({
        method: "POST",
        url: "/source/update/",
        body: updatedSource,
        resolve: (data: DataSource) => {
          dispatch(updateSource(data));
          dispatch(setSelectedSource(null));
        },
        reject: (error) => setError(error),
      });
    }
  };

  return (
    <Drawer
      title={mode === "new" ? "Add Data Source" : "Edit Data Source"}
      width={720}
      onClose={() => dispatch(setSelectedSource(null))}
      visible={true}
    >
      {error ? (
        <Alert
          type="error"
          message={error}
          closable
          onClose={() => setError(null)}
        />
      ) : null}
      <Label text="Name" />
      <Input
        disabled={!source.editable}
        defaultValue={clone.name}
        onChange={(e) => {
          clone.name = e.target.value;
        }}
        size="small"
      />
      <Label text="list_paths.py" />
      <PythonEditor
        readOnly={!source.editable}
        name="list_paths_code"
        value={clone.listPaths}
        onChange={(v) => {
          clone.listPaths = v;
        }}
        width="600"
        maxLines={16}
        minLines={16}
      />
      <Label text="get_data.py" />
      <PythonEditor
        readOnly={!source.editable}
        name="get_data_code"
        value={clone.getData}
        onChange={(v) => {
          clone.getData = v;
        }}
        width="600"
        maxLines={16}
        minLines={16}
      />
      {source.editable ? (
        <Button
          type="primary"
          block
          style={{ marginTop: 10 }}
          onClick={() => {
            if (mode === "new") {
              submitCreate();
            } else {
              submitUpdate();
            }
          }}
        >
          Submit
        </Button>
      ) : null}
    </Drawer>
  );
};

export default Editor;
