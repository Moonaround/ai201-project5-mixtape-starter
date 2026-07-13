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

## 🔍 Milestone 2: Root Cause Analysis (RCA) Tracking
*(This section remains blank for your forthcoming Milestone 2 code modifications. Each fixed bug must document its 5 core fields here.)*
