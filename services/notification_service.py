def rate_song(user_id: str, song_id: str, score: int) -> Rating:
    """
    Save a user's rating for a song.

    Args:
        user_id: The ID of the user submitting the rating.
        song_id: The ID of the song being rated.
        score: An integer from 1 to 5.

    Returns:
        The created or updated Rating instance.
    """
    if score < 1 or score > 5:
        raise ValueError("Score must be between 1 and 5")

    song = db.session.get(Song, song_id)
    if not song:
        raise ValueError(f"Song {song_id} not found")

    rater = db.session.get(User, user_id)
    if not rater:
        raise ValueError(f"User {user_id} not found")

    # Check if the user has already rated this song
    existing = db.session.query(Rating).filter_by(
        user_id=user_id, song_id=song_id
    ).first()

    if existing:
        existing.score = score
        rating = existing
    else:
        rating = Rating(user_id=user_id, song_id=song_id, score=score)
        db.session.add(rating)

    # ✨ THE FIX: Generate a notification alert for the song's original sharer
    # Only notify if the user rating the song isn't the one who shared it
    if song.shared_by != user_id:
        create_notification(
            user_id=song.shared_by,
            notification_type="song_rated",
            body=f"{rater.username} rated your song '{song.title}' with {score} stars."
        )

    db.session.commit()

    return rating
