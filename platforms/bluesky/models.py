"""Conversion functions from Bluesky/AT Protocol objects to universal models."""

from datetime import datetime
from typing import Optional, List, Any

from models import (
    UniversalStatus,
    UniversalUser,
    UniversalNotification,
    UniversalMedia,
    UniversalMention,
)


def extract_rkey_from_uri(uri: str) -> str:
    """Extract the record key from an AT Protocol URI.

    URI format: at://did:plc:xxx/app.bsky.feed.post/rkey
    """
    if not uri:
        return ""
    parts = uri.split('/')
    return parts[-1] if parts else uri


def get_web_url(handle: str, rkey: str) -> str:
    """Get the web URL for a Bluesky post."""
    return f"https://bsky.app/profile/{handle}/post/{rkey}"


def to_camel_case(snake_str):
    """Convert snake_case to camelCase."""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def get_attr(obj, name, default=None):
    """Safely get attribute from object or dict, trying both snake_case and camelCase."""
    if obj is None:
        return default

    # Try snake_case first
    if isinstance(obj, dict):
        if name in obj:
            return obj[name]
        # Try camelCase version
        camel_name = to_camel_case(name)
        if camel_name in obj:
            return obj[camel_name]
        return default

    # For objects, try snake_case first
    result = getattr(obj, name, None)
    if result is not None:
        return result

    # Try camelCase version
    camel_name = to_camel_case(name)
    result = getattr(obj, camel_name, None)
    if result is not None:
        return result

    return default


def bluesky_profile_to_universal(profile, platform_data=None) -> Optional[UniversalUser]:
    """Convert a Bluesky profile to UniversalUser."""
    if profile is None:
        return None

    did = get_attr(profile, 'did', '')
    handle = get_attr(profile, 'handle', '')

    # Parse created_at if available (ProfileViewDetailed has this)
    created_at_str = get_attr(profile, 'created_at', None)
    created_at = parse_bluesky_datetime(created_at_str) if created_at_str else None

    # Get counts - these are only available in ProfileViewDetailed, not basic profile views
    # Use `or 0` to handle None values explicitly
    followers_count = get_attr(profile, 'followers_count', None)
    follows_count = get_attr(profile, 'follows_count', None)
    posts_count = get_attr(profile, 'posts_count', None)

    return UniversalUser(
        id=did,
        acct=handle,
        username=handle.split('.')[0] if '.' in handle else handle,
        display_name=get_attr(profile, 'display_name', '') or handle,
        note=get_attr(profile, 'description', ''),
        avatar=get_attr(profile, 'avatar', None),
        header=get_attr(profile, 'banner', None),
        followers_count=followers_count if followers_count is not None else 0,
        following_count=follows_count if follows_count is not None else 0,
        statuses_count=posts_count if posts_count is not None else 0,
        created_at=created_at,
        url=f"https://bsky.app/profile/{handle}",
        bot=False,  # Bluesky doesn't have bot flag
        locked=False,  # Bluesky doesn't have locked accounts
        _platform_data=platform_data or profile,
        _platform='bluesky',
    )


def bluesky_media_to_universal(embed_image) -> UniversalMedia:
    """Convert a Bluesky image embed to UniversalMedia."""
    return UniversalMedia(
        id=get_attr(embed_image, 'cid', '') or str(hash(get_attr(embed_image, 'fullsize', ''))),
        type='image',
        url=get_attr(embed_image, 'fullsize', ''),
        preview_url=get_attr(embed_image, 'thumb', None),
        description=get_attr(embed_image, 'alt', None),
        _platform_data=embed_image,
    )


