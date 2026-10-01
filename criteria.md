# FitFindr Acceptance Criteria

## Criterion 1 — Successful Search Completes the Full Flow

**Given** a query that matches at least one listing, the agent completes all three tool calls and returns a fit card in at least 4 of 5 tries.

**Why this target:** The agent should normally complete the full workflow, but allowing one miss recognizes that model-generated results can vary.

## Criterion 2 — Empty Search Stops Before Outfit Suggestions

**Given** a query that matches no listings, the agent stops before `suggest_outfit` and returns a message explaining what the user should change in the search in 5 of 5 tries.

**Why this target:** An empty search is a clear branch condition, so the agent should handle it consistently every time.

## Criterion 3 — State Carries the Found Item

**Given** a query that matches at least one listing, the item passed to `suggest_outfit` is the same listing returned by `search_listings` in 5 of 5 tries.

**Why this target:** Passing the wrong item would make the outfit suggestion unrelated to what the user searched for, so this state transition should be reliable.

## Criterion 4 — Fit Card Uses the Selected Item

**Given** a successful search and outfit suggestion, the returned fit card mentions or clearly describes the selected item and includes an outfit-related caption in at least 4 of 5 tries.

**Why this target:** The model can phrase captions differently, so the requirement focuses on the important content rather than exact wording.

## Criterion 5 — Empty Search Does Not Create a Fit Card

**Given** a query that returns no listings, the agent leaves `session["fit_card"]` as `None` in 5 of 5 tries.

**Why this target:** There is no item to style or turn into a fit card after an empty search, so the session should remain in a clean stopped state.