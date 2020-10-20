import React from "react";
import AceEditor, { IAceEditorProps } from "react-ace";

import "ace-builds/src-noconflict/mode-python";
import "ace-builds/src-noconflict/theme-monokai";

type RequiredProps = "name" | "value" | "onChange" | "width";

type Props = Required<Pick<IAceEditorProps, RequiredProps>> &
  Omit<IAceEditorProps, RequiredProps>;

const PythonEditor: React.FC<Props> = ({
  name,
  value,
  onChange,
  width,
  theme = "monokai",
  maxLines = 20,
  minLines = 4,
  editorProps = { $blockScrolling: true },
  wrapEnabled = true,
  ...additionalProps
}) => (
  <AceEditor
    mode="python"
    name={name}
    value={value}
    onChange={onChange}
    width={width}
    theme={theme}
    maxLines={maxLines}
    minLines={minLines}
    editorProps={editorProps}
    wrapEnabled={wrapEnabled}
    {...additionalProps}
  />
);

export { PythonEditor };