def extract_mentions_from_facets(facets) -> List[UniversalMention]:
    """Extract mentions from Bluesky facets."""
    mentions = []
    if not facets:
        return mentions

    for facet in facets:
        features = get_attr(facet, 'features', [])
        for feature in features:
            # Check if it's a mention feature
            feature_type = get_attr(feature, '$type', '') or get_attr(feature, 'py_type', '')
            if 'mention' in str(feature_type).lower():
                did = get_attr(feature, 'did', '')
                mentions.append(UniversalMention(
                    id=did,
                    acct=did,  # We'd need to resolve DID to handle
                    username=did,
                    url=None,
                    _platform_data=feature,
                ))
    return mentions


def extract_links_from_facets(facets) -> List[str]:
    """Extract link URLs from Bluesky facets."""
    links = []
    if not facets:
        return links

    for facet in facets:
        features = get_attr(facet, 'features', [])
        for feature in features:
            # Check if it's a link feature
            feature_type = get_attr(feature, '$type', '') or get_attr(feature, 'py_type', '')
            if 'link' in str(feature_type).lower():
                uri = get_attr(feature, 'uri', '')
                if uri and uri not in links:
                    links.append(uri)
    return links


def extract_card_from_embed(embed):
    """Extract external embed (card) from Bluesky embed.

    Returns a dict with url, title, description, image fields or None.
    """
    if not embed:
        return None

    embed_type = get_attr(embed, '$type', '') or get_attr(embed, 'py_type', '')

    # Handle external embed (link cards)
    if 'external' in str(embed_type).lower():
        external = get_attr(embed, 'external', None)
        if external:
            return type('Card', (), {
                'url': get_attr(external, 'uri', ''),
                'title': get_attr(external, 'title', ''),
                'description': get_attr(external, 'description', ''),
                'image': get_attr(external, 'thumb', None),
            })()

    # Handle recordWithMedia that might have external embed
    if 'recordWithMedia' in str(embed_type).lower():
        inner_media = get_attr(embed, 'media', None)
        if inner_media:
            return extract_card_from_embed(inner_media)

    return None


def extract_media_from_embed(embed) -> List[UniversalMedia]:
    """Extract media attachments from Bluesky embed."""
    media = []
    if not embed:
        return media

    embed_type = get_attr(embed, '$type', '') or get_attr(embed, 'py_type', '')

    # Handle images embed
    if 'images' in str(embed_type).lower():
        images = get_attr(embed, 'images', [])
        for img in images:
            media.append(bluesky_media_to_universal(img))

    # Handle video embed
    elif 'video' in str(embed_type).lower():
        media.append(UniversalMedia(
            id=get_attr(embed, 'cid', ''),
            type='video',
            url=get_attr(embed, 'playlist', '') or get_attr(embed, 'url', ''),
            preview_url=get_attr(embed, 'thumbnail', None),
            description=get_attr(embed, 'alt', None),
            _platform_data=embed,
        ))

    # Handle record with media (quote post with images)
    elif 'recordWithMedia' in str(embed_type).lower():
        inner_media = get_attr(embed, 'media', None)
        if inner_media:
            media.extend(extract_media_from_embed(inner_media))

    return media


def parse_bluesky_datetime(dt_str) -> datetime:
    """Parse a Bluesky datetime string."""
    if not dt_str:
        return datetime.now()
    try:
        # Handle ISO format with Z or +00:00
        dt_str = str(dt_str).replace('Z', '+00:00')
        # Remove timezone for naive datetime
        if '+' in dt_str:
            dt_str = dt_str.split('+')[0]
        if '.' in dt_str:
            # Truncate microseconds if too long
            parts = dt_str.split('.')
            if len(parts[1]) > 6:
                parts[1] = parts[1][:6]
            dt_str = '.'.join(parts)
        return datetime.fromisoformat(dt_str)
    except:
        return datetime.now()


