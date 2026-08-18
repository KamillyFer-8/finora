import { preferencesReducer, setPeriod, toggleSidebar } from "./preferences-slice";
describe("preferences", () => { test("updates global period and sidebar", () => { const period = preferencesReducer(undefined, setPeriod("3m")); expect(period.period).toBe("3m"); expect(preferencesReducer(period, toggleSidebar()).sidebarCollapsed).toBe(true); }); });
