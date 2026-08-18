import { render, screen } from "@testing-library/react";
import { Select } from "./select";
test("renders the select with its label and error", () => { render(<Select label="Conta" error="Obrigatório"><option>Principal</option></Select>); expect(screen.getByRole("combobox")).toBeInTheDocument(); expect(screen.getByText("Conta")).toBeInTheDocument(); expect(screen.getByRole("alert")).toHaveTextContent("Obrigatório"); });
