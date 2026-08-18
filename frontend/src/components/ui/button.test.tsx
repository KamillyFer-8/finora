import { render, screen } from "@testing-library/react";
import { Button } from "./button";

describe("Button", () => {
  it("renders an accessible button", () => {
    render(<Button>Continuar</Button>);
    expect(screen.getByRole("button", { name: "Continuar" })).toBeInTheDocument();
  });
});
