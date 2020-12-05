import React, { useState } from "react";
import { Button } from "antd";
import Icon from "@ant-design/icons";
import { FaSun, FaMoon } from "react-icons/fa";
import { getTheme, Theme, toggleTheme } from "../utils/theme";

export const ThemeController: React.FC<{}> = () => {
  const [theme, setTheme] = useState<Theme>(getTheme());

  const toggle = (): void => {
    const newTheme = toggleTheme();
    setTheme(newTheme);
  };

  return (
    <Button
      icon={<Icon component={theme === "dark" ? FaSun : FaMoon} />}
      shape="circle-outline"
      title="Toggle theme"
      onClick={toggle}
    />
  );
};
