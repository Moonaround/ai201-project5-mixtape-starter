# Mixtape Bug Hunt — Submission Document

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

## 🔍 Milestone 2: Root Cause Analyses (RCA)

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
The explicit `.outerjoin()` statement on the `song_tags` model generates a distinct tabular row for every tag matched to a song. Because the database returns multiple table rows for a single track matching multiple tags, SQLAlchemy instantiates duplicate duplicate `Song` objects for each relative join pair. This means the array response length expands linearly based on the count of keywords mapped to a single item.

**5. Your fix and side-effect check:**
Appended the `.distinct()` constraint method immediately preceding the `.all()` terminal call expression to collapse multi-row join results back into unique entity blocks. Verified that general searches match cleanly and confirmed duplicates are completely eliminated from track payloads.

---

### 📌 Issue #4 — Missing rating notification event

**1. What went wrong:**
When a system profile submits a numerical score rating for a song shared by another user, the asset owner never receives a notification alert on their account stream dashboard.

**2. How you reproduced it:**
- **Inputs used:** Executed a standard network update request matching the target interface schema: `POST /songs/<song_id>/rate` with payload data containing a user ID and a numeric value. Followed up by calling `GET /users/<owner_id>/notifications`.
- **Observed Behavior:** The rating score updated correctly on the track entity block, but the user's notification list length remained empty. No database record linked to the rating action was generated inside the notification table.
- **Expected Behavior:** Rating a friend's song must trigger a notification event instance tracking the sender's rating update action, identical to when a track is appended to a collaborative playlist.

---

### 📌 Issue #5 — The last song in a playlist never shows up

**1. What went wrong:**
Playlists consistently mask and conceal the most recently appended tracking record, dropping the final row collection item from visual outputs entirely.

**2. How you reproduced it:**
- **Inputs used:** Checked the track count via `GET /playlists/<playlist_id>/songs`. Fired a subsequent data update entry: `POST /playlists/<playlist_id>/songs` adding an additional song. Re-queried the primary tracks collection endpoint.
- **Observed Behavior:** The initial invisible target track became visible, but the newly appended tracking row immediately vanished from the response array list. The output collection length stayed permanently short by one item.
- **Expected Behavior:** Every single song associated with the target playlist structure should render inside the returned list array, including the most recent addition.
