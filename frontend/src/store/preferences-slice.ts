import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

type Period = "7d" | "30d" | "3m" | "6m" | "1y";
type PreferencesState = { period: Period; theme: "dark"; sidebarCollapsed: boolean };
const initialState: PreferencesState = { period: "30d", theme: "dark", sidebarCollapsed: false };

const preferencesSlice = createSlice({
  name: "preferences",
  initialState,
  reducers: {
    setPeriod: (state, action: PayloadAction<Period>) => { state.period = action.payload; },
    toggleSidebar: (state) => { state.sidebarCollapsed = !state.sidebarCollapsed; },
  },
});

export const { setPeriod, toggleSidebar } = preferencesSlice.actions;
export const preferencesReducer = preferencesSlice.reducer;