def bluesky_post_to_universal(post, author=None, platform_data=None) -> Optional[UniversalStatus]:
    """Convert a Bluesky post to UniversalStatus.

    Args:
        post: The post record or feed view post (FeedViewPost, PostView, or record)
        author: The author profile (if not embedded in post)
        platform_data: Original platform data to store
    """
    if post is None:
        return None

    # Handle FeedViewPost structure: { post: PostView, reason?: ReasonRepost }
    # vs PostView structure: { uri, cid, author, record, ... }
    # vs raw record: { text, createdAt, ... }

    # Check if this is a FeedViewPost (has .post attribute with a PostView)
    inner_post = getattr(post, 'post', None)
    reason = getattr(post, 'reason', None)
    reply_context = getattr(post, 'reply', None)  # Contains parent/root posts for replies

    # If we have a reason (repost), handle it specially
    if reason is not None:
        # Check for repost reason - try multiple ways to get the type
        reason_type = getattr(reason, 'py_type', None) or getattr(reason, '$type', None) or str(type(reason).__name__)
        is_repost = ('repost' in str(reason_type).lower() or
                     'Repost' in str(type(reason).__name__) or
                     'ReasonRepost' in str(type(reason)))
        if is_repost and inner_post:
            # This is a repost - create the reblogged post first
            reblogged_status = bluesky_post_to_universal(inner_post)

            # Get the original author's DID for sanity check later
            original_author = get_attr(inner_post, 'author', None)
            original_did = get_attr(original_author, 'did', '')

            # The "reposter" is in reason.by - get it directly
            reposter = getattr(reason, 'by', None)

            # ALWAYS create reposter_user with debug info for now
            if reposter is not None:
                reposter_did = get_attr(reposter, 'did', '') or ''
                reposter_handle = get_attr(reposter, 'handle', '') or ''
                reposter_display = get_attr(reposter, 'display_name', '') or get_attr(reposter, 'displayName', '') or reposter_handle or '?'

                # Create user with the reposter's info
                reposter_user = UniversalUser(
                    id=reposter_did or 'no_did',
                    acct=reposter_handle or 'no_handle',
                    username=reposter_handle.split('.')[0] if reposter_handle and '.' in reposter_handle else 'no_user',
                    display_name=reposter_display,  # Use the actual display name from reason.by
                    note='',
                    avatar=get_attr(reposter, 'avatar', None),
                    header=None,
                    followers_count=0,
                    following_count=0,
                    statuses_count=0,
                    created_at=None,
                    url=f"https://bsky.app/profile/{reposter_handle}" if reposter_handle else None,
                    bot=False,
                    locked=False,
                    _platform_data=reposter,
                    _platform='bluesky',
                )
            else:
                # No reposter found - create debug placeholder
                reason_type = type(reason).__name__
                reposter_user = UniversalUser(
                    id='unknown',
                    acct='unknown',
                    username='unknown',
                    display_name=f'[NO_BY:{reason_type}]',
                    note='',
                    avatar=None,
                    header=None,
                    followers_count=0,
                    following_count=0,
                    statuses_count=0,
                    created_at=None,
                    url=None,
                    bot=False,
                    locked=False,
                    _platform_data=None,
                    _platform='bluesky',
                )

            # Get the repost time from reason.indexed_at or indexedAt
            repost_time_str = get_attr(reason, 'indexed_at', '') or get_attr(reason, 'indexedAt', '')
            repost_time = parse_bluesky_datetime(repost_time_str)

            # Return a status that represents the repost action
            # The account is who reposted, reblog is the original post
            return UniversalStatus(
                id=get_attr(inner_post, 'uri', '') + ':repost',
                account=reposter_user,
                content='',
                text='',
                created_at=repost_time,
                favourites_count=0,
                boosts_count=0,
                replies_count=0,
                in_reply_to_id=None,
                reblog=reblogged_status,
                quote=None,
                media_attachments=[],
                mentions=[],
                url=None,
                visibility=None,
                spoiler_text=None,
                card=None,
                poll=None,
                pinned=False,
                _platform_data=platform_data or post,
                _platform='bluesky',
            )

    # For FeedViewPost without reason, unwrap to get the PostView
    if inner_post is not None:
        post = inner_post

    # Now post should be a PostView or similar
    # Get the record which contains text and createdAt
    record = get_attr(post, 'record', None)

    # Get URI and CID
    uri = get_attr(post, 'uri', '')
    cid = get_attr(post, 'cid', '')
    rkey = extract_rkey_from_uri(uri)

    # Get text content from record
    # For ViewRecord (used in quotes), text is in post.value.text
    text = ''
    if record:
        text = get_attr(record, 'text', '')
    if not text:
        # Check for ViewRecord structure (embed.record)
        value = get_attr(post, 'value', None)
        if value:
            text = get_attr(value, 'text', '')
    if not text:
        text = get_attr(post, 'text', '')

    # Get author
    post_author = get_attr(post, 'author', None) or author
    universal_author = bluesky_profile_to_universal(post_author)

    # Get counts (use snake_case first, then camelCase)
    like_count = get_attr(post, 'like_count', None)
    if like_count is None:
        like_count = get_attr(post, 'likeCount', 0)
    repost_count = get_attr(post, 'repost_count', None)
    if repost_count is None:
        repost_count = get_attr(post, 'repostCount', 0)
    reply_count = get_attr(post, 'reply_count', None)
    if reply_count is None:
        reply_count = get_attr(post, 'replyCount', 0)

    # Get created_at from record
    # For ViewRecord (used in quotes), createdAt might be in post.value
    created_at_str = ''
    if record:
        created_at_str = get_attr(record, 'created_at', '') or get_attr(record, 'createdAt', '')
    if not created_at_str:
        # Check ViewRecord value
        value = get_attr(post, 'value', None)
        if value:
            created_at_str = get_attr(value, 'created_at', '') or get_attr(value, 'createdAt', '')
    if not created_at_str:
        created_at_str = get_attr(post, 'indexed_at', '') or get_attr(post, 'indexedAt', '')
    created_at = parse_bluesky_datetime(created_at_str)

    # Get reply info from record and reply_context
    in_reply_to_id = None
    reply_to_handle = None
    if record:
        reply = get_attr(record, 'reply', None)
        if reply:
            parent = get_attr(reply, 'parent', None)
            if parent:
                in_reply_to_id = get_attr(parent, 'uri', None)

    # Get parent author from reply_context (FeedViewPost.reply.parent.author)
    if reply_context:
        parent_post = get_attr(reply_context, 'parent', None)
        if parent_post:
            parent_author = get_attr(parent_post, 'author', None)
            if parent_author:
                reply_to_handle = get_attr(parent_author, 'handle', '')
                # Also get the in_reply_to_id if not already set
                if not in_reply_to_id:
                    in_reply_to_id = get_attr(parent_post, 'uri', None)

    # Prepend reply-to mention to text if this is a reply (but not if replying to self)
    if reply_to_handle and text:
        # Get the post author's handle to check if replying to self
        post_author_handle = get_attr(post_author, 'handle', '') if post_author else ''
        # Only prepend if:
        # 1. Text doesn't already start with @reply_to_handle
        # 2. Not replying to self (same author)
        if not text.lower().startswith(f'@{reply_to_handle.lower()}'):
            if reply_to_handle.lower() != post_author_handle.lower():
                text = f'@{reply_to_handle} {text}'

    # Handle embed (media, quote posts, external links)
    embed = get_attr(post, 'embed', None)
    media_attachments = extract_media_from_embed(embed)

    # Extract card (external link embed)
    card = extract_card_from_embed(embed)

    # Handle quote posts
    quote = None
    if embed:
        embed_type = get_attr(embed, '$type', '') or get_attr(embed, 'py_type', '')
        if 'record' in str(embed_type).lower():
            # For recordWithMedia, the record is nested inside embed.record
            quoted_record = get_attr(embed, 'record', None)
            if quoted_record:
                # The author might be directly on the record, or nested in a 'record' field
                # for recordWithMedia views
                quoted_author = get_attr(quoted_record, 'author', None)
                # For app.bsky.embed.record#viewRecord the value field contains the actual record
                actual_record = get_attr(quoted_record, 'value', None) or quoted_record
                if quoted_author:
                    quote = bluesky_post_to_universal(quoted_record, quoted_author)
                elif actual_record != quoted_record:
                    # Try to get author from nested structure
                    nested_author = get_attr(actual_record, 'author', None)
                    if nested_author:
                        quote = bluesky_post_to_universal(actual_record, nested_author)

    # Get mentions and links from facets in record
    mentions = []
    facet_links = []
    if record:
        facets = get_attr(record, 'facets', [])
        mentions = extract_mentions_from_facets(facets)
        facet_links = extract_links_from_facets(facets)

    # Get web URL
    handle = get_attr(post_author, 'handle', '') if post_author else ''
    web_url = get_web_url(handle, rkey) if handle and rkey else None

    # Get labels (for content warnings)
    labels = get_attr(post, 'labels', []) or []

    # Check for self-labels in record
    if record:
        self_labels = get_attr(record, 'labels', None)
        if self_labels:
            label_values = get_attr(self_labels, 'values', [])
            for lv in label_values:
                val = get_attr(lv, 'val', '')
                if val:
                    labels.append({'val': val})

    status = UniversalStatus(
        id=uri,  # Use full URI as ID for API operations
        account=universal_author,
        content=text,  # Bluesky uses plain text
        text=text,
        created_at=created_at,
        favourites_count=like_count or 0,
        boosts_count=repost_count or 0,
        replies_count=reply_count or 0,
        in_reply_to_id=in_reply_to_id,
        reblog=None,  # Only set for reposts, handled above
        quote=quote,
        media_attachments=media_attachments,
        mentions=mentions,
        url=web_url,
        visibility=None,  # Bluesky doesn't have visibility
        spoiler_text=None,  # Bluesky uses labels instead
        card=card,  # External link embed
        poll=None,  # Bluesky doesn't have polls
        pinned=False,  # Bluesky handles pinned differently
        _platform_data=platform_data or post,
        _platform='bluesky',
    )

    # Store facet links for URL extraction
    if facet_links:
        status._facet_links = facet_links

    return status


