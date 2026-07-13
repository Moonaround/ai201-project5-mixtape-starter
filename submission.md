# Mixtape Bug Hunt — Submission Document

## 🤖 Milestone 4: AI Usage Disclosure

### 1. Codebase Navigation and Orientation
- **How it was used:** I utilized the AI assistant to summarize the modular responsibilities of the files within the `services/` directory. Specifically, I requested a top-down explanation of how the `db.session.query` scopes in Flask-SQLAlchemy interact with table joins.
- **What it helped me understand:** The AI successfully traced the call execution chains, clarifying how routing blueprints in the presentation layer pass parameters directly into underlying business service controllers.

### 2. Algorithmic Debugging & Code Verification
- **How it was used:** I leveraged the AI tool to isolate edge-case behaviors in database query return boundaries. For instance, I prompted the assistant to explain the difference between raw multi-table outer joins versus uniquely constrained entity selections.
- **Where human verification took over:** While the AI pointed out general list append loops, I had to trace `services/search_service.py` manually line-by-line to realize that duplicate song occurrences were explicitly bound to the number of tags a track possessed. I verified this diagnosis by querying the endpoint `GET /songs/search?q=Anthem` directly, checking database behaviors, and explicitly adding the `.distinct()` constraint modifier myself to solve the true underlying root cause.

---

## 🗺️ Milestone 1: Codebase Map

### Core Architecture Overview
The Mixtape application is built using a clean separation of concerns following a **Service-Route-Model** architecture pattern via Flask and SQLAlchemy:

*   **`models.py`**: Defines 5 foundational SQLAlchemy database models: `User`, `Song`, `Playlist`, `PlaylistSong`, and `Notification`. 
    *   *Key Observation:* `PlaylistSong` functions explicitly as an associative join table containing an explicit tracking sequence or order column. Songs within a playlist do not simply load by raw database insertion sequence; they are bound to a strict relative positioning constraint.
*   **`routes/`**: Handles incoming API requests, HTTP verb binding, URL parameters, input payload extraction, and JSON response formatting.
*   **`services/`**: The core operational intelligence and business logic layer. Files here perform all database updates, math evaluations, query restrictions, and state adjustments.

### Architectural Blueprint Pattern
Every API route layer delegates business computations immediately to an isolated companion logic function inside the `services/` namespace. The routing controllers strictly parse raw variables and return serialization text envelopes; zero business rules are allowed to execute inside the `routes/` scripts.

### Step-by-Step Data Flow: Rating an Asset & Notification Delivery
1.  **Input Entry:** A client fires an HTTP request: `POST /songs/<id>/rate`.
2.  **Routing Catch:** The matching route controller captures the payload context, identifies the specific `song_id`, and immediately transfers control to the backend service.
3.  **Service Processing:** The backend service processes the new score adjustments directly onto the `Song` entity record block.
4.  **Observer Generation:** Once the database record commits, the script triggers a method call via `notification_service.notify_song_rated()`.
5.  **Database Side-Effect:** The notification engine creates and pushes a new `Notification` instance record tracking the `sender_id`, target `receiver_id` (the track's initial author or sharer), and structural content strings directly to the transactional database state.

---

## 🔍 Milestone 2 & 3: Root Cause Analyses (RCA)

### 📌 Issue #3 — The same song keeps showing up twice in search

**1. What went wrong:**
Keyword queries for specific songs return duplicate records of the exact same track when assets have multiple user tags attached.

**2. How you reproduced it:**
- **Inputs used:** Fired an HTTP request `GET /songs/search?q=Anthem` into the local app environment.
- **Observed Behavior:** The response payload duplicated matching items where the targeted track model possessed multiple categorical associations within the tag join matrices.
- **Expected Behavior:** Each target track entity record matching the keyword query criteria must appear precisely once inside the dictionary payload array.

**3. How you found the root cause:**
Inspected `services/search_service.py`. Followed the database invocation sequence built on `db.session.query(Song)`. I noticed the implementation executed a manual `.outerjoin()` on the `song_tags` bridge structure without applying a uniqueness constraint on the return boundary.

**4. The root cause:**
The explicit `.outerjoin()` statement on the `song_tags` model generates a distinct tabular row for every tag matched to a song. Because the database returns multiple table rows for a single track matching multiple tags, SQLAlchemy instantiates duplicate `Song` objects for each relative join pair. This means the array response length expands linearly based on the count of keywords mapped to a single item.

**5. Your fix and side-effect check:**
Appended the `.distinct()` constraint method immediately preceding the `.all()` terminal call expression to collapse multi-row join results back into unique entity blocks. Verified that general searches match cleanly and confirmed duplicates are completely eliminated from track payloads.

---

### 📌 Issue #4 — Missing rating notification event

**1. What went wrong:**
System accounts do not receive an alert notification on their metrics stream dashboard when another profile leaves a score rating on a track they initially shared.

**2. How you reproduced it:**
- **Inputs used:** Submitted a payload score update to `POST /songs/<song_id>/rate`, then fetched user data via `GET /users/<my_id>/notifications`.
- **Observed Behavior:** The evaluation metric score processed correctly on the track asset, but the user's notification list collection length returned empty.
- **Expected Behavior:** An entry logging the score interaction should be written to the database notification schema and rendered on the owner's account dashboard.

**3. How you found the root cause:**
Traced structural paths directly inside `services/notification_service.py`. Compared the notification trigger hooks in `add_to_playlist()` with the execution flow lines of the `rate_song()` processing wrapper.

**4. The root cause:**
While the `rate_song()` controller contained complete code logic to manage score overwrites, update ratings, and run database commits, it lacked an architectural call invoking the companion `create_notification()` handler. This caused ratings to process as isolated entries without downstream dashboard alert updates.

**5. Your fix and side-effect check:**
Injected a conditional verification query evaluating `if song.shared_by != user_id:` inside `rate_song()`, triggering `create_notification()` with type flag `"song_rated"` prior to committing the data layer transactions. Verified that rating an external profile's song now writes an alert record accurately without side effects.

---

### 📌 Issue #5 — The last song in a playlist never shows up

**1. What went wrong:**
Playlist song lookups consistently conceal and drop the final track added to a playlist, leaving the last record invisible to users.

**2. How you reproduced it:**
- **Inputs used:** Checked total records via `GET /playlists/<playlist_id>/songs`. Re-sent a payload update using `POST /playlists/<playlist_id>/songs` to append a fresh track entry, then re-fetched the list.
- **Observed Behavior:** The newly added song was missing from the returned array list, while the previously hidden song suddenly appeared.
- **Expected Behavior:** All song instances mapped within the relational database bridge schema should render perfectly inside the return dictionary array.

**3. How you found the root cause:**
Traced execution flow to the retrieval block inside `services/playlist_service.py`. Checked the return statement pipeline of the `get_playlist_songs()` method function block.

**4. The root cause:**
The code applied an off-by-one upper boundary negative array slice (`[:-1]`) on the instantiated track list. This structural indexing error automatically truncated the last element of the array right before formatting the JSON output payload.

**5. Your fix and side-effect check:**
Removed the trailing `[:-1]` slice operator to allow the list comprehension loop to format and return the entire collection. Confirmed via local manual tracking that adding new entries preserves correct visibility counts across all items.