def bluesky_notification_to_universal(notification) -> Optional[UniversalNotification]:
    """Convert a Bluesky notification to UniversalNotification."""
    if notification is None:
        return None

    # Map Bluesky notification reasons to our types
    reason_map = {
        'like': 'favourite',
        'repost': 'reblog',
        'follow': 'follow',
        'mention': 'mention',
        'reply': 'mention',  # Treat replies as mentions
        'quote': 'mention',  # Treat quotes as mentions
    }

    reason = get_attr(notification, 'reason', 'unknown')
    notif_type = reason_map.get(reason, reason)

    # Get the actor (who triggered the notification)
    author = get_attr(notification, 'author', None)
    universal_author = bluesky_profile_to_universal(author)

    # Get indexed_at as created_at
    indexed_at = get_attr(notification, 'indexed_at', '') or get_attr(notification, 'indexedAt', '')
    if indexed_at:
        try:
            indexed_at = indexed_at.replace('Z', '+00:00')
            created_at = datetime.fromisoformat(indexed_at.replace('+00:00', ''))
        except:
            created_at = datetime.now()
    else:
        created_at = datetime.now()

    # Get associated status if any
    status = None
    record = get_attr(notification, 'record', None)
    if record and reason in ('mention', 'reply', 'quote'):
        # For these types, the record IS the post
        status = bluesky_post_to_universal(notification, author)

    uri = get_attr(notification, 'uri', '')

    return UniversalNotification(
        id=uri,
        type=notif_type,
        account=universal_author,
        created_at=created_at,
        status=status,
        _platform_data=notification,
        _platform='bluesky',
    )
